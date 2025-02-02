from flask import Blueprint, request, jsonify, current_app
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import bcrypt
import os
import jwt
import datetime
import logging
from functools import wraps
from models import User, Admin

auth_blueprint = Blueprint('auth', __name__)

def get_server_manager():
    """Retrieve the server manager instance attached to the blueprint."""
    server_manager = getattr(auth_blueprint, 'server_manager', None)
    if not server_manager:
        raise RuntimeError("ServerManager not passed to auth_blueprint.")
    return server_manager

def get_database_session():
    """Retrieve a database session from the server manager."""
    server_manager = get_server_manager()
    Session = server_manager.get_database_session()
    return Session()

def token_required(f):
    """Decorator to check for a valid JWT token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'error': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['username']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@auth_blueprint.route('/register', methods=['POST'])
def register_user():
    """Endpoint to register a new user."""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    # role = data.get('role', 'client')  # Default role is 'client'

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    if len(username) < 3 or len(password) < 6:
        return jsonify({"error": "Invalid username or password length."}), 400

    session = get_database_session()
    try:
        if session.query(User).filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 409

        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        new_user = User(username=username, password_hash=password_hash.decode('utf-8'))
        session.add(new_user)
        session.commit()
        logging.info(f"User {username} registered successfully.")
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        logging.error(f"Registration error: {e}")
        session.rollback()
        return jsonify({"error": "Registration failed"}), 500
    finally:
        session.close()

@auth_blueprint.route('/login', methods=['POST'])
def login_user():
    """Endpoint to authenticate a user and return a JWT token."""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    session = get_database_session()
    try:
        user = session.query(User).filter_by(username=username).first()
        if user:
            logging.info(f"User found: {username}")
            if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                token = jwt.encode({
                    'username': username,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
                }, current_app.config['SECRET_KEY'], algorithm="HS256")
                logging.info(f"Login successful for user: {username}")
                return jsonify({"message": "Login successful", "token": token}), 200
            else:
                logging.warning(f"Invalid password for user: {username}")
                return jsonify({"error": "Invalid credentials"}), 401
        else:
            logging.warning(f"User not found: {username}")
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        logging.error(f"Login error for user {username}: {e}")
        return jsonify({"error": "An error occurred during login"}), 500
    finally:
        session.close()

@auth_blueprint.route('/registeradmin', methods=['POST'])
def register_admin():
    """Endpoint to register a new user."""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    # role = data.get('role', 'admin') 

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    if len(username) < 3 or len(password) < 6:
        return jsonify({"error": "Invalid username or password length."}), 400

    session = get_database_session()
    try:
        if session.query(Admin).filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 409

        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        new_user = Admin(username=username, password_hash=password_hash.decode('utf-8'))
        session.add(new_user)
        session.commit()
        logging.info(f"User {username} registered successfully.")
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        logging.error(f"Registration error: {e}")
        session.rollback()
        return jsonify({"error": "Registration failed"}), 500
    finally:
        session.close()

@auth_blueprint.route('/loginadmin', methods=['POST'])
def login_admin():
    """Endpoint to authenticate a user and return a JWT token."""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    session = get_database_session()
    try:
        user = session.query(Admin).filter_by(username=username).first()
        if user:
            logging.info(f"User found: {username}")
            if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                token = jwt.encode({
                    'username': username,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
                }, current_app.config['SECRET_KEY'], algorithm="HS256")
                logging.info(f"Login successful for user: {username}")
                return jsonify({"message": "Login successful", "token": token}), 200
            else:
                logging.warning(f"Invalid password for user: {username}")
                return jsonify({"error": "Invalid credentials"}), 401
        else:
            logging.warning(f"User not found: {username}")
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        logging.error(f"Login error for user {username}: {e}")
        return jsonify({"error": "An error occurred during login"}), 500
    finally:
        session.close()

@auth_blueprint.route('/change_password', methods=['POST'])
@token_required
def change_password(current_user):
    """
    Endpoint to handle changing the password for a user.
    Requires a valid JWT token.
    """
    data = request.get_json()
    old_password = data.get('old_password', '').strip()
    new_password = data.get('new_password', '').strip()

    # Validate input
    if not old_password or not new_password:
        return jsonify({"error": "Old and new passwords are required."}), 400

    if len(new_password) < 8:
        return jsonify({"error": "New password must be at least 8 characters long."}), 400

    session = get_database_session()
    try:
        # Find the user by username
        user = session.query(User).filter_by(username=current_user).first()
        if not user:
            return jsonify({"error": "User not found."}), 404

        # Verify the old password
        if not bcrypt.checkpw(old_password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return jsonify({"error": "Old password is incorrect."}), 401

        # Hash the new password
        new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        user.password_hash = new_password_hash.decode('utf-8')

        # Commit changes
        session.commit()
        return jsonify({"message": "Password changed successfully."}), 200
    except Exception as e:
        logging.error(f"Change password error for user {current_user}: {e}")
        session.rollback()
        return jsonify({"error": "An error occurred while changing the password."}), 500
    finally:
        session.close()
