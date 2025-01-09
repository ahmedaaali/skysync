import customtkinter as ctk
import logging
import requests
from tkinter import messagebox

def fetch_missions(app):
    """Fetch missions for the current user."""
    try:
        headers = {'x-access-token': app.token}
        response = requests.get(
            f"{app.SERVER_URL}/missions/get_missions",
            headers=headers,
            verify=app.CERT_PATH
        )
        if response.status_code == 200:
            missions = response.json()
            return missions if missions else []
        else:
            logging.error(f"Failed to fetch missions: {response.text}")
            return []
    except Exception as e:
        logging.error(f"Error fetching missions: {e}")
        return []

def show_error_message(app, message):
    """Displays an error message and clears it after a delay."""
    if not hasattr(app, 'error_message') or not app.error_message.winfo_exists():
        app.error_message = ctk.CTkLabel(
            app.main_frame,
            text="",
            font=("Helvetica Neue", 12, "italic"),
            text_color="red",
            pady=10
        )
        app.error_message.pack(pady=10)

    app.error_message.configure(text=message)
    app.error_message.after(5000, lambda: clear_error_message(app))

def show_error_message_box(app, message):
    """Displays an error message box."""
    messagebox.showerror("Error", message)

def show_info_message(app, message):
    """Displays an info message and clears it after a delay."""
    if not hasattr(app, 'info_message') or not app.info_message.winfo_exists():
        app.info_message = ctk.CTkLabel(
            app.main_frame,
            text="",
            font=("Helvetica Neue", 12, "italic"),
            text_color="green",
            pady=10
        )
        app.info_message.pack(pady=10)

    app.info_message.configure(text=message)
    app.info_message.after(5000, lambda: clear_info_message(app))

def clear_error_message(app):
    """Clears the displayed error message."""
    if hasattr(app, 'error_message') and app.error_message:
        app.error_message.configure(text="")

def clear_info_message(app):
    """Clears the displayed info message."""
    if hasattr(app, 'info_message') and app.info_message:
        app.info_message.configure(text="")

def enable_mouse_wheel_scrolling(app, event):
    """Enable scrolling in a canvas or scrollable area."""
    if hasattr(app, 'canvas'):
        if event.delta:
            app.canvas.yview_scroll(-1 * int(event.delta / 120), "units")
        else:
            if event.num == 4:
                app.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                app.canvas.yview_scroll(1, "units")

def create_button(app, parent, text, command, pady=10, **kwargs):
    """Helper method to create buttons with consistent styles."""
    button = ctk.CTkButton(
        parent,
        text=text,
        command=command,
        **kwargs
    )
    button.pack(pady=pady)
    return button

def create_label(app, parent, text, font=None, text_color=None, fg_color=None, pady=10, **kwargs):
    """Helper method to create labels with consistent styles."""
    label = ctk.CTkLabel(
        parent,
        text=text,
        font=font or app.body_font,
        text_color=text_color or app.text_color,
        fg_color=fg_color or app.bg_color,
        **kwargs
    )
    label.pack(pady=pady)
    return label

def create_frame(app, parent, fg_color=None, **kwargs):
    """Helper to create a frame with consistent styles."""
    frame = ctk.CTkFrame(parent, fg_color=fg_color or app.bg_color)
    frame.pack(fill=kwargs.get('fill', ctk.BOTH), expand=kwargs.get('expand', True))
    return frame

def create_entry(app, parent, placeholder="", show="", width=200, **kwargs):
    """Helper method to create entry fields with consistent styles."""
    entry = ctk.CTkEntry(
        parent,
        placeholder_text=placeholder,
        show=show,
        width=width,
        **kwargs
    )
    return entry

def create_title(app, text, font_size=20):
    """Helper method to create a title label."""
    create_label(
        app,
        app.display_frame,
        text=text,
        font=("Helvetica Neue", font_size, "bold"),
        text_color=app.text_color,
        pady=10
    )

def clear_frame(app, frame=None):
    """Clears all widgets from the specified frame. If no frame is specified, clears the app's main_frame."""
    if frame is None:
        frame = app.main_frame  
    if hasattr(frame, 'winfo_children'):
        for widget in frame.winfo_children():
            widget.destroy()
    else:
        logging.warning(f"Attempted to clear a frame that does not exist or is invalid: {frame}")

def clear_display_frame(app):
    """Clears all widgets from the display frame."""
    if hasattr(app, 'display_frame') and app.display_frame.winfo_exists():
        for widget in app.display_frame.winfo_children():
            widget.destroy()
    else:
        logging.warning("Display frame not found or does not exist.")

def enable_mouse_wheel_scrolling(app):
    """Return a handler for mouse wheel scrolling in a canvas."""
    def handler(event):
        if hasattr(app, 'canvas'):
            if event.delta:
                app.canvas.yview_scroll(-1 * int(event.delta / 120), "units")
            else:
                if event.num == 4:
                    app.canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    app.canvas.yview_scroll(1, "units")
    return handler
