from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'student' or 'staff'
    is_first_login = db.Column(db.Boolean, default=True)
    name = db.Column(db.String(100), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    reg_number = db.Column(db.BigInteger, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Leave(db.Model):
    __tablename__ = 'leaves'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    reg_number = db.Column(db.BigInteger, nullable=False)
    dates = db.Column(db.Text, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending') # 'pending', 'approved', 'rejected'
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', backref=db.backref('leaves', lazy=True))
