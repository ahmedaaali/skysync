import os
import sys
import time
import logging
import threading
import argparse
import requests
from dronekit import connect
from config import Config
from waypoint_manager import WaypointManager
from command_handler import CommandHandler
from drone_controller import DroneController
from camera_manager import CameraManager
from uploader import Uploader
from telemetry_monitor import TelemetryMonitor
from tofu_pinning import verify_or_set_fingerprint

def setup_logging():
    logging.basicConfig(
        filename=Config.LOG_PATH,
        level=logging.INFO,
        format='%(asctime)s:%(levelname)s:%(message)s'
    )
    logging.info("SkySync Drone System Starting.")

def drone_login(username, password, role="drone"):
    """
    Example function to log in as the drone endpoint.
    If successful, store token in Config.DRONE_TOKEN or return it.
    """
    data = {"username": username, "password": password, "role": role}
    # skip normal TLS checks, relying on pinned-fingerprint
    resp = requests.post(f"{Config.SERVER_URL}/login", json=data, verify=False)
    if resp.status_code == 200:
        token = resp.json().get('token')
        if token:
            logging.info("Drone login successful.")
            Config.DRONE_TOKEN = token
            return token
        else:
            logging.error("Drone login failed: No token received.")
            sys.exit(1)
    else:
        logging.error(f"Drone login failed: {resp.status_code} - {resp.text}")
        sys.exit(1)

def start_heartbeat_loop(token, interval=15):
    """
    If you want the drone to periodically let the server know it's alive:
    """
    import threading

    def heartbeat():
        while True:
            try:
                requests.post(
                    f"{Config.SERVER_URL}/drone/heartbeat",
                    headers={"x-access-token": token},
                    verify=False
                )
            except Exception as e:
                logging.warning(f"Failed to send drone heartbeat: {e}")
            time.sleep(interval)

    t = threading.Thread(target=heartbeat, daemon=True)
    t.start()

def main():
    parser = argparse.ArgumentParser(description="SkySync RPi main script with TOFU & IP override.")
    parser.add_argument("-p","--server-ip", type=str, help="Override the server IP address from .env")
    parser.add_argument("--baud", type=int, default=57600, help="Baud rate for the Pixhawk serial connection.")
    parser.add_argument("--alt", type=float, default=20, help="Takeoff altitude (meters).")
    parser.add_argument("--username", type=str, default="", help="Drone user account username.")
    parser.add_argument("--password", type=str, default="", help="Drone user account password.")
    args = parser.parse_args()

    # 1) Setup logging
    setup_logging()

    # 2) Override server IP if needed
    if args.server_ip:
        # Basic approach
        old_url = Config.SERVER_URL
        parts = old_url.split(':')
        if len(parts) >= 3:
            # e.g. "https://127.0.0.1:5000"
            scheme = parts[0]  # "https"
            port = parts[-1]   # "5000"
        else:
            scheme = "https"
            port = "5000"
        new_url = f"{scheme}:{args.server_ip}:{port}"
        Config.SERVER_URL = new_url
        logging.info(f"Overrode SERVER_URL to {Config.SERVER_URL}")

    # 3) Do TOFU pinned-fingerprint check
    pinned_file = os.path.join(os.path.dirname(__file__), "pinned_fingerprint.txt")
    verify_or_set_fingerprint(Config.SERVER_URL, pinned_file)

    # 4) Drone login (if you want to keep the same user credentials in .env, or pass them in)
    if args.username and args.password:
        # Attempt drone login
        token = drone_login(args.username, args.password, role="drone")
        # Optionally start heartbeat
        start_heartbeat_loop(token, interval=15)
    else:
        # If you have a pre-set DRONE_TOKEN or some other approach, do that
        logging.info("No username/password provided. Skipping login/heartbeat.")

    # 5) Connect to Pixhawk
    logging.info("Connecting to Pixhawk flight controller...")
    vehicle = connect(Config.SERIAL_PORT, wait_ready=True, baud=args.baud)
    logging.info("Connected to Pixhawk.")

    # 6) Waypoints
    wp_manager = WaypointManager(Config.KML_PATH)
    waypoints = wp_manager.load_waypoints()
    if not waypoints:
        logging.error("No waypoints loaded from KML. Aborting mission.")
        sys.exit(1)

    # 7) Initialize command handler
    cmd_handler = CommandHandler(vehicle)

    # 8) Start telemetry monitor thread
    telem_monitor = TelemetryMonitor(vehicle)
    telem_thread = threading.Thread(target=telem_monitor.run_telemetry_loop, daemon=True)
    telem_thread.start()

    # 9) Drone Controller
    drone_ctrl = DroneController(vehicle, cmd_handler)
    drone_ctrl.arm_and_takeoff(args.alt)

    # 10) Start camera capture thread
    cam_manager = CameraManager(Config.IMAGE_DIR, vehicle, Config.CAPTURE_INTERVAL_SEC)
    camera_thread = threading.Thread(target=cam_manager.start_capture_loop, args=(cmd_handler,), daemon=True)
    camera_thread.start()

    # 11) Start uploader thread
    uploader = Uploader(Config.IMAGE_DIR, Config.MISSION_NAME)
    uploader_thread = threading.Thread(target=uploader.run_upload_loop, daemon=True)
    uploader_thread.start()

    # 12) Follow mission waypoints
    drone_ctrl.follow_waypoints(waypoints)

    # 13) Close vehicle after done
    vehicle.close()
    logging.info("Mission ended. Vehicle closed.")

if __name__ == "__main__":
    main()
