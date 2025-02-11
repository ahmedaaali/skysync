import os
import time
import json
import logging
from picamera import PiCamera

class CameraManager:
    def __init__(self, image_dir, vehicle, capture_interval):
        self.image_dir = image_dir
        self.vehicle = vehicle
        self.capture_interval = capture_interval
        os.makedirs(self.image_dir, exist_ok=True)
        self.camera = PiCamera()
        self.camera.resolution = (1920, 1080)
        self.running = True

    def start_capture_loop(self, command_handler):
        while self.running:
            # If GCS changed camera interval
            if command_handler.change_camera_interval:
                self.capture_interval = command_handler.change_camera_interval
                command_handler.change_camera_interval = None

            timestamp = int(time.time())
            lat = self.vehicle.location.global_frame.lat
            lon = self.vehicle.location.global_frame.lon
            alt = self.vehicle.location.global_frame.alt

            img_name = f"image_{timestamp}.jpg"
            img_path = os.path.join(self.image_dir, img_name)
            self.camera.capture(img_path)

            metadata = {
                "latitude": lat,
                "longitude": lon,
                "altitude": alt,
                "timestamp": timestamp
            }
            meta_name = f"metadata_{timestamp}.json"
            meta_path = os.path.join(self.image_dir, meta_name)
            with open(meta_path, "w") as f:
                json.dump(metadata, f)
            logging.info(f"Captured image {img_path} with metadata {meta_path}")

            time.sleep(self.capture_interval)
