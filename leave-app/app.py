import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from models import db

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///local.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'default-secret-key-fallback')

db.init_app(app)
jwt = JWTManager(app)

from routes.auth import auth_bp
from routes.student import student_bp
from routes.staff import staff_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(student_bp, url_prefix='/api/student')
app.register_blueprint(staff_bp, url_prefix='/api/staff')

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return send_from_directory(app.template_folder, 'index.html')

@app.route('/<path:path>')
def serve_templates(path):
    if path.endswith('.html'):
        return send_from_directory(app.template_folder, path)
    
    file_path = os.path.join(app.template_folder, path + '.html')
    if os.path.exists(file_path):
        return send_from_directory(app.template_folder, path + '.html')
    
    return "Not found", 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
