import torch
from ultralytics import YOLO
import os

model_path = "/home/student/SkySync/300_Epochs/runs/detect/train/weights/best.pt"

model = YOLO(model_path)

export_dir = "/home/student/SkySync/exported_model"
export_path = os.path.join(export_dir, "300_epochs.pt")

torch.save(model.model.state_dict(), export_path)

print(f"Model exported to {export_path}")
