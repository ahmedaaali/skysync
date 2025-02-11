from flask import Blueprint, request, jsonify
from auth import token_required
from models import User
import datetime
import logging

drone_blueprint = Blueprint('drone', __name__)

def get_server_manager():
    server_manager = getattr(drone_blueprint, 'server_manager', None)
    if not server_manager:
        raise RuntimeError("ServerManager not passed to drone_blueprint.")
    return server_manager

def get_database_session():
    return get_server_manager().get_database_session()()

@drone_blueprint.route('/drone/heartbeat', methods=['POST'])
@token_required
def drone_heartbeat(current_user):
    token_data = getattr(request, 'token_data', None)  # If you store data in request

    session = get_database_session()
    try:
        user = session.query(User).filter_by(username=current_user).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        user.drone_last_heartbeat = datetime.datetime.utcnow()
        session.commit()
        return jsonify({"message": "Heartbeat received"}), 200
    except Exception as e:
        logging.error(f"Error in drone_heartbeat: {e}")
        session.rollback()
        return jsonify({"error": "Failed to update drone heartbeat"}), 500
    finally:
        session.close()

@drone_blueprint.route('/drone/status', methods=['GET'])
@token_required
def drone_status(current_user):
    """
    Check if the drone is online.
    """
    session = get_database_session()
    try:
        user = session.query(User).filter_by(username=current_user).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        if user.drone_last_heartbeat:
            delta = datetime.datetime.utcnow() - user.drone_last_heartbeat
            if delta.total_seconds() < 30:
                return jsonify({"drone_online": True}), 200
        return jsonify({"drone_online": False}), 200
    except Exception as e:
        logging.error(f"Error checking drone status: {e}")
        return jsonify({"error": "Failed to check drone status"}), 500
    finally:
        session.close()
