import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import requests
import sys
import os
import logging
import configparser
import urllib3
from dotenv import load_dotenv

from . import styles
from . import utils
from .pages import login, signup, main_interface, upload, home, profile, settings, inspection, team, drone_specs

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SkySyncApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SkySync - Autonomous Drone System")
        self.root.geometry("1440x900")

        self.platform = sys.platform  

        # Specify the path to the .env file
        self.ENV_PATH = os.path.join(os.path.dirname(__file__), '..', 'conf', '.env')
        # Load environment variables
        load_dotenv(self.ENV_PATH)

        # Access environment variables
        self.CLIENT_PATH = os.getenv('CLIENT_PATH')
        self.LOG_PATH = os.getenv('LOG_PATH')
        self.SERVER_URL = os.getenv('SERVER_URL')
        self.CERT_PATH = os.getenv('CERT_PATH')
        self.BG_IMG = os.getenv('BG_IMG')

        # TODO:
        # Update session path using update_client_conf in .env

        # Load configuration
        self.session = configparser.ConfigParser()
        self.session.read(os.path.join(self.CLIENT_PATH, 'conf', 'session.ini'))

        # Configure logging
        logging.basicConfig(
            filename=self.LOG_PATH,
            level=logging.INFO,
            format='%(asctime)s:%(levelname)s:%(message)s'
        )

        # Initialize styles
        styles.setup_styles(self)

        # App state
        self.is_logged_in = False
        self.username = None
        self.token = None
        self.selected_files = []
        self.cache_dir = os.path.join(self.CLIENT_PATH, 'cached_images')
        os.makedirs(self.cache_dir, exist_ok=True)

        # Create main UI frames
        self.main_frame = utils.create_frame(self, self.root)

        # Show login screen initially
        self.show_login_screen()

    # Screen management methods
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

    # Session management
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
