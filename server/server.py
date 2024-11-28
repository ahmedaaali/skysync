import os
import sys
import signal
import argparse

# Import the ServerManager and define the `app` at the module level
from server_manager import ServerManager
from missions import missions_blueprint
from photos import photos_blueprint
from analysis import analysis_blueprint
from auth import auth_blueprint

# Ensure the current directory is in the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create the server manager instance
server_manager = ServerManager()

# Define the app for Gunicorn
app = server_manager.create_app()

# Register blueprints
app.register_blueprint(photos_blueprint)
app.register_blueprint(analysis_blueprint)
app.register_blueprint(auth_blueprint)
app.register_blueprint(missions_blueprint)

if __name__ == "__main__":
    # Parse arguments for configuration and runtime options
    parser = argparse.ArgumentParser(
        description="Run the SkySync server with various configuration and runtime options."
    )
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Enable verbose output for configuration updates."
    )
    parser.add_argument(
        "-r", "--regenerate-cert", 
        action="store_true", 
        help="Force regeneration of SSL certificates."
    )
    parser.add_argument(
        "-g", "--run-gui", 
        action="store_true", 
        help="Start the Server GUI."
    )
    args = parser.parse_args()

    # Display help message if requested (automatically handled by argparse)

    # Update configuration based on arguments
    from conf.update_server_conf import update_configuration
    update_configuration(verbose=args.verbose, regenerate_cert=args.regenerate_cert)

    # Set up signal handlers for clean shutdown
    signal.signal(signal.SIGINT, server_manager.handle_signal)
    signal.signal(signal.SIGTERM, server_manager.handle_signal)

    # Start and monitor server processes
    server_manager.start_processes(run_gui=args.run_gui)
    server_manager.monitor_processes()