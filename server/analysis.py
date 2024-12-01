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

        for photo in photos:
            server_manager = get_server_manager()
            user_upload_folder = os.path.join(server_manager.UPLOADED_IMAGES_PATH, username, mission_name)
            user_processed_folder = os.path.join(server_manager.PROCESSED_IMAGES_PATH, username, mission_name)
            os.makedirs(user_processed_folder, exist_ok=True)

            original_path = os.path.join(user_upload_folder, photo.filename)
            processed_path = os.path.join(user_processed_folder, photo.filename)

            # Run YOLOv11 inference
            photo_type = run_yolov11_inference(original_path, processed_path)

            # Organize the processed image into the type folder
            type_folder = os.path.join(user_processed_folder, photo_type)
            os.makedirs(type_folder, exist_ok=True)
            shutil.move(processed_path, os.path.join(type_folder, photo.filename))

            # Update the database
            photo.photo_type = photo_type
            photo.is_new_image = False

        session.commit()
    except Exception as e:
        logging.error(f"Error during analysis for mission {mission_name}: {e}")
    finally:
        session.close()

def run_yolov11_inference(input_path, output_path):
    """Placeholder function to run YOLOv11 inference."""
    # Simulate processing by copying the file and assigning a random type
    shutil.copy(input_path, output_path)
    photo_type = f"type_{random.randint(1,3)}"
    return photo_type

