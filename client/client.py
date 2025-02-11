import os
import sys
import argparse
import customtkinter as ctk

# Ensure the current directory is in the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the update_configuration function
from conf.update_client_conf import update_configuration
from gui.app import SkySyncApp

if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser(description="Run the SkySync client.")
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output for configuration updates."
    )
    parser.add_argument(
        "-r", "--regenerate-cert",
        action="store_true",
        help="Force regeneration of SSL certificates."
    )
    parser.add_argument(
        "-p", "--server-ip",
        type=str,
        help="Specify the server IP address (overrides .env)."
    )
    args = parser.parse_args()

    # Run update_configuration with parsed arguments
    update_configuration(verbose=args.verbose, regenerate_cert=args.regenerate_cert, server_ip=args.server_ip)

    # Initialize and run the application
    root = ctk.CTk()
    app = SkySyncApp(root)
    if not app.load_session():
        app.show_login_screen()
    else:
        app.show_main_interface()
    root.mainloop()
