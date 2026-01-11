from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

from config import Config
from models import db
from controllers.auth_controller import auth_bp
from controllers.client_controller import client_bp
from controllers.exercise_controller import exercise_bp


socketio = SocketIO()  # create once, init later


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    origins = app.config.get("CORS_ORIGINS", "*")
    CORS(app, resources={r"/api/*": {"origins": origins}})
    socketio.init_app(app, cors_allowed_origins=origins)

    app.register_blueprint(auth_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(exercise_bp)

    return app, socketio


if __name__ == "__main__":
    app, _socketio = create_app()
    _socketio.run(app, debug=True, port=5000)
