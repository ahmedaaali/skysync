from ultralytics import YOLO
import requests

#TESTS RAN WITH JPG 

def downloaded_image():
    #Downloaded an image then ran it

    model_path = "C:\\Users\\bishe\\Downloads\\Computer Systems Engineering\\Computer Systems Engineering Year 4\\SYSC4907\\best.pt" #My path to the model
    model = YOLO(model_path)
    image_path = "C:\\Users\\bishe\\Downloads\\Computer Systems Engineering\\Computer Systems Engineering Year 4\SYSC4907\\crackimage.jpg" #My path to the test image

    results = model.predict(source=image_path, conf=0.5, save=True)
    print("Inference complete! Results saved in 'runs/detect/predict/'.")

def url_image():
    #Here I pass a URL so YOLO has to go the respective URL, download the image, then run it

    model_path = "C:\\Users\\bishe\\Downloads\\Computer Systems Engineering\\Computer Systems Engineering Year 4\\SYSC4907\\best.pt"
    model = YOLO(model_path)
    image_url = "https://www.thefloorcompany.ca/wp-content/uploads/2016/05/the-floor-company-ottawa-Concrete-Floor-Crack-Repair-Techniques-that-Work-.jpg"

    results = model.predict(source=image_url, conf=0.5, save=True)
    print("Inference complete! Results saved in 'runs/detect/predict/'.")

url_image()
