import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SERVER_URL = os.getenv("SERVER_URL", "https://example.com")
    DRONE_TOKEN = os.getenv("DRONE_TOKEN", "")
    IMAGE_DIR = os.getenv("IMAGE_DIR", "/home/pi/skysync_images")
    LOG_PATH = os.getenv("LOG_PATH", "/var/log/skysync.log")
    KML_PATH = os.getenv("KML_PATH", "/home/pi/mission.kml")
    CAPTURE_INTERVAL_SEC = int(os.getenv("CAPTURE_INTERVAL_SEC", "5"))
    SERIAL_PORT = os.getenv("SERIAL_PORT", "/dev/serial0")
    SERIAL_BAUD = int(os.getenv("SERIAL_BAUD", "57600"))
    MISSION_NAME = os.getenv("MISSION_NAME", "bridge_inspection_001")
    CERT_PATH = os.getenv("CERT_PATH", "/home/pi/cert.pem")
    BATTERY_LOW_THRESHOLD = float(os.getenv("BATTERY_LOW_THRESHOLD", "10.5"))
    WAYPOINT_REACH_THRESHOLD = float(os.getenv("WAYPOINT_REACH_THRESHOLD", "2.0")
