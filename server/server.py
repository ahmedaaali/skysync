import logging
import os
import sys
import signal
import argparse

# Import the ServerManager and define the `app` at the module level
from conf.update_server_conf import update_configuration
from flask import jsonify, request
from models import User, Admin, Mission
from server_manager import ServerManager
from analysis import analysis_blueprint
from auth import auth_blueprint
from missions import missions_blueprint
from photos import photos_blueprint

# Ensure the current directory is in the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create the server manager instance
server_manager = ServerManager()

# Define the app for Gunicorn
app = server_manager.create_app()

# Pass server_manager to blueprints
analysis_blueprint.server_manager = server_manager
auth_blueprint.server_manager = server_manager
missions_blueprint.server_manager = server_manager
photos_blueprint.server_manager = server_manager

# Register blueprints
app.register_blueprint(analysis_blueprint)
app.register_blueprint(auth_blueprint)
app.register_blueprint(missions_blueprint)
app.register_blueprint(photos_blueprint)

@app.route('/status', methods=['GET'])
def status():
    return "Server is running", 200

@app.route('/users', methods=['GET'])
def get_users():
    """Endpoint to fetch all users."""
    session = server_manager.get_database_session()()
    try:
        users = session.query(User).all()
        users_list = [{"username": user.username} for user in users]
        return jsonify(users_list), 200
    except Exception as e:
        logging.error(f"Error fetching users: {e}")
        return jsonify({"error": "Failed to fetch users."}), 500
    finally:
        session.close()

@app.route('/admin_users', methods=['GET'])
def get_admin_users():
    """Endpoint to fetch all admin users."""
    session = server_manager.get_database_session()()
    try:
        users = session.query(Admin).filter_by(role='admin').all()
        users_list = [{"username": user.username} for user in users]
        return jsonify(users_list), 200
    except Exception as e:
        logging.error(f"Error fetching admin users: {e}")
        return jsonify({"error": "Failed to fetch admin users."}), 500
    finally:
        session.close()

@app.route('/client_users', methods=['GET'])
def get_client_users():
    """Endpoint to fetch all client users."""
    session = server_manager.get_database_session()()
    try:
        logging.info("Fetching client users from the database.")
        users = session.query(User).filter_by(role='client').all()
        users_list = [{"username": user.username} for user in users]
        print(users_list)
        logging.info(f"Fetched {len(users_list)} client users.")
        return jsonify(users_list), 200
    except Exception as e:
        logging.error(f"Error fetching client users: {e}")
        return jsonify({"error": "Failed to fetch client users."}), 500
    finally:
        session.close()

@app.route('/missions', methods=['GET'])
def get_missions():
    """Endpoint to fetch all missions."""
    session = server_manager.get_database_session()()
    username = request.args.get('username')
    try:
        missions = session.query(Mission).filter_by(username=username).all()
        missions_list = [{"mission_name": mission.mission_name} for mission in missions]
        logging.info(f"Error fetching missions: {e}", username, missions)
        return jsonify(missions_list), 200
    except Exception as e:
        logging.error(f"Error fetching missions: {e}", username, missions)
        return jsonify({"error": "Failed to fetch missions."}), 500
    finally:
        session.close()


if __name__ == "__main__":
    # Parse arguments for configuration and runtime options
    parser = argparse.ArgumentParser(
        description="Run the SkySync server with various configuration and runtime options."
    )
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
        "-g", "--run-gui", 
        action="store_true", 
        help="Start the Server GUI."
    )
    args = parser.parse_args()

    # Display help message if requested (automatically handled by argparse)

    # Update configuration based on arguments
    update_configuration(verbose=args.verbose, regenerate_cert=args.regenerate_cert)

    # FIXME:
    # Updated ENV vairables aren't being used, update conf script needs to be run beforehand. Need a way to wait for update_configuration to execute before initializing or executing anything else

    # Set up signal handlers for clean shutdown
    signal.signal(signal.SIGINT, server_manager.handle_signal)
    signal.signal(signal.SIGTERM, server_manager.handle_signal)

    # Start and monitor server processes
    server_manager.start_processes(run_gui=args.run_gui)
    server_manager.monitor_processes()
