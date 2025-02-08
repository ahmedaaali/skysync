from flask import Blueprint, request, jsonify
from auth import token_required
from celery import Celery
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
import shutil
import random
import logging
from models import Photo, Mission
from ultralytics import YOLO


analysis_blueprint = Blueprint('analysis', __name__)

# Configure Celery with result backend
celery = Celery(
    __name__,
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)
celery.conf.update(
    broker_connection_retry_on_startup=True
)

def get_server_manager():
    """Retrieve the server manager instance attached to the blueprint."""
    server_manager = getattr(analysis_blueprint, 'server_manager', None)
    if not server_manager:
        raise RuntimeError("ServerManager not passed to analysis_blueprint.")
    return server_manager

def get_database_session():
    """Retrieve a database session from the server manager."""
    server_manager = get_server_manager()
    Session = server_manager.get_database_session()
    return Session()

@analysis_blueprint.route('/analyze', methods=['POST'])
@token_required
def analyze_photos(current_user):
    """Endpoint to trigger analysis of photos."""
    data = request.get_json()
    mission_name = data.get('mission_name')

    if not mission_name:
        return jsonify({"error": "Mission name is required"}), 400

    run_analysis.delay(current_user.username, mission_name)
    return jsonify({"message": "Analysis started"}), 200

@celery.task
def run_analysis(username, mission_name):
    """Background task to analyze photos."""
    session = get_database_session()
    try:
        mission = session.query(Mission).filter_by(username=username, mission_name=mission_name).first()
        if not mission:
            logging.error(f"Mission {mission_name} not found for user {username}")
            session.close()
            return

        photos = session.query(Photo).filter_by(
            mission_id=mission.id,
            is_new_image=True
        ).all()

        if not photos:
            return

        server_manager = get_server_manager()
        user_upload_folder = os.path.join(server_manager.UPLOADED_IMAGES_PATH, username, mission_name)
        user_processed_folder = os.path.join(server_manager.PROCESSED_IMAGES_PATH, username, mission_name)
        os.makedirs(user_processed_folder, exist_ok=True)

        model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'machine_learning', 'best.pt'))
        #Run YOLOv11 inference on the folder - this returns a dictionary with the dict key being the filename and the dict value being "crack" or "unknown"
        results = run_yolov11_inference_on_folder(user_upload_folder, user_processed_folder, model_path)

        # Update database with results
        for photo_filename, category in results.items():
            photo = session.query(Photo).filter_by(mission_id=mission.id, filename=photo_filename).first()
            if photo:
                photo.photo_type = category  # Save "crack" or "unknown"
                photo.is_new_image = False

        # Organize the processed image into the type folder
        #type_folder = os.path.join(user_processed_folder, photo_type)
        #os.makedirs(type_folder, exist_ok=True)
        #shutil.move(processed_path, os.path.join(type_folder, photo.filename))

        session.commit()
    except Exception as e:
        logging.error(f"Error during analysis for mission {mission_name}: {e}")
    finally:
        session.close()


def run_yolov11_inference_on_folder(input_folder, output_folder, model_path):
    """
    Run YOLOv11 inference on all images in a folder and classify images as "crack" or "unknown" organized in a dict
    """ 

    output_dir_parent = os.path.dirname(output_folder) #Grab output directory's parent name to pass it to the predict call -> "path\to\skysync" becomes now "path\to"
    output_dir_child = os.path.basename(output_folder) #Grab the output directory's child name to pass it to the predict call -> "path\to\skysync" becomes now "skysync"

    # Remove the output folder to not mistakenly create duplicates 
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    
    #Load the model from its path
    model = YOLO(model_path)

    #Now we run our inference on all images in the folder
    results = model.predict(
        source=input_folder,  #Input folder path
        conf=0.393,             #Confidence threshold - anything that is 39.3% or more sure that its a crack will be classified
        save=True,            #Save predictions
        project=output_dir_parent, #Gives the parent directory as the project paramerter to know where to save the results
        name=output_dir_child #Gives the name of the folder to create which is used to store the results -> so now it knows to go the parent dir, ok now lets create this child folder to save results in it
    )

    image_categories = {}

    for result in results:
        #Categorize by "crack" if a detection exists else its "unknown"
        if len(result.boxes) > 0:
            category = "crack" 
        else:
            category = "unknown"

        #Extract filename of the specific image from its path
        photo_filename = result.path.split(os.sep)[-1]

        # Store the result in the dictionary
        image_categories[photo_filename] = category

    return image_categories


