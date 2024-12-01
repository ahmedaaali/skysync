import os
import signal
import subprocess
import sys
import time
from urllib.parse import urlparse
from flask import Flask
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from auth import auth_blueprint
from photos import photos_blueprint
from analysis import analysis_blueprint
from database import init_db

import warnings

# Suppress Flask-Limiter UserWarning for in-memory storage
warnings.filterwarnings("ignore", category=UserWarning)

class ServerManager:
    def __init__(self):
        """Initialize server manager and load configurations."""
        self.ENV_PATH = os.path.join(os.path.dirname(__file__), 'conf', '.env')
        self._load_and_validate_env()

        self.UPLOADED_IMAGES_PATH = os.path.join(self.SERVER_PATH, "uploaded_images")
        self.PROCESSED_IMAGES_PATH = os.path.join(self.SERVER_PATH, "processed_images")

        # Extract host and port from SERVER_URL
        parsed_url = urlparse(self.SERVER_URL)
        self.SERVER_HOST = parsed_url.hostname
        self.SERVER_PORT = parsed_url.port

        # Gunicorn and Celery commands
        self.GUNICORN_CMD = [
            "env",
            f"PYTHONPATH={self.SERVER_PATH}",
            "gunicorn", "server:app",
            "--bind", f"{self.SERVER_HOST}:{self.SERVER_PORT}",
            "--certfile", self.CERT_PATH,
            "--keyfile", self.KEY_PATH,
            "--workers", "4",
            "--timeout", "60",
            "--log-level", "critical"  
        ]
        self.CELERY_CMD = [
            "env",
            f"PYTHONPATH={self.SERVER_PATH}",
            "celery", "-A", "analysis.celery", "worker",
            "--loglevel=error", "--autoscale=10,3"
        ]

        # Processes list for monitoring
        self.processes = []

        # Set up logging
        logging.basicConfig(
            filename=self.LOG_PATH,
            level=logging.INFO,
            format='%(asctime)s:%(levelname)s:%(message)s'
        )
        # Suppress unwanted logs
        logging.getLogger("gunicorn.error").setLevel(logging.CRITICAL)
        logging.getLogger("celery").setLevel(logging.ERROR)

        # Initialize the shutdown logger
        shutdown_log_path = os.path.join(self.SERVER_PATH, "shutdown.log")
        self.shutdown_logger = logging.getLogger("shutdown")
        shutdown_handler = logging.FileHandler(shutdown_log_path)  
        shutdown_handler.setLevel(logging.INFO)
        shutdown_formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        shutdown_handler.setFormatter(shutdown_formatter)
        self.shutdown_logger.addHandler(shutdown_handler)
        self.shutdown_logger.propagate = False

    def handle_signal(self, signum, frame):
        """Handle OS signals for graceful shutdown."""
        self.shutdown_logger.info(f"Signal {signum} received. Stopping all processes.")
        self.stop_processes()
        sys.exit(0)

    def _load_and_validate_env(self):
        """Load and validate required environment variables."""
        if not os.path.exists(self.ENV_PATH):
            raise FileNotFoundError(f".env file not found at {self.ENV_PATH}")
        load_dotenv(self.ENV_PATH, override=True)

        # Load required variables
        self.SERVER_PATH = os.getenv('SERVER_PATH')
        self.LOG_PATH = os.getenv('LOG_PATH', 'server.log')
        self.SERVER_URL = os.getenv('SERVER_URL', 'https://localhost:5000')
        self.CERT_PATH = os.getenv('CERT_PATH')
        self.KEY_PATH = os.getenv('KEY_PATH')
        self.SECRET_KEY = os.getenv('SECRET_KEY')
        self.DATABASE_URL = os.getenv('DATABASE_URL')

        logging.info(f"SERVER_PATH: {self.SERVER_PATH}")
        logging.info(f"DATABASE_URL: {self.DATABASE_URL}")
        # Validate required variables
        if not all([self.SECRET_KEY, self.DATABASE_URL, self.CERT_PATH, self.KEY_PATH]):
            raise ValueError("One or more required environment variables are missing.")

    def get_database_session(self):
        """Provide a new database session."""
        engine = create_engine(self.DATABASE_URL)
        return sessionmaker(bind=engine)

    def create_app(self):
        """Create and configure the Flask application."""
        app = Flask(__name__)
        app.config['SECRET_KEY'] = self.SECRET_KEY
        app.config['SQLALCHEMY_DATABASE_URI'] = self.DATABASE_URL

        # Initialize rate limiting
        limiter = Limiter(
            key_func=get_remote_address,
            default_limits=["900 per day", "500 per hour"],
            storage_uri="redis://localhost:6379"
        )
        limiter.init_app(app)

        init_db()

        return app

    def start_processes(self, run_gui=False):
        """Start Gunicorn, Celery, and optionally the Server GUI as subprocesses."""
        try:
            env = os.environ.copy()
            env['SERVER_PATH'] = self.SERVER_PATH

            print("Starting Gunicorn...")
            gunicorn_proc = subprocess.Popen(
                self.GUNICORN_CMD,
                env=env,
                stdout=sys.stdout,
                stderr=sys.stderr,
                preexec_fn=os.setsid
            )
            self.processes.append(("Gunicorn", gunicorn_proc))

            print("Starting Celery...")
            celery_proc = subprocess.Popen(
                self.CELERY_CMD,
                env=env,
                stdout=sys.stdout,
                stderr=sys.stderr,
                preexec_fn=os.setsid
            )
            self.processes.append(("Celery", celery_proc))

            if run_gui:
                print("Starting Server GUI...")
                gui_proc = subprocess.Popen(
                    ["python", os.path.join(self.SERVER_PATH, "server_gui.py")],
                    env=env,
                    stdout=sys.stdout,
                    stderr=sys.stderr,
                    preexec_fn=os.setsid
                )
                self.processes.append(("Server GUI", gui_proc))
            else:
                print("Server GUI will not be started.")
        except Exception as e:
            self.shutdown_logger.error(f"Error starting processes: {e}")
            self.stop_processes()
            sys.exit(1)

    def stop_processes(self, exclude_gui=False):
        """Terminate all running subprocesses, optionally excluding the GUI."""
        for name, proc in self.processes[:]:
            if exclude_gui and name == "Server GUI":
                continue
            if proc.poll() is None:  
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                    self.shutdown_logger.info(f"Terminated process '{name}' with PID {proc.pid}")
                except Exception as e:
                    self.shutdown_logger.error(f"Error stopping process '{name}' with PID {proc.pid}: {e}")
                self.processes.remove((name, proc))

    def monitor_processes(self):
        """Monitor subprocesses and terminate all if one fails."""
        try:
            while True:
                for name, proc in self.processes[:]:
                    if proc.poll() is not None:  
                        if name == "Server GUI":
                            # If GUI ends, stop other processes gracefully
                            print("Server GUI process has ended. Stopping all processes.")
                            self.stop_processes(exclude_gui=True)
                            sys.exit(0)
                        else:
                            # Handle unexpected process termination
                            print(f"Process '{name}' has stopped unexpectedly.")
                            self.stop_processes()
                            sys.exit(1)
                time.sleep(1)
        except KeyboardInterrupt:
            print("Keyboard interrupt received. Stopping all processes.")
            self.stop_processes()

    def restart_process(self, name):
        """Restart a subprocess by name."""
        self.shutdown_logger.info(f"Attempting to restart process '{name}'")
        if name == "Gunicorn":
            cmd = self.GUNICORN_CMD
        elif name == "Celery":
            cmd = self.CELERY_CMD
        elif name == "Server GUI":
            cmd = ["python", "server_gui.py"]
        else:
            self.shutdown_logger.error(f"Unknown process name: {name}")
            return

        env = os.environ.copy()
        env['SERVER_PATH'] = self.SERVER_PATH

        try:
            proc = subprocess.Popen(
                cmd,
                env=env,
                stdout=sys.stdout,
                stderr=sys.stderr,
                preexec_fn=os.setsid
            )
            self.processes.append((name, proc))
            self.shutdown_logger.info(f"Successfully restarted process '{name}' with PID {proc.pid}")
        except Exception as e:
            self.shutdown_logger.error(f"Failed to restart process '{name}': {e}")

    def run(self):
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)

        self.start_processes()
        self.monitor_processes()
