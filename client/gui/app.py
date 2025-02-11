import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import requests
import sys
import os
import logging
import configparser
import urllib3
import socket
import ssl
import time
import hashlib
from urllib.parse import urlparse
from dotenv import load_dotenv

from . import styles
from . import utils
from .pages import login, signup, main_interface, upload, home, profile, settings, inspection, team, drone_specs

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

########################################################################
# HELPER METHODS for TOFU, SSL, etc.
########################################################################

def create_ssl_context(
    verify_mode=ssl.CERT_NONE,
    client_cert_path=None,  # For mutual TLS (optional)
    client_key_path=None,
):
    """
    Create an SSLContext with strong TLS settings.
    If you want the client to present its own certificate (mutual TLS),
    set client_cert_path and client_key_path here, and verify_mode=ssl.CERT_REQUIRED.
    We'll do pinned-fingerprint ourselves, so we typically skip normal CA checks.
    """
    # Modern approach: PROTOCOL_TLS_CLIENT (Python 3.7+)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False  # We'll do a fingerprint check manually
    context.verify_mode = verify_mode

    # Force minimum TLS 1.2 (optional)
    context.minimum_version = ssl.TLSVersion.TLSv1_2

    # Restrict ciphers to ephemeral ECDHE + AES-GCM only (optional)
    context.set_ciphers("ECDHE+AESGCM:!aNULL:!eNULL")

    # If doing mutual TLS, load client certificate + key
    if client_cert_path and client_key_path:
        context.load_cert_chain(certfile=client_cert_path, keyfile=client_key_path)

    return context

def get_server_certificate_fingerprint(host, port, timeout=5):
    """
    Retrieve server’s certificate, compute SHA256 fingerprint, return hex digest.
    Raises ConnectionRefusedError if server is unavailable.
    """
    ssl_context = create_ssl_context()
    with socket.create_connection((host, port), timeout=timeout) as sock:
        with ssl_context.wrap_socket(sock, server_hostname=host) as ssock:
            der_cert = ssock.getpeercert(True)
            return hashlib.sha256(der_cert).hexdigest()

def load_pinned_fingerprint(path):
    """Load pinned fingerprint from file, or None if missing."""
    if os.path.exists(path):
        with open(path, 'r') as f:
            return f.read().strip()
    return None

def save_pinned_fingerprint(path, fingerprint):
    """Save the server fingerprint for future TOFU checks."""
    with open(path, 'w') as f:
        f.write(fingerprint)

def verify_or_set_fingerprint(host, port, pinned_fpr_file):
    """
    TOFU logic:
      - if pinned fingerprint doesn't exist, trust and save current server cert
      - if pinned fingerprint changes, warn user
    """
    actual_fpr = get_server_certificate_fingerprint(host, port)
    pinned_fpr = load_pinned_fingerprint(pinned_fpr_file)

    if pinned_fpr is None:
        print("No pinned fingerprint found. Trusting current server cert (TOFU).")
        save_pinned_fingerprint(pinned_fpr_file, actual_fpr)
    else:
        if pinned_fpr != actual_fpr:
            print("WARNING: Server certificate fingerprint has CHANGED!")
            print(f"Old pinned: {pinned_fpr}")
            print(f"New actual: {actual_fpr}")
            print("Possible MITM attack. Proceed with caution.")

def wait_for_server_with_tofu(server_url, pinned_fpr_file, max_retries=50, delay=3):
    """
    Repeatedly attempt to verify pinned-fingerprint, then GET /ping.
    Returns True if the server is eventually up, False otherwise.
    """
    parsed = urlparse(server_url)
    host = parsed.hostname
    port = parsed.port if parsed.port else 443

    for attempt in range(1, max_retries + 1):
        print(f"[Attempt {attempt}/{max_retries}] Checking server availability...")

        # 1) Attempt pinned-fingerprint check
        try:
            verify_or_set_fingerprint(host, port, pinned_fpr_file)
        except (ConnectionRefusedError, socket.timeout):
            print("Server connection refused or timed out. Retrying...")
            time.sleep(delay)
            continue
        except Exception as e:
            print(f"Error verifying server cert: {e}. Retrying...")
            time.sleep(delay)
            continue

        # 2) Attempt GET /ping
        try:
            # We skip normal CA validation, so 'verify=False'
            resp = requests.get(f"{server_url}/ping", verify=False, timeout=4)
            if resp.status_code == 200:
                print("Server responded OK to /ping!")
                return True
            else:
                print(f"/ping returned status {resp.status_code}. Retrying...")
        except requests.RequestException as e:
            print(f"Error on /ping: {e}")

        time.sleep(delay)

    return False

########################################################################
# MAIN SKYSYNCAPP CLASS
########################################################################

class SkySyncApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SkySync - Autonomous Drone System")
        self.root.geometry("1440x900")

        self.platform = sys.platform  

        # 1) Load environment variables from .env
        self.ENV_PATH = os.path.join(os.path.dirname(__file__), '..', 'conf', '.env')
        load_dotenv(self.ENV_PATH)

        # 2) Access environment variables
        self.CLIENT_PATH = os.getenv('CLIENT_PATH')
        self.LOG_PATH    = os.getenv('LOG_PATH')
        self.SERVER_URL  = os.getenv('SERVER_URL')
        # self.CERT_PATH   = os.getenv('CERT_PATH', '')  
        # self.CLIENT_CERT_PATH = os.getenv('CLIENT_CERT_PATH')  
        # self.CLIENT_KEY_PATH  = os.getenv('CLIENT_KEY_PATH')   
        self.BG_IMG      = os.getenv('BG_IMG')

        # TODO:
        # Update session path using update_client_conf in .env

        # 3) Logging
        logging.basicConfig(
            filename=self.LOG_PATH,
            level=logging.INFO,
            format='%(asctime)s:%(levelname)s:%(message)s'
        )

        # 4) Prepare pinned-fingerprint logic
        pinned_fpr_file = os.path.join(self.CLIENT_PATH, 'conf', 'pinned_fingerprint.txt')
        # Wait for server up with TOFU check; if server fails to come up, we can exit:
        if not wait_for_server_with_tofu(self.SERVER_URL, pinned_fpr_file, max_retries=50, delay=3):
            print("Server not found after repeated attempts. Exiting client.")
            sys.exit(1)

        # 5) Initialize your styles
        styles.setup_styles(self)

        # 6) Load session config
        self.session = configparser.ConfigParser()
        self.session.read(os.path.join(self.CLIENT_PATH, 'conf', 'session.ini'))

        # 7) App state
        self.is_logged_in = False
        self.username     = None
        self.token        = None
        self.selected_files = []

        self.cache_dir = os.path.join(self.CLIENT_PATH, 'cached_images')
        os.makedirs(self.cache_dir, exist_ok=True)

        # 8) Create the main UI frame
        self.main_frame = utils.create_frame(self, self.root)

        # 9) Show login screen initially
        self.show_login_screen()

    ########################################################################
    # Screen management methods
    ########################################################################
    def show_login_screen(self):
        login.show_login_screen(self)

    def show_signup_screen(self):
        signup.show_signup_screen(self)

    def show_main_interface(self):
        main_interface.show_main_interface(self)

    def show_upload_page(self):
        upload.show_upload_page(self)

    def show_drone_specs(self):
        drone_specs.show_drone_specs(self)

    def show_home_page(self):
        home.show_home_page(self)

    def show_profile_page(self):
        profile.show_profile_page(self)

    def show_settings_page(self):
        settings.show_settings_page(self)

    def show_inspection_page(self):
        inspection.show_inspection_page(self)

    def show_team_page(self):
        team.show_team_page(self)

    ########################################################################
    # Session management
    ########################################################################
    def load_session(self):
        """Load session information if available."""
        if self.session.has_section('Session'):
            self.username = self.session.get('Session', 'username')
            self.token = self.session.get('Session', 'token')
            self.is_logged_in = True
            return True
        return False

    def save_session(self):
        """Save session information."""
        self.session['Session'] = {'username': self.username, 'token': self.token}
        with open(os.path.join(self.CLIENT_PATH, 'conf', 'session.ini'), 'w') as configfile:
            self.session.write(configfile)

    def remove_session(self):
        """Remove session information."""
        if self.session.has_section('Session'):
            self.session.remove_section('Session')
            with open(os.path.join(self.CLIENT_PATH, 'conf', 'session.ini'), 'w') as configfile:
                self.session.write(configfile)
            self.is_logged_in = False
            self.token = None
