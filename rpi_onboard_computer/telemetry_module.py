import time
import requests
import logging
from config import Config

class TelemetryMonitor:
    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.headers = {'x-access-token': Config.DRONE_TOKEN}
        self.telemetry_url = f"{Config.SERVER_URL}/missions/{Config.MISSION_NAME}/telemetry"

    def run_telemetry_loop(self):
        while True:
            lat = self.vehicle.location.global_frame.lat
            lon = self.vehicle.location.global_frame.lon
            alt = self.vehicle.location.global_relative_frame.alt
            batt = self.vehicle.battery.voltage
            payload = {
                'latitude': lat,
                'longitude': lon,
                'altitude': alt,
                'battery': batt
            }
            try:
                requests.post(self.telemetry_url, json=payload, headers=self.headers, verify=False)
            except Exception as e:
                logging.error(f"Telemetry upload error: {e}")
            time.sleep(30)
