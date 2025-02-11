import customtkinter as ctk
from tkinter import messagebox, ttk
import tkinter as tk
import requests
import sys
import os
import logging
import json
from PIL import Image, ImageTk

from .. import utils

def show_inspection_page(app):
    """Displays the inspection page with mission selection, photo type options, and photo display."""
    utils.clear_display_frame(app)

    # Page Title
    utils.create_label(app, app.display_frame, "Drone Inspection Overview", font=("Helvetica Neue", 30, "bold"))

    # Mission Selection
    utils.create_label(app, app.display_frame, "Select Mission:", font=app.body_font, text_color=app.text_color)
    app.mission_var = tk.StringVar()
    missions = get_missions(app)
    if missions:
        app.mission_dropdown = ctk.CTkOptionMenu(
            app.display_frame,
            variable=app.mission_var,
            values=missions,
            command=lambda mission_name: on_mission_select(app, mission_name),
            fg_color=app.accent_color
        )
        app.mission_dropdown.pack(pady=10)
    else:
        utils.create_label(
            app,
            app.display_frame,
            "No missions available. Please create a mission first.",
            font=app.body_font,
            text_color=app.text_color
        )
        return

    # Photo Type Selection
    utils.create_label(app, app.display_frame, "Select Photo Type:", font=app.body_font, text_color=app.text_color)
    app.photo_type_var = tk.StringVar(value="Select a mission first")
    app.photo_type_dropdown = ctk.CTkOptionMenu(
        app.display_frame,
        variable=app.photo_type_var,
        values=["Select a mission first"],
        command=lambda photo_type: load_photos(app, photo_type),
        fg_color=app.accent_color,
        state="disabled"
    )
    app.photo_type_dropdown.pack(pady=10)

    # Analyze Button
    utils.create_button(
        app,
        app.display_frame,
        "Analyze Inspection Data",
        lambda: analyze_inspection(app),
        fg_color=app.accent_color,
        font=app.subheader_font,
        pady=10
    )

    # Initialize Photos Frame after clearing display_frame
    app.photos_frame = ctk.CTkFrame(app.display_frame, fg_color=app.bg_color)
    app.photos_frame.pack(fill='both', expand=True, padx=50, pady=10)

    # Restore previously selected mission and photo type if available
    if hasattr(app, 'selected_mission') and app.selected_mission in missions:
        app.mission_var.set(app.selected_mission)
        on_mission_select(app, app.selected_mission)

        # If the user had previously selected a photo_type, restore it
        if hasattr(app, 'photo_type') and app.photo_type in ["All", "Crack", "Spall", "Corrosion"]:
            app.photo_type_var.set(app.photo_type)
            load_photos(app, app.photo_type)
        else:
            app.photo_type_var.set("")  
    else:
        app.mission_var.set("")  

def on_mission_select(app, mission_name):
    """Handle mission selection from the dropdown."""
    # If the selected mission is the same as the current mission, just re-enable and update the dropdown
    if getattr(app, 'selected_mission', None) == mission_name:
        app.photo_type_dropdown.configure(values=["All", "Crack", "Spall", "Corrosion"], state="normal")
        return

    # Update the selected mission and reset dependent attributes
    app.mission_name = mission_name
    app.photo_type = None  
    app.photo_type_var.set("")  

    # Enable and set the photo type dropdown options
    app.photo_type_dropdown.configure(values=["All", "Crack", "Spall", "Corrosion"], state="normal")

    # Clear any displayed photos
    if hasattr(app, 'photos_frame') and app.photos_frame.winfo_exists():
        utils.clear_frame(app, app.photos_frame)
    app.photo_images = []

def sync_photos(app, mission_name, photo_type):
    """Sync photos between server and client."""
    mission_dir = os.path.join(app.cache_dir, app.username, mission_name)
    os.makedirs(mission_dir, exist_ok=True)

    # Path for {mission_name}_cache.json
    cache_file = os.path.join(mission_dir, f"{mission_name}_cache.json")
    try:
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                cached_photos = json.load(f)
        else:
            cached_photos = {}
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"Error reading cache file {cache_file}: {e}")
        utils.show_error_message_box(app, f"Error reading cache file: {e}")
        cached_photos = {}

    # Ensure cached_photos is structured as a dict
    if not isinstance(cached_photos, dict):
        logging.warning(f"Invalid cache structure in {cache_file}. Resetting to empty dict.")
        cached_photos = {}

    # Prepare request data
    headers = {"x-access-token": app.token}
    data = {"cached_photos": cached_photos}

    # Send cached data to the server and fetch new photos
    try:
        response = requests.post(
            f"{app.SERVER_URL}/missions/{mission_name}/photos",
            headers=headers,
            json=data,
            # verify=app.CERT_PATH,
            verify=False,
        )
        if response.status_code == 200:
            new_photos = response.json()
            for pt, photos in new_photos.items():
                photo_type_dir = os.path.join(mission_dir, pt)
                os.makedirs(photo_type_dir, exist_ok=True)
                download_new_photos(app, mission_name, pt, photos)
                cached_photos.setdefault(pt, []).extend(photos)
            # Save all cached photos into {mission_name}_cache.json
            with open(cache_file, "w") as f:
                json.dump(cached_photos, f)
        else:
            logging.error(f"Failed to sync photos: {response.status_code} - {response.text}")
            utils.show_error_message_box(app, "Failed to sync photos with the server.")
    except requests.RequestException as e:
        logging.error(f"Error syncing photos: {e}")

def load_cache(cache_file):
    """Load cached photos from {mission_name}_cache.json."""
    try:
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                cached_photos = json.load(f)
        else:
            cached_photos = {}
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"Error reading cache file {cache_file}: {e}. Resetting to empty dict.")
        cached_photos = {}
    if not isinstance(cached_photos, dict):
        logging.warning(f"Invalid cache structure in {cache_file}. Resetting to empty dict.")
        cached_photos = {}
    return cached_photos

def download_new_photos(app, mission_name, photo_type, new_photos):
    """Download new photos from the server and update the cache."""
    mission_dir = os.path.join(app.cache_dir, app.username, mission_name)
    photo_type_dir = os.path.join(mission_dir, photo_type)
    os.makedirs(photo_type_dir, exist_ok=True)

    cache_file = os.path.join(mission_dir, f"{mission_name}_cache.json")

    for photo in new_photos:
        local_path = os.path.join(photo_type_dir, photo)
        if not os.path.exists(local_path):
            try:
                response = requests.get(
                    f"{app.SERVER_URL}/missions/{mission_name}/photos/{photo}",
                    headers={"x-access-token": app.token},
                    # verify=app.CERT_PATH,
                    verify=False,
                    stream=True,
                )
                if response.status_code == 200:
                    with open(local_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    logging.info(f"Downloaded photo: {photo} to {local_path}")
                else:
                    logging.error(f"Failed to download image {photo}: {response.status_code} - {response.text}")
            except requests.RequestException as e:
                logging.error(f"Error downloading image {photo}: {e}")

    # Update {mission_name}_cache.json
    try:
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                cached_photos = json.load(f)
        else:
            cached_photos = {}

        if not isinstance(cached_photos, dict):
            cached_photos = {}

        cached_photos.setdefault(photo_type, []).extend(new_photos)
        with open(cache_file, "w") as f:
            json.dump(cached_photos, f)
    except IOError as e:
        logging.error(f"Error updating cache.json: {e}")

def load_photos(app, photo_type):
    """Load and display photos from cache."""
    if not hasattr(app, 'selected_mission') or not app.selected_mission or not photo_type:
        return

    app.photo_type = photo_type
    sync_photos(app, app.selected_mission, photo_type)

    cache_file = os.path.join(app.cache_dir, app.username, app.selected_mission, f"{app.selected_mission}_cache.json")
    cached_photos = load_cache(cache_file)

    if photo_type == "All":
        photos = [
            {"filename": filename, "photo_type": pt}
            for pt, files in cached_photos.items()
            for filename in files
        ]
    else:
        photos = [{"filename": f, "photo_type": photo_type} for f in cached_photos.get(photo_type, [])]

    display_cached_photos(app, photos)

def get_cached_image(app, photo):
    """Get the local path to a cached image."""
    filename = photo.get("filename")
    if not filename:
        logging.error("Photo does not have a valid filename.")
        return None

    mission_dir = os.path.join(app.cache_dir, app.username, app.selected_mission)
    photo_type = photo.get("photo_type", "Unprocessed")
    photo_type_dir = os.path.join(mission_dir, photo_type)
    local_image_path = os.path.join(photo_type_dir, filename)

    if not os.path.exists(local_image_path):
        logging.error(f"Image file {local_image_path} does not exist.")
        return None
    return local_image_path

def get_missions(app):
    """Fetch the list of missions for the current user."""
    try:
        return utils.fetch_missions(app)
    except Exception as e:
        logging.error(f"Error fetching missions: {e}")
        utils.show_error_message_box(app, "Failed to fetch missions.")
        return []

def analyze_inspection(app):
    """Trigger analysis for the selected mission."""
    # Check if we have app.selected_mission
    if not hasattr(app, 'selected_mission') or not app.selected_mission:
        messagebox.showwarning("Warning", "Please select a mission.")
        app.root.focus_force()
        return

    headers = {'x-access-token': app.token}
    try:
        response = requests.post(
            f'{app.SERVER_URL}/analyze',
            json={'mission_name': app.selected_mission},
            headers=headers,
            # verify=app.CERT_PATH
            verify=False
        )
        if response.status_code == 200:
            messagebox.showinfo("Success", response.json().get('message'))
            app.root.focus_force()
            # Update photo type dropdown after analysis
            app.photo_type_dropdown.configure(values=["All", "Crack", "Spall", "Corrosion"])
            app.photo_type_var.set("All")
            load_photos(app, "All")
        else:
            messagebox.showerror("Error", f"Failed to start analysis: {response.text}")
            app.root.focus_force()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Server connection issue: {e}")
        logging.error(f"Error during analysis: {e}")
        app.root.focus_force()

def get_photos(app, mission_name, photo_type):
    """Fetch photos from the server."""
    try:
        headers = {'x-access-token': app.token}
        params = {}
        if photo_type != "All":
            params['photo_type'] = photo_type

        response = requests.get(
            f"{app.SERVER_URL}/missions/{mission_name}/photos",
            headers=headers,
            params=params,
            # verify=app.CERT_PATH
            verify=False
        )
        if response.status_code == 200:
            photos = response.json()
            logging.info(f"Fetched photos: {photos}")
            if not photos:
                logging.warning("No photos retrieved for the mission.")
            return photos
        else:
            logging.error(f"Failed to fetch photos: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        logging.error(f"Error fetching photos: {e}")
        return []

def get_cached_image(app, photo):
    """Get the local path to a cached image."""
    filename = photo.get("filename")
    if not filename:
        logging.error("Photo does not have a valid filename.")
        return None

    mission_dir = os.path.join(app.cache_dir, app.username, app.mission_name)
    photo_type = photo.get("photo_type", "Unprocessed")
    photo_type_dir = os.path.join(mission_dir, photo_type)
    local_image_path = os.path.join(photo_type_dir, filename)

    if not os.path.exists(local_image_path):
        logging.error(f"Image file {local_image_path} does not exist.")
        return None
    else:
        logging.info(f"Using cached image: {local_image_path}")
    return local_image_path

def display_cached_photos(app, photos):
    """Display cached photos from the local directories."""
    utils.clear_frame(app, app.photos_frame)
    app.photo_images = []  # Prevent garbage collection
    if not photos:
        display_no_photos(app)
        return

    # Create a scrollable canvas for the photo display
    canvas = tk.Canvas(app.photos_frame, highlightthickness=0, bd=0)
    scrollbar = ttk.Scrollbar(app.photos_frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Create an inner frame for the content inside the canvas
    photo_inner_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=photo_inner_frame, anchor="nw")

    # Update the scrollable region when the inner frame's size changes
    photo_inner_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    # Keep track of loaded images
    columns, thumbnail_size, pady = 5, 200, 10
    row, col = 0, 0

    for photo in photos:
        photo_type = photo.get("photo_type")
        filename = photo.get("filename")
        if not filename or not photo_type:
            continue

        # Construct the full path to the photo
        mission_dir = os.path.join(app.cache_dir, app.username, app.selected_mission)
        photo_type_dir = os.path.join(mission_dir, photo_type)
        local_image_path = os.path.join(photo_type_dir, filename)

        if not os.path.exists(local_image_path):
            logging.warning(f"Image file {local_image_path} does not exist. Skipping.")
            continue

        try:
            # Load and resize the photo
            image = Image.open(local_image_path)
            image.thumbnail((thumbnail_size, thumbnail_size))
            photo_image = ImageTk.PhotoImage(image)
            app.photo_images.append(photo_image)  # Prevent garbage collection

            # Determine padding
            if col == 0:
                padx = (0, 5)
            elif col == columns - 1:
                padx = (5, 0)
            else:
                padx = (5, 5)

            # Add image label
            image_label = tk.Label(photo_inner_frame, image=photo_image)
            image_label.grid(row=row, column=col, padx=padx, pady=pady)

            # Add a status label if applicable
            if photo_type in ["Crack", "Spall", "Corrosion"]:
                status_label = tk.Label(
                    photo_inner_frame,
                    text=f"Type: {photo_type}",
                    font=("Helvetica", 10),
                    fg="blue"
                )
                status_label.grid(row=row + 1, column=col, padx=padx, pady=2)

            # Handle column wrapping
            col += 1
            if col >= columns:
                col = 0
                row += 2

        except Exception as e:
            logging.error(f"Error displaying image {local_image_path}: {e}")

    # If no photos were displayed, show "No photos found"
    if not app.photo_images:
        display_no_photos(app)

def display_photos(app, photos):
    """Display photos in a grid layout."""
    utils.clear_frame(app, app.photos_frame)

    canvas = tk.Canvas(app.photos_frame, highlightthickness=0, bd=0)
    scrollbar = ttk.Scrollbar(app.photos_frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Style the scrollbar to make it visually seamless
    style = ttk.Style()
    style.configure("TScrollbar", background=app.bg_color, troughcolor=app.bg_color, bordercolor=app.bg_color, arrowcolor=app.bg_color)

    # Create an inner frame for the content inside the canvas
    photo_inner_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=photo_inner_frame, anchor="nw")

    # Update scrollable region when the inner frame's size changes
    photo_inner_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    # Keep a list of photo images to prevent garbage collection
    app.photo_images = []
    columns, thumbnail_size, pady = 5, 200, 10
    row, col = 0, 0

    total_photos = len(photos)
    for idx, photo in enumerate(photos):
        local_image_path = get_cached_image(app, photo)
        if not local_image_path or not os.path.exists(local_image_path):
            continue

        try:
            # Load and resize the photo
            image = Image.open(local_image_path)
            image.thumbnail((thumbnail_size, thumbnail_size))
            photo_image = ImageTk.PhotoImage(image)
            app.photo_images.append(photo_image)  

            # Determine padx for first and last columns
            if col == 0:
                padx = (0, 5)
            elif col == columns - 1 or idx == total_photos - 1:
                padx = (5, 0)
            else:
                padx = (5, 5)

            image_label = tk.Label(photo_inner_frame, image=photo_image)
            image_label.grid(row=row, column=col, padx=padx, pady=pady)

            # Add a status label if applicable
            if photo.get('photo_type') in ["Crack", "Spall", "Corrosion"]:
                status_label = tk.Label(
                    photo_inner_frame,
                    text=f"Type: {photo['photo_type']}",
                    font=("Helvetica", 10),
                    fg="blue"
                )
                status_label.grid(row=row + 1, column=col, padx=padx, pady=2)

            # Increment column and handle wrapping to the next row
            col += 1
            if col >= columns:
                col = 0
                row += 2  

        except Exception as e:
            logging.error(f"Error displaying image {local_image_path}: {e}")

    # If no photos were displayed, show "No photos found"
    if not app.photo_images:
        logging.info("No photos to display.")
        display_no_photos(app)

def display_no_photos(app):
    """Display a message when no photos are found."""
    utils.clear_frame(app, app.photos_frame)
    utils.create_label(
        app,
        app.photos_frame,
        "No photos found.",
        font=app.body_font,
        text_color=app.text_color
    )
