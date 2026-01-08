from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from models import db
from models.user import User
from models.client import Client
from controllers.auth_controller import auth_bp
from controllers.client_controller import client_bp
from config import Config
from models.exercise import Exercise
from controllers.exercise_controller import exercise_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
    socketio = SocketIO(app, cors_allowed_origins=app.config['CORS_ORIGINS'])
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(exercise_bp)
     
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app, socketio

if __name__ == '__main__':
    app, socketio = create_app()
    socketio.run(app, debug=True, port=5000)
