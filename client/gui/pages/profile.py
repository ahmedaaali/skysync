from .. import utils

def show_profile_page(app):
    utils.clear_display_frame(app)
    utils.create_label(app, app.display_frame, "User Profile", font=("Helvetica Neue", 30, "bold"))

    profile_info = (
        f"Username: {app.username}\n"
        "Role: Drone Operator\n"
        "Project: SkySync - Autonomous Drone System"
    )
    utils.create_label(app, app.display_frame, profile_info, font=app.body_font, text_color=app.text_color, wraplength=600)
