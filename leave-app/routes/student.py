from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Leave

student_bp = Blueprint('student', __name__)

@student_bp.route('/details', methods=['POST'])
@jwt_required()
def details():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role != 'student':
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    name = data.get('name')
    department = data.get('department')
    reg_number = data.get('reg_number')

    if not name or not department or not reg_number:
        return jsonify({"error": "All fields are required"}), 400

    try:
        reg_number = int(reg_number)
        if reg_number < 710725106064 or reg_number > 710725106126:
            return jsonify({"error": "Invalid register number range"}), 400
    except ValueError:
        return jsonify({"error": "Register number must be an integer"}), 400

    user.name = name.upper()
    user.department = department.upper()
    user.reg_number = reg_number
    db.session.commit()

    return jsonify({"message": "Details updated successfully"}), 200

@student_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"name": user.name, "reg_number": user.reg_number}), 200

@student_bp.route('/leave', methods=['POST'])
@jwt_required()
def submit_leave():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or user.role != 'student':
        return jsonify({"error": "Unauthorized"}), 403

    if not user.name or not user.reg_number:
        return jsonify({"error": "Student details not filled"}), 400

    data = request.json
    dates = data.get('dates', [])
    reason = data.get('reason')

    if not dates or not reason:
        return jsonify({"error": "Dates and reason are required"}), 400

    # Check for duplicate dates
    existing_leaves = Leave.query.filter_by(user_id=user.id).all()
    existing_dates = set()
    for el in existing_leaves:
        existing_dates.update(el.dates.split(', '))
    
    for date_str in dates:
        if date_str in existing_dates:
            return jsonify({"error": f"You have already requested leave for {date_str}"}), 400

    dates_string = ", ".join(sorted(dates))

    leave = Leave(
        user_id=user.id,
        name=user.name,
        reg_number=user.reg_number,
        dates=dates_string,
        reason=reason,
        status='pending'
    )
    db.session.add(leave)
    db.session.commit()

    return jsonify({"submitted": 1}), 200

@student_bp.route('/leaves', methods=['GET'])
@jwt_required()
def get_leaves():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or user.role != 'student':
        return jsonify({"error": "Unauthorized"}), 403

    leaves = Leave.query.filter_by(user_id=user.id).order_by(Leave.submitted_at.desc()).all()
    
    result = [{
        "id": l.id,
        "date": l.dates,
        "reason": l.reason,
        "status": l.status,
        "submitted_at": l.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
    } for l in leaves]

    return jsonify(result), 200
