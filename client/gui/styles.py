import customtkinter as ctk

def setup_styles(app):
    """Set up color schemes and fonts."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app.bg_color = "#1c1c1c"
    app.accent_color = "#007b83"
    app.light_accent = "#4ecdc4"
    app.text_color = "#f5f5f5"
    app.success_color = "#4caf50"
    app.warning_color = "#e74c3c"
    app.error_color = "#f44336"
    app.header_font = ("Helvetica Neue", 40, "bold")
    app.subheader_font = ("Helvetica Neue", 20, "italic")
    app.body_font = ("Helvetica Neue", 16)
