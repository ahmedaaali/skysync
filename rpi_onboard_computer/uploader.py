import os
import time
import requests
import json
import logging
from config import Config

class Uploader:
    def __init__(self, image_dir, mission_name):
        self.image_dir = image_dir
        self.mission_name = mission_name
        self.headers = {'x-access-token': Config.DRONE_TOKEN}
        self.upload_url = f"{Config.SERVER_URL}/missions/{mission_name}/upload_images"

    def run_upload_loop(self):
        while True:
            self.upload_pending_files()
            time.sleep(10)

    def upload_pending_files(self):
        files = os.listdir(self.image_dir)
        images = [f for f in files if f.endswith('.jpg')]
        for img in images:
            meta = img.replace('.jpg', '.json')
            img_path = os.path.join(self.image_dir, img)
            meta_path = os.path.join(self.image_dir, meta)
            if not os.path.exists(meta_path):
                continue
            self.upload_file(img_path, meta_path)

    def upload_file(self, img_path, meta_path):
        with open(meta_path, 'r') as m:
            metadata = json.load(m)
        data = {'mission_name': self.mission_name, 'metadata': json.dumps(metadata)}

        with open(img_path, 'rb') as f:
            files = {'images': (os.path.basename(img_path), f)}
            try:
                # verify=False for pinned-fingerprint approach
                response = requests.post(self.upload_url, headers=self.headers, files=files, data=data, verify=False)
                if response.status_code == 200:
                    ack = response.json()
                    # In your server code, if you return {"message": "Images uploaded successfully"}
                    # adjust logic accordingly
                    msg = ack.get('message', '')
                    if "uploaded" in msg.lower() or msg.lower().startswith("images uploaded"):
                        os.remove(img_path)
                        os.remove(meta_path)
                        logging.info(f"Uploaded and removed local {img_path} and {meta_path}")
                    else:
                        logging.error(f"Server did not acknowledge properly: {ack}")
                else:
                    logging.error(f"Upload failed for {img_path}: {response.text}")
            except Exception as e:
                logging.error(f"Error uploading {img_path}: {e}")
