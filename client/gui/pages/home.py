import requests  
import customtkinter as ctk

from .. import utils

def show_home_page(app):
    """
    Displays the home page with mission creation functionality.
    """
    utils.clear_display_frame(app)  # Clear the display frame

    # Add a title label
    utils.create_label(app, app.display_frame, "Welcome to SkySync", font=("Helvetica Neue", 30, "bold"))

    # Add description text
    desc_text = (
        "SkySync project aims to enhance safety, accuracy, and efficiency of bridge inspections. "
        "It integrates sensors, cameras, and machine learning to find structural defects. "
        "The key objective of this project includes developing a drone capable of autonomously navigating complex structures "
        "and using machine learning to detect cracks, corrosion, and other defects."
    )
    utils.create_label(
        app,
        app.display_frame,
        desc_text,
        font=app.body_font,
        text_color=app.text_color,
        wraplength=800,
        justify="left",
        pady=20,  # Add spacing between elements
    )

    # Add a label for the mission creation section
    utils.create_label(app, app.display_frame, "Create a New Mission", font=("Helvetica Neue", 20, "bold"), pady=10)

    # Add an entry for the mission name
    app.mission_name_entry = utils.create_entry(app, app.display_frame, placeholder="Enter mission name", width=300)
    app.mission_name_entry.pack(pady=10)

    # Add a button to create the mission
    utils.create_button(
        app,
        app.display_frame,
        "Create Mission",
        command=lambda: create_mission(app),
        pady=10,
    ).pack(pady=10)

    # Add a message label for success/error messages
    if not hasattr(app, 'home_message_label') or not app.home_message_label.winfo_exists():
        app.home_message_label = ctk.CTkLabel(
            app.display_frame,
            text="",
            font=app.body_font,
            text_color="green",
            anchor="center",
            wraplength=600,
        )
        app.home_message_label.pack(pady=10)

    # Bind the Enter key to trigger mission creation
    app.root.bind("<Return>", lambda event: create_mission(app))

def create_mission(app):
    """
    Sends a POST request to the server to create a new mission.
    """
    try:
        # Get mission name from the entry field
        mission_name = app.mission_name_entry.get().strip()
        if not mission_name:
            show_home_error_message(app, "Mission name cannot be empty.")
            return

        # API request details
        url = f"{app.SERVER_URL}/missions/create_mission"
        headers = {
            'x-access-token': app.token,
            'Content-Type': 'application/json'
        }
        data = {'mission_name': mission_name}

        # Make the POST request
        response = requests.post(url, json=data, headers=headers, verify=app.CERT_PATH)

        if response.status_code == 200:
            # Mission creation succeeded
            show_home_info_message(app, "Mission created successfully.")
            app.mission_name_entry.delete(0, 'end')  
        else:
            # Handle server errors
            try:
                error_message = response.json().get('error', 'Failed to create mission.')
            except ValueError:
                error_message = response.text or "Unknown error occurred."
            show_home_error_message(app, f"Error: {error_message}")

    except requests.exceptions.RequestException as e:
        # Handle network errors
        show_home_error_message(app, f"Network error: {str(e)}")
    except Exception as e:
        # Handle unexpected errors
        show_home_error_message(app, f"Unexpected error: {str(e)}")

def show_home_info_message(app, message):
    """
    Displays an informational message in the home page.
    """
    if hasattr(app, 'home_message_label') and app.home_message_label.winfo_exists():
        app.home_message_label.configure(text=message, text_color="green")
        app.home_message_label.after(5000, lambda: clear_home_message(app))

def show_home_error_message(app, message):
    """
    Displays an error message in the home page.
    """
    if hasattr(app, 'home_message_label') and app.home_message_label.winfo_exists():
        app.home_message_label.configure(text=message, text_color="red")
        app.home_message_label.after(5000, lambda: clear_home_message(app))

def clear_home_message(app):
    """
    Clears the informational/error message from the home page.
    """
    if hasattr(app, 'home_message_label') and app.home_message_label.winfo_exists():
        app.home_message_label.configure(text="")
