from IPython import display
import sys
import torch
import os
from ultralytics import YOLO
from roboflow import Roboflow
import glob
from IPython.display import Image as IPyImage
import shutil

HOME = "/home/student/SkySync"

os.makedirs(f"{HOME}/datasets", exist_ok=True)
os.chdir(f"{HOME}/datasets")

rf = Roboflow(api_key="Hf2n7z323KLGcAPVfDRM")

# Download datasets
project1 = rf.workspace("ta-8behn").project("crack-detection-ypnwo") # This points to the specific project in roboflow
version1 = project1.version(3) # Version means the dataset version that we are pulling from, some projects have many datasets so I just pull the latest one
dataset1 = version1.download("yolov11") # This is the YOLO version we are using, in this case we are using YOLO V11

#project2 = rf.workspace("bridgetest01").project("bridge_detection_01")
#version2 = project2.version(5)
#dataset2 = version2.download("yolov11")

project3 = rf.workspace("xplodingdog").project("dawgsurfacecrackssag")
version3 = project3.version(1)
dataset3 = version3.download("yolov11")

project4 = rf.workspace("engr423").project("bridge-drone")
version4 = project4.version(18)
dataset4 = version4.download("yolov11")

project5 = rf.workspace("project-ya1zp").project("bridge-crack-detection-pagfb")
version5 = project5.version(15)
dataset5 = version5.download("yolov11")

# Merging all datasets: Move images and labels to one common folder
os.makedirs(f"{HOME}/datasets/combined/images", exist_ok=True)
os.makedirs(f"{HOME}/datasets/combined/labels", exist_ok=True)

# Combine the datasets we are using into one single dataset by copying from their respective folders to the combined folder
datasets = [dataset1, dataset3, dataset4, dataset5]
for dataset in datasets:
    images_src = os.path.join(dataset.location, "train", "images")
    labels_src = os.path.join(dataset.location, "train", "labels")
    images_dest = f"{HOME}/datasets/combined/images/"
    labels_dest = f"{HOME}/datasets/combined/labels/"

    # Copy images and labels from each dataset to the combined folder
    for img_file in glob.glob(f"{images_src}/*"):
        shutil.copy(img_file, images_dest)
    for lbl_file in glob.glob(f"{labels_src}/*"):
        shutil.copy(lbl_file, labels_dest)

# Print the total number of training images we are using to train the model by getting the length of the combined folder
total_images = len(glob.glob(f"{HOME}/datasets/combined/images/*"))
print(f"TOTAL NUMBER OF TRAINING IMAGES: {total_images}")

# Create a new data.yaml file for the combined dataset
# 'train' keyword specifies what we are training the model with
# 'val' keyword specifies what we are validating the model with, in this case the same set, in the future we choose our own set from drone to validate the model
# 'nc' keyword is the number of classes we are training on, in this case only 1 class which is the cracks
# 'names' keyword is the name of the class we are training, so we train 1 class, named crack

data_yaml_path = f"{HOME}/datasets/combined/data.yaml"
with open(data_yaml_path, "w") as file:
    file.write(f"""
    train: {HOME}/datasets/combined/images
    val: {HOME}/datasets/combined/images

    nc: 1
    names: ['crack']
    """)

os.chdir(HOME)
if torch.cuda.is_available(): # This checks if the GPU is available on the machine, I have this to just prove whether the GPU is actually the one being used
    print("Running on Graphics Processing Unit")
    model = YOLO('yolo11s.pt') # This initializes the YOLO model we will use
    model.train(data=data_yaml_path, epochs=300, imgsz=640, plots=True, device=0)  # This line launches the training
    # 'epochs' keyword means how many times we go over each image, so we train the model 10 times per image, basically analyzes the images 10 times each
    # 'imgsz' keyword is the 640x640 image size
    # 'plots=True' keyword basically outputs plots that show results of the training like loss, precision, recall, mean average precision, confusion matrix
    # 'device=0' keyword is for the first GPU, so train using the first GPU on the machine that you locate

else: # If we reach else block that means the machine is not recognizing the GPU, or maybe my if statement is dumb
    print("Running on CPU")
    # Now we could technically train, but its a CPU so very slow, but for now lets not do that
    sys.exit() # Exit the program

    # model = YOLO('yolo11s.pt')
    # model.train(data=data_yaml_path, epochs=10, imgsz=640, plots=True, device='cpu') # This line launches the training but on a CPU

# Display the confusion matrix
conf_matrix_path = f"{HOME}/runs/detect/train/confusion_matrix.png"
if os.path.exists(conf_matrix_path):
    display(IPyImage(filename=conf_matrix_path, width=600)) # Displays the confusion matrix, if you don't understand it quick google search can help

# Make predictions using the trained model
model.predict(source=f"{dataset1.location}/test/images", conf=0.75, save=True) # conf=0.75 means the model needs to be at least 75% confident (sure) that the crack is present - we can play around with this
