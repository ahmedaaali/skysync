# Import necessary packages
from IPython import display
import sys
import torch
import os
from ultralytics import YOLO
from roboflow import Roboflow
import glob
from IPython.display import Image as IPyImage
import shutil

# Define HOME directory
HOME = "/home/student/SkySync/Jan10"

# Define Roboflow API key
API = "Hf2n7z323KLGcAPVfDRM"

# Ensure datasets directory exists
os.makedirs(f"{HOME}/datasets", exist_ok=True)
os.chdir(f"{HOME}/datasets")

# Setup Roboflow for downloading datasets using the API key
rf = Roboflow(api_key=API)

# Add the new datasets
new_datasets = []

# Dataset 1
project1 = rf.workspace("nguyen-thi-thuy-hien-3ea5t").project("bac_hien_crack_concrete_2024")
version1 = project1.version(14)
new_dataset1 = version1.download("yolov11")
new_datasets.append(new_dataset1)

# Dataset 2
project2 = rf.workspace("enim-sppgm").project("cracks-detection-xtbn8")
version2 = project2.version(9)
new_dataset2 = version2.download("yolov11")
new_datasets.append(new_dataset2)

# Dataset 3
project3 = rf.workspace("yolo-wtdwv").project("asdf2")
version3 = project3.version(1)
new_dataset3 = version3.download("yolov11")
new_datasets.append(new_dataset3)

# Dataset 4
project4 = rf.workspace("woxsen").project("crack-detection-265sq")
version4 = project4.version(1)
new_dataset4 = version4.download("yolov11")
new_datasets.append(new_dataset4)

# Additional datasets
project5 = rf.workspace("ta-8behn").project("crack-detection-ypnwo")
version5 = project5.version(3)
new_dataset5 = version5.download("yolov11")
new_datasets.append(new_dataset5)

project6 = rf.workspace("xplodingdog").project("dawgsurfacecrackssag")
version6 = project6.version(1)
new_dataset6 = version6.download("yolov11")
new_datasets.append(new_dataset6)

project7 = rf.workspace("engr423").project("bridge-drone")
version7 = project7.version(18)
new_dataset7 = version7.download("yolov11")
new_datasets.append(new_dataset7)

project8 = rf.workspace("project-ya1zp").project("bridge-crack-detection-pagfb")
version8 = project8.version(15)
new_dataset8 = version8.download("yolov11")
new_datasets.append(new_dataset8)

# Create a new data.yaml file with individual entries for train and val paths
data_yaml_path = f"{HOME}/datasets/data.yaml"

with open(data_yaml_path, "w") as file:
    file.write("train:\n")
    for dataset in new_datasets:
        train_path = f"{dataset.location}/train/images"
        file.write(f"  - {train_path}\n")
    
    file.write("\nval:\n")
    for dataset in new_datasets:
        val_path = f"{dataset.location}/valid/images"
        if os.path.exists(val_path):  # Check if the valid folder exists
            file.write(f"  - {val_path}\n")
        else:
            print(f"Validation folder not found for {dataset.location}, using train folder instead.")
            file.write(f"  - {dataset.location}/train/images\n")  # Use train as fallback

    file.write("\nnc: 1\nnames: ['crack']\n")

print(f"Data YAML created at: {data_yaml_path}")


# Training the model
os.chdir(HOME)

if torch.cuda.is_available():
    print("Running on Graphics Processing Unit")
    model = YOLO('yolo11s.pt')  # Initialize the YOLO model
    model.train(data=data_yaml_path, epochs=400, imgsz=640, plots=True, device=0)  # Train the model
else:
    print("Running on CPU")
    sys.exit()  # Exit the program if GPU is not available

# Make predictions using the trained model
model.predict(source=f"{new_datasets[0].location}/test/images", conf=0.75, save=True)
