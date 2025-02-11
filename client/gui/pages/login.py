import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import requests
import logging

from .. import utils

def show_login_screen(app):
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

    # Application title above login
    utils.create_label(app, center_frame, "SkySync - Autonomous Drone System", font=app.header_font, text_color=app.light_accent, pady=(30, 10))

    # Decorative separator line
    utils.create_label(app, center_frame, "—" * 50, font=app.body_font, text_color=app.accent_color, pady=10)

    # Login Header
    utils.create_label(app, center_frame, "Sign in", font=("Helvetica Neue", 30, "bold"), text_color=app.light_accent, pady=(60, 5))

    # Username and Password Frame
    input_frame = ctk.CTkFrame(center_frame, fg_color=app.bg_color)
    input_frame.pack(pady=20)

    # Username Label and Entry
    username_label = ctk.CTkLabel(input_frame, text="Username:", font=app.body_font, text_color=app.light_accent)
    username_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
    app.username_entry = utils.create_entry(app, input_frame, placeholder="Enter your username")
    app.username_entry.grid(row=0, column=1, padx=10, pady=10)

    # Password Label and Entry
    password_label = ctk.CTkLabel(input_frame, text="Password:", font=app.body_font, text_color=app.light_accent)
    password_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
    app.password_entry = utils.create_entry(app, input_frame, placeholder="Enter your password", show="*")
    app.password_entry.grid(row=1, column=1, padx=10, pady=10)

    # Login Button
    utils.create_button(app, 
        center_frame,
        "Login",
        lambda: verify_login(app),
        fg_color="#3498db",
        hover_color="#2980b9",
        font=("Helvetica Neue", 22, "bold"),
        width=250,
        height=50,
        border_width=2,
        border_color="#2980b9",
        corner_radius=12,
        pady=30
    )

    # Error message placeholder (hidden by default)
    app.error_message = utils.create_label(app, center_frame, "", font=("Helvetica Neue", 12, "italic"), text_color="red", pady=(0, 10))

    utils.create_label(app, center_frame, "Don't have an account? Sign up below!", text_color=app.text_color)
    utils.create_button(app, center_frame, "Sign Up", app.show_signup_screen, fg_color=app.success_color, width=150, pady=5)

    # Bind Enter key to login
    app.root.bind("<Return>", lambda event: verify_login_with_enter(app, event))

def verify_login_with_enter(app, event=None):
    """Trigger login verification when the Enter key is pressed."""
    verify_login(app)

def verify_login(app):
    """Verify user credentials."""
    if app.username_entry.winfo_exists():
        username = app.username_entry.get().strip()
    else:
        logging.warning("Username entry widget does not exist.")
        return
    if app.password_entry.winfo_exists():
        password = app.password_entry.get().strip()
    else:
        logging.warning("Password entry widget does not exist.")
        return

    # Process login
    process_login(app, username, password)

def process_login(app, username, password):
    """Process login request."""
    try:
        response = requests.post(
            f'{app.SERVER_URL}/login',
            json={'username': username, 'password': password},
            # verify=app.CERT_PATH,
            verify=False,
            timeout=10
        )
    except requests.exceptions.RequestException as e:
        utils.show_error_message_box(app, f"Server connection issue: {e}")
        app.root.focus_force()
        return

    if response.status_code == 200:
        app.is_logged_in = True
        app.username = username
        app.token = response.json().get('token')
        app.save_session()
        app.show_main_interface()
    elif response.status_code == 401:
        utils.show_error_message(app, "Invalid credentials.")
        app.root.focus_force()
    else:
        utils.show_error_message(app, f"Unexpected error: {response.status_code}")
        app.root.focus_force()
