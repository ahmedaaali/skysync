from flask import Blueprint, request, jsonify, send_from_directory
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from auth import token_required
import os
import logging
from models import Mission, Photo

missions_blueprint = Blueprint('missions', __name__)

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

BASE_PROCESSED_FOLDER = 'processed_images'

@missions_blueprint.route('/missions/create_mission', methods=['POST'])
@token_required
def create_mission(current_user):
    mission_name = request.json.get('mission_name')
    if not mission_name:
        return jsonify({"error": "Mission name is required"}), 400

    session = Session()

    # Check if the mission already exists for the user
    existing_mission = session.query(Mission).filter_by(username=current_user, mission_name=mission_name).first()
    if existing_mission:
        session.close()
        return jsonify({"error": "Mission with this name already exists"}), 400

    # Create a new mission
    mission = Mission(username=current_user, mission_name=mission_name, processed=False)
    session.add(mission)
    session.commit()

    # Create folder structure
    user_uploaded_folder = os.path.join("uploaded_images", current_user, mission_name)
    user_processed_folder = os.path.join("processed_images", current_user, mission_name)

    os.makedirs(user_uploaded_folder, exist_ok=True)
    os.makedirs(user_processed_folder, exist_ok=True)
    for photo_type in ["Crack", "Spall", "Corrosion"]:
        os.makedirs(os.path.join(user_processed_folder, photo_type), exist_ok=True)

    logging.info(f"Created folder structure for mission: {mission_name}")
    session.close()
    return jsonify({"message": "Mission created successfully"}), 200

@missions_blueprint.route('/missions/get_missions', methods=['GET'])
@token_required
def get_missions(current_user):
    session = Session()
    missions = session.query(Mission).filter_by(username=current_user).all()
    mission_names = [mission.mission_name for mission in missions]
    session.close()
    return jsonify(mission_names), 200

# --- Endpoint: Get Photo Types for a Mission ---
@missions_blueprint.route('/missions/<mission_name>/photo_types', methods=['GET'])
@token_required
def get_photo_types(current_user, mission_name):
    session = Session()
    try:
        # Fetch the mission
        mission = session.query(Mission).filter_by(username=current_user, mission_name=mission_name).first()
        if not mission:
            session.close()
            return jsonify({"error": "Mission not found"}), 404

        # Use mission.id to filter photos
        photo_types = session.query(Photo.photo_type).filter_by(
            mission_id=mission.id,
            is_new_image=False
        ).distinct().all()
        session.close()
        photo_types_list = [pt[0] for pt in photo_types if pt[0]]
        return jsonify(photo_types_list), 200
    except Exception as e:
        logging.error(f"Error fetching photo types for mission {mission_name}: {e}")
        session.close()
        return jsonify({"error": "Failed to fetch photo types"}), 500

# --- Endpoint: Get Photos for a Mission and Photo Type ---
@missions_blueprint.route('/missions/<mission_name>/photos', methods=['POST'])
@token_required
def get_new_photos(current_user, mission_name):
    """Fetch new photos by comparing client's cache.json with server's database."""
    session = Session()
    try:
        client_cache = request.json.get("cached_photos", {})
        if not isinstance(client_cache, dict):
            return jsonify({"error": "Invalid cache structure"}), 400

        # Check mission existence
        mission = session.query(Mission).filter_by(username=current_user, mission_name=mission_name).first()
        if not mission:
            return jsonify({"error": "Mission not found"}), 404

        # Get all photos for the mission from the database
        photos = session.query(Photo).filter_by(
            username=current_user,
            mission_id=mission.id
        ).all()

        # Organize photos by photo_type
        server_photos = {}
        for photo in photos:
            pt = photo.photo_type if photo.photo_type else "Unprocessed"
            server_photos.setdefault(pt, []).append(photo.filename)

        # Determine missing photos for each photo_type
        missing_photos = {}
        for pt, filenames in server_photos.items():
            client_filenames = client_cache.get(pt, [])
            missing = list(set(filenames) - set(client_filenames))
            missing_photos[pt] = missing

        return jsonify(missing_photos), 200

    except Exception as e:
        logging.error(f"Error fetching new photos for mission {mission_name}: {e}")
        return jsonify({"error": "Failed to fetch photos"}), 500
    finally:
        session.close()

# --- Endpoint: Download a Specific Photo ---
@missions_blueprint.route('/missions/<mission_name>/photos/<filename>', methods=['GET'])
@token_required
def download_photo(current_user, mission_name, filename):
    """Serve a specific photo to the client."""
    if filename == "cache.json":
        return jsonify({"error": "Photo not found"}), 404

    session = Session()
    try:
        mission = session.query(Mission).filter_by(username=current_user, mission_name=mission_name).first()
        if not mission:
            return jsonify({"error": "Mission not found"}), 404

        # Paths
        uploaded_folder = os.path.join("uploaded_images", current_user, mission_name)
        processed_folder = os.path.join("processed_images", current_user, mission_name)

        # Serve uploaded photos
        uploaded_path = os.path.join(uploaded_folder, filename)
        if os.path.exists(uploaded_path):
            return send_from_directory(uploaded_folder, filename)

        # Serve processed photos
        for photo_type in ["Crack", "Spall", "Corrosion"]:
            type_folder = os.path.join(processed_folder, photo_type)
            processed_path = os.path.join(type_folder, filename)
            if os.path.exists(processed_path):
                return send_from_directory(type_folder, filename)

        return jsonify({"error": "Photo not found"}), 404

    except Exception as e:
        logging.error(f"Error while serving photo {filename}: {e}")
        return jsonify({"error": "Failed to serve photo"}), 500
    finally:
        session.close()
