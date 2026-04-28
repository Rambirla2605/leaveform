import re
import bcrypt
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User, PasswordResetRequest

auth_bp = Blueprint('auth', __name__)

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email', '').lower()
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    student_pattern = r'^25ec\d{3}@drngpit\.ac\.in$'

    if not user:
        # Dynamically create user on first login with default credentials
        if email == "iam.rambirla@gmail.com" and password == "ram@123":
            user = User(
                email=email,
                password_hash=hash_password("ram@123"),
                role='staff',
                is_first_login=False
            )
            db.session.add(user)
            db.session.commit()
        elif re.match(student_pattern, email) and password == "stu123":
            user = User(
                email=email,
                password_hash=hash_password("stu123"),
                role='student',
                is_first_login=True
            )
            db.session.add(user)
            db.session.commit()
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    else:
        # Existing user, verify credentials
        if user.role == 'student' and not re.match(student_pattern, email):
            return jsonify({"error": "Invalid student email format"}), 400

        if not check_password(password, user.password_hash):
            return jsonify({"error": "Invalid credentials"}), 401

    if user.is_first_login and (password in ["stu123", "ram@123", "staff@123"]):
        return jsonify({"first_login": True, "token": create_access_token(identity=str(user.id))}), 200

    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        "token": access_token,
        "role": user.role,
        "first_login": user.is_first_login,
        "has_details": bool(user.name and user.reg_number)
    }), 200

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    data = request.json
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not new_password or not confirm_password:
        return jsonify({"error": "Passwords are required"}), 400

    if new_password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400

    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.password_hash = hash_password(new_password)
    user.is_first_login = False
    db.session.commit()

    return jsonify({"message": "Password updated successfully"}), 200

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email', '').lower()

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "No account found with this email"}), 404

    # Check if there is already a pending request
    existing_request = PasswordResetRequest.query.filter_by(user_id=user.id, status='pending').first()
    if existing_request:
        return jsonify({"error": "You already have a pending password reset request"}), 400

    new_request = PasswordResetRequest(user_id=user.id)
    db.session.add(new_request)
    db.session.commit()

    return jsonify({"message": "Password reset request sent to admin for approval"}), 200
