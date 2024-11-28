import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import requests
import os
import logging

class AdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SkySync - Admin Panel")
        self.root.geometry("1440x900")

        # Access environment variables
        self.SERVER_URL = os.environ.get('SERVER_URL')
        self.CERT_PATH = os.environ.get('CERT_PATH')
        self.LOG_PATH = os.environ.get('LOG_PATH', 'server_gui.log')

        # Set up logging
        logging.basicConfig(
            filename=self.LOG_PATH,
            level=logging.INFO,
            format='%(asctime)s:%(levelname)s:%(message)s'
        )

        self.token = None  # Admin authentication token

        self.setup_styles()
        self.main_frame = self.create_frame(self.root)
        self.show_login_screen()

    def setup_styles(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.bg_color = "#1c1c1c"
        self.text_color = "#f5f5f5"
        self.header_font = ("Helvetica Neue", 30, "bold")
        self.body_font = ("Helvetica Neue", 16)

    def create_frame(self, parent, **kwargs):
        frame = ctk.CTkFrame(parent, fg_color=self.bg_color)
        frame.pack(fill=kwargs.get('fill', ctk.BOTH), expand=kwargs.get('expand', True))
        return frame

    def show_login_screen(self):
        self.clear_frame()

        center_frame = self.create_frame(self.main_frame)

        self.create_label(center_frame, "Admin Login", font=self.header_font, pady=20).pack()

        input_frame = self.create_frame(center_frame)

        self.create_label(input_frame, "Username:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.username_entry = self.create_entry(input_frame, placeholder="Enter admin username")
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        self.create_label(input_frame, "Password:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.password_entry = self.create_entry(input_frame, placeholder="Enter admin password", show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        self.create_button(center_frame, "Login", self.verify_login, width=150)

if __name__ == "__main__":
    root = ctk.CTk()
    app = AdminApp(root)

# TODO:
# Create admin gui for server side management and easy database access
