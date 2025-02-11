import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import requests
import os
import logging

from .. import utils

def show_upload_page(app):
    """Displays the Upload Images page."""
    if not hasattr(app, 'check_vars'):
        app.check_vars = []

    # Clear the display frame and set the page title
    utils.clear_display_frame(app)
    utils.create_title(app, "Upload Mission Images", font_size=30)

    # Mission Dropdown
    utils.create_label(
        app,
        app.display_frame,
        "Select Mission:",
        font=app.body_font,
        text_color=app.text_color
    )

    app.mission_var = tk.StringVar()
    missions = get_missions(app)

    if missions:
        app.mission_dropdown = ctk.CTkOptionMenu(
            app.display_frame,
            variable=app.mission_var,
            values=missions,
            command=lambda mission: on_mission_select(app, mission),
            fg_color=app.accent_color
        )
    else:
        app.mission_dropdown = ctk.CTkOptionMenu(
            app.display_frame,
            variable=app.mission_var,
            values=["Please create a mission first"],
            state="disabled",
            fg_color=app.accent_color
        )
    app.mission_dropdown.pack(pady=10)

    if missions and hasattr(app, 'selected_mission') and app.selected_mission in missions:
        app.mission_var.set(app.selected_mission)
    else:
        app.mission_var.set("" if missions else "Please create a mission first")

    # Initialize image tracking attributes if not already set
    if not hasattr(app, 'selected_images'):
        app.selected_images = []
    if not hasattr(app, 'uploaded_images'):
        app.uploaded_images = {}
    if not hasattr(app, 'last_directory'):
        app.last_directory = os.path.expanduser("~")

    # Left Frame
    left_frame = ctk.CTkFrame(app.display_frame, width=200, fg_color=app.bg_color)
    left_frame.pack(side="left", fill="y", padx=10, pady=10)

    blank_label_left = ctk.CTkLabel(left_frame, text="", width=200)
    blank_label_left.pack()

    # Vertical Separator
    separator = tk.Canvas(app.display_frame, width=3, bg="gray", highlightthickness=0)
    separator.pack(side="left", fill="y", padx=0)

    # Right Frame
    right_frame = ctk.CTkFrame(app.display_frame, width=700, fg_color=app.bg_color)
    right_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    blank_label_right = ctk.CTkLabel(right_frame, text="", width=600)
    blank_label_right.pack()

    # Buttons in Left Frame
    utils.create_button(
        app,
        left_frame,
        "Browse Images",
        lambda: browse_images(app),
        fg_color=app.accent_color,
        font=app.subheader_font,
        pady=5
    )
    utils.create_button(
        app,
        left_frame,
        "Browse Folder",
        lambda: browse_folder(app),
        fg_color=app.accent_color,
        font=app.subheader_font,
        pady=5
    )
    utils.create_button(
        app,
        left_frame,
        "Upload",
        lambda: validate_upload(app),
        fg_color=app.success_color,
        font=app.subheader_font,
        pady=5
    )
    utils.create_button(
        app,
        left_frame,
        "Remove Selected",
        lambda: remove_selected_images(app),
        fg_color=app.warning_color,
        font=app.subheader_font,
        pady=5
    )

    # Message Label
    app.message_label = ctk.CTkLabel(
        left_frame,
        text="",
        font=app.body_font,
        text_color="green",
        anchor="center",
        wraplength=200
    )
    app.message_label.pack(pady=10)

    # image Display Area
    canvas = tk.Canvas(right_frame, bg=app.bg_color, highlightthickness=0)
    scrollbar = tk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    app.images_display_frame = ctk.CTkFrame(canvas, fg_color=app.bg_color)
    canvas.create_window((0, 0), window=app.images_display_frame, anchor="nw")

    app.images_display_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    app.canvas = canvas

    # Check All Button
    app.check_all_var = tk.BooleanVar(value=False)
    app.check_all_button = ctk.CTkButton(
        app.images_display_frame,
        text="Check All",
        command=lambda: toggle_check_all(app),
        fg_color=app.accent_color,
        font=app.subheader_font,
        width=100
    )

    # Checkbox Frame
    app.checkboxes_frame = ctk.CTkFrame(app.images_display_frame, fg_color=app.bg_color)
    app.checkboxes_frame.pack(fill='both', expand=True)
    # Restore image list display if previously loaded
    update_selected_images_display(app)

    # Restore image list display if previously loaded
    update_selected_images_display(app)

    canvas.bind_all("<MouseWheel>", utils.enable_mouse_wheel_scrolling(app))

def get_missions(app):
    """Fetch the list of missions for the current user."""
    return utils.fetch_missions(app)

def on_mission_select(app, mission):
    """Handle mission selection."""
    if hasattr(app, 'selected_mission') and app.selected_mission != mission:
        # Clear previous images and uploaded status when a new mission is selected
        app.selected_images = []
        app.check_vars = []
        app.uploaded_images = {}
    logging.info(f"Mission selected: {mission}")
    app.selected_mission = mission
    update_selected_images_display(app)

def remove_selected_images(app):
    """Removes selected images from the list and reorders the display."""
    # Check if a mission is selected
    if not hasattr(app, 'selected_mission') or not app.selected_mission:
        show_upload_error_message(app, "Please select a mission first.")
        return

    # Check if any photos are selected
    if not hasattr(app, 'check_vars') or not app.check_vars or not any(check_var.get() for _, check_var in app.check_vars):
        show_upload_error_message(app, "Please select photos first.")
        return

    selected_to_remove = [image_path for image_path, check_var in app.check_vars if check_var.get()]
    app.selected_images = [image for image in app.selected_images if image not in selected_to_remove]

    # Reset the checkboxes and refresh the display
    update_selected_images_display(app)

def validate_upload(app):
    """Ensure a mission is selected before proceeding with upload."""
    selected_mission = app.mission_var.get()
    if not selected_mission or selected_mission == "Please create a mission first":
        show_upload_error_message(app, "Please select a mission before uploading images.")
        return
    upload_images(app)

def update_selected_images_display(app):
    """Display the selected images in the right frame."""
    for widget in app.checkboxes_frame.winfo_children():
        widget.destroy()

    if not app.selected_images:
        app.check_all_button.pack_forget()
        return

    app.check_all_button.pack(anchor="w", pady=5, padx=10)

    app.check_vars = []
    for idx, image in enumerate(app.selected_images, start=1):
        imagename = os.path.basename(image)

        image_frame = ctk.CTkFrame(app.checkboxes_frame, fg_color=app.bg_color)
        image_frame.pack(anchor="w", fill="x", padx=20, pady=2)

        if app.uploaded_images.get(image):
            label = ctk.CTkLabel(
                image_frame,
                text=f"{idx}: {imagename}",
                font=("Helvetica", 12),
                text_color="green"
            )
            label.pack(side="left")
            status_label = ctk.CTkLabel(
                image_frame,
                text="Uploaded",
                font=("Helvetica", 12),
                text_color="green"
            )
            status_label.pack(side="right", padx=10)
        else:
            check_var = tk.BooleanVar(value=app.check_all_var.get())
            app.check_vars.append((image, check_var))

            checkbox = ctk.CTkCheckBox(
                image_frame,
                text=f"{idx}: {imagename}",
                variable=check_var,
                onvalue=True,
                offvalue=False,
                font=("Helvetica", 14),
                text_color="white"
            )
            checkbox.pack(side="left", padx=5)

def toggle_check_all(app):
    """Toggle the state of all checkboxes."""
    new_state = not app.check_all_var.get()
    app.check_all_var.set(new_state)
    for _, check_var in app.check_vars:
        check_var.set(new_state)

def browse_images(app):
    """Open a image dialog to select image images."""
    selected_mission = app.mission_var.get()
    if not selected_mission or selected_mission == "Please create a mission first":
        show_upload_error_message(app, "Please select a mission before selecting images.")
        return
    try:
        image_paths = filedialog.askopenfilenames(
            title="Select Images",
            initialdir=app.last_directory,
            filetypes=[
                ("Image Files", ("*.png", "*.jpg", "*.jpeg", "*.webp", "*.bmp", "*.tiff")),
                ("All images", "*.*")
            ]
        )
        app.root.focus_force()

        if image_paths:
            app.last_directory = os.path.dirname(image_paths[0])
            allowed_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff')
            new_images = []
            for image_path in image_paths:
                if os.path.isfile(image_path) and image_path not in app.selected_images:
                    if image_path.lower().endswith(allowed_extensions):
                        if app.uploaded_images.get(image_path):
                            continue  
                        app.selected_images.append(image_path)
                        new_images.append(image_path)
            if new_images:
                update_selected_images_display(app)
            else:
                show_upload_error_message(app, "No valid image images were selected or images have already been uploaded.")
        else:
            show_upload_error_message(app, "No images selected.")
    except Exception as e:
        logging.error(f"Error in browse_images: {e}")
        show_upload_error_message(app, f"An unexpected error occurred: {e}")

def browse_folder(app):
    """Open a dialog to select a folder and add all image files inside it."""
    selected_mission = app.mission_var.get()
    if not selected_mission or selected_mission == "Please create a mission first":
        show_upload_error_message(app, "Please select a mission before selecting a folder.")
        return
    try:
        folder_path = filedialog.askdirectory(
            title="Select Folder Containing Images",
            initialdir=app.last_directory
        )
        app.root.focus_force()

        if folder_path:
            app.last_directory = folder_path
            image_files = []
            allowed_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff')
            for root, dirs, images in os.walk(folder_path):
                for image in images:
                    if image.lower().endswith(allowed_extensions):
                        image_path = os.path.join(root, image)
                        if image_path not in app.selected_images and not app.uploaded_images.get(image_path):
                            image_files.append(image_path)
            if image_files:
                app.selected_images.extend(image_files)
                update_selected_images_display(app)
            else:
                show_upload_error_message(app, "No image files found in the selected folder or images have already been uploaded.")
        else:
            show_upload_error_message(app, "No folder selected.")
    except Exception as e:
        logging.error(f"Error in browse_folder: {e}")
        show_upload_error_message(app, f"An unexpected error occurred: {e}")

def upload_images(app):
    """Upload selected images to the server."""
    if not app.selected_images:
        show_upload_error_message(app, "No images selected for upload.")
        return
    process_upload(app)

def process_upload(app):
    selected_mission = app.mission_var.get()
    if not selected_mission or selected_mission == "Please create a mission first":
        show_upload_error_message(app, "Please select a valid mission before uploading.")
        return

    headers = {'x-access-token': app.token}
    images_to_upload = []
    images_uploaded = []

    for image_path, check_var in app.check_vars:
        if check_var.get():
            try:
                image_obj = open(image_path, 'rb')
                images_to_upload.append(('images', (os.path.basename(image_path), image_obj)))
                images_uploaded.append(image_path)
            except FileNotFoundError:
                logging.error(f"Images not found: {image_path}")
                show_upload_error_message(app, f"Images not found: {image_path}")
                continue

    if not images_to_upload:
        show_upload_error_message(app, "No images selected for upload.")
        return

    # Updated URL to include the mission_name
    url = f'{app.SERVER_URL}/missions/{selected_mission}/upload_images'
    data = {'mission_name': selected_mission}  

    try:
        response = requests.post(
            url,
            headers=headers,
            files=images_to_upload,
            data=data,
            # verify=app.CERT_PATH
            verify=False
        )

        for _, (_, image_obj) in images_to_upload:
            image_obj.close()

        if response.status_code == 200:
            show_upload_info_message(app, "Images uploaded successfully.")
            for image_path in images_uploaded:
                app.uploaded_images[image_path] = True
            update_selected_images_display(app)
        else:
            show_upload_error_message(app, f"Failed to upload images: {response.text}")

    except requests.exceptions.SSLError as ssl_error:
        logging.error(f"SSL Error: {ssl_error}")
        show_upload_error_message(app, "SSL Error: Please check the server certificate.")
    except requests.exceptions.RequestException as req_error:
        logging.error(f"Request Error: {req_error}")
        show_upload_error_message(app, "Request Error: Unable to connect to the server.")

def show_upload_info_message(app, message):
    """Displays an info message in the upload page and clears it after a delay."""
    if hasattr(app, 'message_label'):
        app.message_label.configure(text=message, text_color="green")
        app.message_label.after(5000, lambda: clear_upload_message(app))

def show_upload_error_message(app, message):
    """Displays an error message in the upload page and clears it after a delay."""
    if hasattr(app, 'message_label'):
        app.message_label.configure(text=message, text_color="red")
        app.message_label.after(5000, lambda: clear_upload_message(app))

def clear_upload_message(app):
    """Clears the message displayed in the upload page."""
    if hasattr(app, 'message_label'):
        app.message_label.configure(text="")

# TODO: 
# 3 columns for buttons, image file names and uploaded message
# blank labels for correct widths and wraparound
# file names wrap around and always start from the left
# fix scrollbar color
# when changing missions, everything needs to be cleared
