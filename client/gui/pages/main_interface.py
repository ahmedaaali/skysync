import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk

from .. import utils

def show_main_interface(app):
    utils.clear_frame(app)

    # Load and resize the background image
    image = Image.open(app.BG_IMG)
    image = image.resize((1240, 900), Image.LANCZOS)
    background_photo = ImageTk.PhotoImage(image)

    # Replace display_frame with a Canvas
    app.display_frame = tk.Canvas(app.main_frame, width=1240, height=900, highlightthickness=0)
    app.display_frame.pack(side=ctk.RIGHT, expand=True, fill=ctk.BOTH, padx=10, pady=10)

    # Set the background image
    app.display_frame.create_image(0, 0, image=background_photo, anchor="nw")
    app.background_photo = background_photo

    # # FIXME:
    # # Header Frame with Title and Dropdown Menu for mission across pages
    # app.header_frame = ctk.CTkFrame(app.main_frame, fg_color=app.accent_color)
    # app.header_frame.pack(fill=ctk.X)
    #
    # # Title
    # utils.create_label(app, app.header_frame, "SkySync", font=app.header_font, text_color=app.text_color, pady=5)
    #
    # # Dropdown Menu for Profile, Settings, and Logout
    # app.options_var = ctk.StringVar()
    # app.options_menu = ctk.CTkOptionMenu(
    #     app.header_frame,
    #     variable=app.options_var,
    #     values=[],
    #     command=lambda option: handle_menu_option(app, option),
    #     fg_color="#3498db")
    # app.options_menu.pack(pady=5, anchor="e")

    # Navigation Sidebar
    app.sidebar_frame = ctk.CTkFrame(app.main_frame, width=200, fg_color=app.light_accent)
    app.sidebar_frame.pack(side=ctk.LEFT, fill=ctk.Y, padx=10)
    app.sidebar_frame.pack_propagate(False)

    # Sidebar Buttons
    create_sidebar_buttons(app)

    # Load Home Page by default
    app.show_home_page()

def create_sidebar_buttons(app):
    button_config = {"width": 180, "font": app.subheader_font, "fg_color": app.bg_color, "hover_color": app.accent_color}

    buttons = [
        ("Home", app.show_home_page),
        ("Profile", app.show_profile_page),
        ("Settings", app.show_settings_page),
        ("Drone Inspection", app.show_inspection_page),
        ("Upload Images", app.show_upload_page),
        ("Drone Specs", app.show_drone_specs),
        ("Meet the Team", app.show_team_page),
        ("Logout", lambda: handle_logout(app))
    ]

    for idx, (text, command) in enumerate(buttons):
        pady = (20, 10) if idx == 0 else 10
        button = ctk.CTkButton(app.sidebar_frame, text=text, command=command, **button_config)
        button.pack(pady=pady, fill='x')

def handle_logout(app):
    """Handles the logout process."""
    app.remove_session()
    app.is_logged_in = False
    app.token = None
    app.show_login_screen()

# #FIXME:
# def handle_menu_option(app, selected_option):
#     if selected_option == "Logout":
#         app.remove_session()
#         app.is_logged_in = False
#         app.token = None
#         app.show_login_screen()
#     elif selected_option == "Profile":
#         app.show_profile_page()
#     elif selected_option == "Settings":
#         app.show_settings_page()
