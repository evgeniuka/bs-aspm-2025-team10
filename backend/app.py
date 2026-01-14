from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from models import db
from controllers.auth_controller import auth_bp
from controllers.client_controller import client_bp
from controllers.exercise_controller import exercise_bp
from controllers.program_controller import program_bp
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    app.extensions['socketio'] = socketio
    app.register_blueprint(auth_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(exercise_bp)
    app.register_blueprint(program_bp)
    
    from controllers.session_controller import session_bp
    app.register_blueprint(session_bp)
     
    with app.app_context():
        db.create_all()
    
    return app, socketio

if __name__ == '__main__':
    app, socketio = create_app()
    
    from flask import request
    from flask_socketio import join_room, leave_room
    from models.session import Session
    
    @socketio.on('connect')
    def handle_connect():
        print(f'Client connected: {request.sid}')

    @socketio.on('join_session')
    def on_join_session(data):
        session_id = data.get('session_id')
        if not session_id:
            return
        room = f"session_{session_id}"
        join_room(room)
        print(f'Client joined room: {room}')

    @socketio.on('leave_session')
    def on_leave_session(data):
        session_id = data.get('session_id')
        if not session_id:
            return
        room = f"session_{session_id}"
        leave_room(room)
        print(f'Client left room: {room}')

    @socketio.on('disconnect')
    def handle_disconnect():
        print(f'Client disconnected: {request.sid}')
    
    socketio.run(app, debug=True, port=5000)