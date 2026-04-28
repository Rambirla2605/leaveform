from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Leave, PasswordResetRequest

staff_bp = Blueprint('staff', __name__)

def is_staff(user_id):
    user = User.query.get(user_id)
    return user and user.role == 'staff'

@staff_bp.route('/leaves', methods=['GET'])
@jwt_required()
def get_leaves():
    user_id = get_jwt_identity()
    if not is_staff(user_id):
        return jsonify({"error": "Unauthorized"}), 403

    status = request.args.get('status')
    search = request.args.get('search')
    date_filter = request.args.get('date')

    query = Leave.query

    if status and status != 'all':
        query = query.filter_by(status=status)
    
    if search:
        query = query.filter(Leave.name.ilike(f'%{search}%'))
        
    if date_filter:
        query = query.filter(Leave.dates.like(f'%{date_filter}%'))

    leaves = query.order_by(Leave.submitted_at.desc()).all()

    result = [{
        "id": l.id,
        "user_id": l.user_id,
        "name": l.name,
        "reg_number": l.reg_number,
        "date": l.dates,
        "reason": l.reason,
        "status": l.status,
        "submitted_at": l.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
        "reviewed_at": l.reviewed_at.strftime('%Y-%m-%d %H:%M:%S') if l.reviewed_at else None,
        "reviewed_by_name": l.reviewer.name if l.reviewer else None
    } for l in leaves]

    return jsonify(result), 200

@staff_bp.route('/leaves/<int:leave_id>/approve', methods=['PATCH'])
@jwt_required()
def approve_leave(leave_id):
    user_id = get_jwt_identity()
    if not is_staff(user_id):
        return jsonify({"error": "Unauthorized"}), 403

    leave = Leave.query.get(leave_id)
    if not leave:
        return jsonify({"error": "Leave not found"}), 404

    if leave.status != 'pending':
        return jsonify({"error": f"Leave already {leave.status}"}), 400

    leave.status = 'approved'
    leave.reviewed_at = datetime.utcnow()
    leave.reviewed_by = user_id
    db.session.commit()

    return jsonify({"message": "Leave approved"}), 200

@staff_bp.route('/leaves/<int:leave_id>/reject', methods=['PATCH'])
@jwt_required()
def reject_leave(leave_id):
    user_id = get_jwt_identity()
    if not is_staff(user_id):
        return jsonify({"error": "Unauthorized"}), 403

    leave = Leave.query.get(leave_id)
    if not leave:
        return jsonify({"error": "Leave not found"}), 404

    if leave.status != 'pending':
        return jsonify({"error": f"Leave already {leave.status}"}), 400

    leave.status = 'rejected'
    leave.reviewed_at = datetime.utcnow()
    leave.reviewed_by = user_id
    db.session.commit()

    return jsonify({"message": "Leave rejected"}), 200

@staff_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    user_id = get_jwt_identity()
    if not is_staff(user_id):
        return jsonify({"error": "Unauthorized"}), 403

    approved = Leave.query.filter_by(status='approved').count()
    pending = Leave.query.filter_by(status='pending').count()
    rejected = Leave.query.filter_by(status='rejected').count()
    
    today_str = datetime.utcnow().strftime('%Y-%m-%d')
    today_count = Leave.query.filter(Leave.dates.like(f'%{today_str}%')).count()

    return jsonify({
        "approved": approved,
        "pending": pending,
        "rejected": rejected,
        "today_count": today_count
    }), 200

@staff_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    user_id = get_jwt_identity()
    if not is_staff(user_id):
        return jsonify({"error": "Unauthorized"}), 403

    from_date_str = request.args.get('from')
    to_date_str = request.args.get('to')

    query = Leave.query.filter(Leave.status.in_(['approved', 'rejected']))

    if from_date_str:
        try:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            query = query.filter(Leave.date >= from_date)
        except ValueError:
            pass

    if to_date_str:
        try:
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
            query = query.filter(Leave.date <= to_date)
        except ValueError:
            pass

    leaves = query.order_by(Leave.reviewed_at.desc()).all()

    result = [{
        "id": l.id,
        "name": l.name,
        "reg_number": l.reg_number,
        "date": l.dates,
        "reason": l.reason,
        "status": l.status,
        "reviewed_at": l.reviewed_at.strftime('%Y-%m-%d %H:%M:%S') if l.reviewed_at else None,
        "reviewed_by_name": l.reviewer.name if l.reviewer else None
    } for l in leaves]

    return jsonify(result), 200

@staff_bp.route('/add-staff', methods=['POST'])
@jwt_required()
def add_staff():
    import bcrypt
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.email != 'iam.rambirla@gmail.com':
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    name = data.get('name')
    email = data.get('email')
    temp_password = data.get('temp_password')

    if not name or not email or not temp_password:
        return jsonify({"error": "Missing required fields"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    hashed = bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    new_staff = User(
        name=name,
        email=email,
        password_hash=hashed,
        role='staff',
        is_first_login=True
    )
    db.session.add(new_staff)
    db.session.commit()

    return jsonify({"message": "Staff added successfully"}), 201

@staff_bp.route('/list-staff', methods=['GET'])
@jwt_required()
def list_staff():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.email != 'iam.rambirla@gmail.com':
        return jsonify({"error": "Unauthorized"}), 403

    staff_members = User.query.filter_by(role='staff').all()
    result = [{
        "id": s.id,
        "name": s.name,
        "email": s.email,
        "created_at": s.created_at.strftime('%Y-%m-%d')
    } for s in staff_members]

    return jsonify(result), 200

from routes.auth import hash_password

@staff_bp.route('/password-requests', methods=['GET'])
@jwt_required()
def get_password_requests():
    user_id = get_jwt_identity()
    if not is_staff(user_id):
        return jsonify({"error": "Unauthorized"}), 403

    requests = PasswordResetRequest.query.filter_by(status='pending').order_by(PasswordResetRequest.requested_at.desc()).all()
    
    result = [{
        "id": req.id,
        "user_id": req.user_id,
        "user_email": req.user.email,
        "user_role": req.user.role,
        "requested_at": req.requested_at.strftime('%Y-%m-%d %H:%M:%S')
    } for req in requests]

    return jsonify(result), 200

@staff_bp.route('/password-requests/<int:req_id>/approve', methods=['POST'])
@jwt_required()
def approve_password_request(req_id):
    user_id = get_jwt_identity()
    if not is_staff(user_id):
        return jsonify({"error": "Unauthorized"}), 403

    req = PasswordResetRequest.query.get(req_id)
    if not req or req.status != 'pending':
        return jsonify({"error": "Request not found or already processed"}), 404

    # Approve request
    req.status = 'approved'
    req.resolved_at = datetime.utcnow()
    req.resolved_by = user_id

    # Reset user password to default and force password change on next login
    user = req.user
    default_password = 'staff@123' if user.role == 'staff' else 'stu123'
    user.password_hash = hash_password(default_password)
    user.is_first_login = True

    db.session.commit()

    return jsonify({"message": "Password reset approved"}), 200

@staff_bp.route('/password-requests/<int:req_id>/reject', methods=['POST'])
@jwt_required()
def reject_password_request(req_id):
    user_id = get_jwt_identity()
    if not is_staff(user_id):
        return jsonify({"error": "Unauthorized"}), 403

    req = PasswordResetRequest.query.get(req_id)
    if not req or req.status != 'pending':
        return jsonify({"error": "Request not found or already processed"}), 404

    # Reject request
    req.status = 'rejected'
    req.resolved_at = datetime.utcnow()
    req.resolved_by = user_id

    db.session.commit()

    return jsonify({"message": "Password reset rejected"}), 200
