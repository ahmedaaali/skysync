import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from PIL import Image, ImageTk
import requests
import logging
import re

from .. import utils

def is_password_strong(password):
    """Check if the password meets the strength requirements."""
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not any(char.isupper() for char in password):
        return "Password must contain at least one uppercase letter."
    if not any(char.islower() for char in password):
        return "Password must contain at least one lowercase letter."
    if not any(char.isdigit() for char in password):
        return "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special character (!@#$%^&*(), etc.)."
    return None

def show_signup_screen(app):
    """Displays the signup screen."""
    utils.clear_frame(app)

    # Load the background image
    image = Image.open(app.BG_IMG)
    image = image.resize((1440, 900), Image.LANCZOS)
    background_photo = ImageTk.PhotoImage(image)

    # Create a Canvas for the background image
    canvas = tk.Canvas(app.main_frame, width=1440, height=900, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=background_photo, anchor="nw")
    app.bg_image_ref = background_photo

    # Center frame to hold all widgets
    center_frame = ctk.CTkFrame(app.main_frame, fg_color=app.bg_color)
    center_frame.place(relx=0.5, rely=0.5, anchor='center')

    utils.create_label(
        app,
        center_frame,
        "SkySync Sign Up",
        font=("Helvetica Neue", 30, "bold"),
        text_color=app.light_accent,
        pady=(30, 10)
    )

    input_frame = ctk.CTkFrame(center_frame, fg_color=app.bg_color)
    input_frame.pack(pady=20, padx=20)

    # Username Label and Entry
    username_label = ctk.CTkLabel(
        input_frame, text="Username:", font=app.body_font, text_color=app.light_accent
    )
    username_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
    app.signup_username_entry = utils.create_entry(
        app, input_frame, placeholder="Choose a Username", width=300
    )
    app.signup_username_entry.grid(row=0, column=1, padx=10, pady=10)

    # Password Label and Entry
    password_label = ctk.CTkLabel(
        input_frame, text="Password:", font=app.body_font, text_color=app.light_accent
    )
    password_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
    app.signup_password_entry = utils.create_entry(
        app, input_frame, placeholder="Choose a Password", show="*", width=300
    )
    app.signup_password_entry.grid(row=1, column=1, padx=10, pady=10)

    # Confirm Password Label and Entry
    confirm_password_label = ctk.CTkLabel(
        input_frame,
        text="Confirm Password:",
        font=app.body_font,
        text_color=app.light_accent,
    )
    confirm_password_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
    app.confirm_password_entry = utils.create_entry(
        app, input_frame, placeholder="Confirm Password", show="*", width=300
    )
    app.confirm_password_entry.grid(row=2, column=1, padx=10, pady=10)

    utils.create_button(
        app,
        center_frame,
        "Register",
        lambda: submit_signup(app),
        fg_color=app.success_color,
        width=150,
        pady=20,
    )
    utils.create_button(
        app,
        center_frame,
        "Back to Login",
        app.show_login_screen,
        fg_color=app.accent_color,
        width=150,
        pady=5,
    )

    # Bind Enter key to submit the signup form
    app.root.bind("<Return>", lambda event: submit_signup(app))

def submit_signup(app):
    """Handles the signup form submission."""
    username = app.signup_username_entry.get()
    password = app.signup_password_entry.get()
    confirm_password = app.confirm_password_entry.get()

    # Validate username length
    username_error = is_username_valid(username)
    if username_error:
        messagebox.showerror("Error", username_error)
        app.root.focus_force()
        return

    # Validate password strength
    password_error = is_password_strong(password)
    if password_error:
        messagebox.showerror("Error", password_error)
        app.root.focus_force()
        return

    # Check if passwords match
    if password != confirm_password:
        messagebox.showerror("Error", "Passwords do not match.")
        app.root.focus_force()
        return

    try:
        # Send signup request to the server
        response = requests.post(
            f'{app.SERVER_URL}/register',
            json={'username': username, 'password': password},
            # verify=app.CERT_PATH
            verify=False
        )
        if response.status_code == 201:
            # Success: Account created
            messagebox.showinfo("Success", "Account created successfully! Please log in.")
            app.root.focus_force()
            app.show_login_screen()
        elif response.status_code == 409:
            # Conflict: Username already exists
            messagebox.showerror("Error", "Username already exists.")
            app.root.focus_force()
        else:
            # Other errors
            messagebox.showerror("Error", "Registration failed.")
            app.root.focus_force()
    except requests.exceptions.RequestException as e:
        # Handle server connection issues
        logging.error(f"Error in submit_signup: {e}")
        messagebox.showerror("Error", "Server connection issue.")
        app.root.focus_force()

def is_username_valid(username):
    """Check if the username meets the minimum length requirement."""
    if len(username) < 5:
        return "Username must be at least 5 characters long."
    return None
