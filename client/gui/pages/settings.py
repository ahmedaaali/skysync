from .. import utils
import customtkinter as ctk
import requests

def show_settings_page(app):
    """
    Displays the settings page.
    """
    utils.clear_display_frame(app)  # Clear the display frame

    # Add a title label
    utils.create_label(
        app,
        app.display_frame,
        "Settings",
        font=("Helvetica Neue", 30, "bold"),
        pady=(10, 20),
    )

    # Add a button to change the password
    utils.create_button(
        app,
        app.display_frame,
        "Change Password",
        command=lambda: show_change_password_dialog(app),
        pady=10,
        font=app.body_font,
        fg_color=app.accent_color,
    ).pack(pady=10)

    # Add a placeholder for future settings options (optional)
    utils.create_label(
        app,
        app.display_frame,
        "Other settings options will appear here.",
        font=app.body_font,
        text_color=app.text_color,
        pady=10,
    )

    # Add a message label for success/error messages
    if not hasattr(app, 'settings_message_label') or not app.settings_message_label.winfo_exists():
        app.settings_message_label = ctk.CTkLabel(
            app.display_frame,
            text="",
            font=app.body_font,
            text_color="green",
            anchor="center",
            wraplength=600,
        )
        app.settings_message_label.pack(pady=10)

def show_change_password_dialog(app):
    """Show a modal dialog for changing the password."""
    dialog = ctk.CTkToplevel(app.root)
    dialog.title("Change Password")
    dialog.geometry("400x450")
    dialog.grab_set()

    # Title
    utils.create_label(
        app,
        dialog,
        "Change Password",
        font=("Helvetica Neue", 20, "bold"),
        pady=(10, 20),
    )

    # Old Password
    old_password_label = utils.create_label(app, dialog, "Old Password:", font=app.body_font, pady=5, anchor="w")
    old_password_entry = utils.create_entry(app, dialog, placeholder="Enter your old password", show="*")
    old_password_entry.pack(pady=(5, 15), padx=20, fill="x")

    # New Password
    new_password_label = utils.create_label(app, dialog, "New Password:", font=app.body_font, pady=5, anchor="w")
    new_password_entry = utils.create_entry(app, dialog, placeholder="Enter your new password", show="*")
    new_password_entry.pack(pady=(5, 15), padx=20, fill="x")

    # Confirm Password
    confirm_password_label = utils.create_label(app, dialog, "Confirm Password:", font=app.body_font, pady=5, anchor="w")
    confirm_password_entry = utils.create_entry(app, dialog, placeholder="Confirm your new password", show="*")
    confirm_password_entry.pack(pady=(5, 15), padx=20, fill="x")

    # Submit Button
    submit_button = ctk.CTkButton(
        dialog,
        text="Submit",
        command=lambda: submit_password_change(
            app, old_password_entry, new_password_entry, confirm_password_entry, dialog
        ),
        fg_color=app.success_color,
        font=app.body_font,
    )
    submit_button.pack(pady=20)

    # Close Button
    close_button = ctk.CTkButton(dialog, text="Close", command=lambda: close_dialog(dialog, app), font=app.body_font)
    close_button.pack(pady=10)

    # Bind the "Enter" key to trigger the submit button
    dialog.bind(
        "<Return>",
        lambda event: submit_password_change(
            app, old_password_entry, new_password_entry, confirm_password_entry, dialog
        )
    )

    # Focus on the dialog
    dialog.focus_force()

def close_dialog(dialog, app):
    """Close the dialog and rebind the Enter key to the root."""
    dialog.destroy()
    app.root.bind("<Return>", lambda event: None)  
    app.root.focus_force()  

def submit_password_change(app, old_password_entry, new_password_entry, confirm_password_entry, dialog):
    """Handle the logic for changing the password."""
    old_password = old_password_entry.get()
    new_password = new_password_entry.get()
    confirm_password = confirm_password_entry.get()

    if not new_password or not confirm_password:
        utils.show_error_message_box(app, "Password fields cannot be empty.")
        dialog.after(100, dialog.focus_force)
        return

    if new_password != confirm_password:
        utils.show_error_message_box(app, "New passwords do not match.")
        dialog.after(100, dialog.focus_force)
        return

    if len(new_password) < 8:
        utils.show_error_message_box(app, "Password must be at least 8 characters long.")
        dialog.after(100, dialog.focus_force)
        return

    if old_password == new_password:
        utils.show_error_message_box(app, "New password cannot be the same as the old password.")
        dialog.after(100, dialog.focus_force)
        return

    # Send change password request to server
    try:
        headers = {
            "x-access-token": app.token,  
            "Content-Type": "application/json"
        }
        payload = {"old_password": old_password, "new_password": new_password}

        response = requests.post(
            f"{app.SERVER_URL}/change_password",
            json=payload,
            headers=headers,
            verify=app.CERT_PATH,
        )
        if response.status_code == 200:
            show_settings_info_message(app, "Password changed successfully!")
            close_dialog(dialog, app)
        else:
            utils.show_error_message_box(
                app, f"Failed to change password: {response.status_code} {response.json().get('error', 'Unknown error')}"
            )
            dialog.after(100, dialog.focus_force)
    except requests.exceptions.RequestException as e:
        utils.show_error_message_box(app, f"Server connection issue: {e}")
        dialog.after(100, dialog.focus_force)

def show_settings_info_message(app, message):
    """Displays an info message in the settings page."""
    if hasattr(app, 'settings_message_label'):
        app.settings_message_label.configure(text=message, text_color="green")
        app.settings_message_label.after(5000, lambda: clear_settings_message(app))

def show_settings_error_message(app, message):
    """Displays an error message in the settings page."""
    if hasattr(app, 'settings_message_label'):
        app.settings_message_label.configure(text=message, text_color="red")
        app.settings_message_label.after(5000, lambda: clear_settings_message(app))

def clear_settings_message(app):
    """Clears the message displayed in the settings page."""
    if hasattr(app, 'settings_message_label'):
        app.settings_message_label.configure(text="")

