import bcrypt
from app import app
from models import db, User

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def seed_db():
    with app.app_context():
        db.create_all()
        
        # Check if staff already exists
        if not User.query.filter_by(email='iam.rambirla@gmail.com').first():
            staff = User(
                email='iam.rambirla@gmail.com',
                password_hash=hash_password('ram@123'),
                role='staff',
                is_first_login=False
            )
            db.session.add(staff)
        
        # Add 3 students
        for i in range(64, 127):
            email = f'25ec{i:03d}@drngpit.ac.in'
            if not User.query.filter_by(email=email).first():
                student = User(
                    email=email,
                    password_hash=hash_password('stu123'),
                    role='student',
                    is_first_login=True
                )
                db.session.add(student)
                
        db.session.commit()
        print("Seeded successfully")

if __name__ == '__main__':
    seed_db()
