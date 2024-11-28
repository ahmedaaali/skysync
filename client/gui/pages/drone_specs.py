from .. import utils

def show_drone_specs(app):
    utils.clear_display_frame(app)
    utils.create_label(app, app.display_frame, "Drone Specifications", font=("Helvetica Neue", 30, "bold"))

    specs_list = [
        "• Pixhawk 2.4 - Flight Controller",
        "• Raspberry Pi 5 - On-board Computer",
        "• RPI HQ Camera - Capture Camera",
        "• 5.1Ah 3S Battery - Power Source",
        "• SiK Telemetry Radio V3 - Data Communication",
        "• CubePilot Here4 RTK GNSS - High Accuracy Positioning",
    ]
    specs_text = "\n\n".join(specs_list)
    utils.create_label(app, app.display_frame, specs_text, font=app.body_font, text_color=app.text_color, wraplength=600, justify="left")
