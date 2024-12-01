from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from auth import token_required
from models import Photo, Mission
import os
import logging

photos_blueprint = Blueprint('photos', __name__)

def get_server_manager():
    """Retrieve the server manager instance attached to the blueprint."""
    server_manager = getattr(photos_blueprint, 'server_manager', None)
    if not server_manager:
        raise RuntimeError("ServerManager not passed to photos_blueprint.")
    return server_manager

def get_database_session():
    """Retrieve a database session from the server manager."""
    server_manager = get_server_manager()
    Session = server_manager.get_database_session()
    return Session()

@photos_blueprint.route('/missions/<mission_name>/upload_images', methods=['POST'])
@token_required
def upload_images(current_user, mission_name):
    mission_name = request.form.get('mission_name')
    if not mission_name:
        return jsonify({"error": "Mission name is required"}), 400
    session = get_database_session()
    mission = session.query(Mission).filter_by(username=current_user, mission_name=mission_name).first()
    if not mission:
        session.close()
        return jsonify({"error": "Mission not found"}), 404

    if 'images' not in request.files:
        return jsonify({"error": "No images provided"}), 400

    images = request.files.getlist('images')
    server_manager = get_server_manager()
    user_upload_folder = os.path.join(server_manager.UPLOADED_IMAGES_PATH, current_user, mission_name)
    os.makedirs(user_upload_folder, exist_ok=True)

    try:
        for image in images:
            filename = secure_filename(image.filename)
            image_path = os.path.join(user_upload_folder, filename)
            image.save(image_path)
            photo = Photo(
                username=current_user,
                mission_id=mission.id,
                filename=filename,
                is_new_image=True
            )
            session.add(photo)

        session.commit()
        return jsonify({"message": "Images uploaded successfully"}), 200
    except Exception as e:
        logging.error(f"Error uploading images for mission {mission_name}: {e}")
        session.rollback()
        return jsonify({"error": "Failed to upload images"}), 500
    finally:
        session.close()
