# backend/app.py
import os
from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, leave_room, emit
from models import db
from config import Config
from threading import Timer
import time
from dotenv import load_dotenv
load_dotenv()


socketio = SocketIO()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
    socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')
    
    app.extensions['socketio'] = socketio
    
    # Import blueprints AFTER db.init_app()
    from controllers.auth_controller import auth_bp
    from controllers.client_controller import client_bp
    from controllers.exercise_controller import exercise_bp
    from controllers.program_controller import program_bp
    from controllers.session_controller import session_bp
    from controllers.trainer_history_controller import trainer_history_bp
    from controllers.trainee_history_controller import trainee_history_bp
    from controllers.trainer_analytics_controller import trainer_analytics_bp
    from controllers.trainee_analytics_controller import trainee_analytics_bp
    from controllers.trainee_session_controller import trainee_session_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(exercise_bp)
    app.register_blueprint(program_bp)
    app.register_blueprint(session_bp)
    app.register_blueprint(trainer_history_bp)
    app.register_blueprint(trainee_history_bp)
    app.register_blueprint(trainer_analytics_bp)
    app.register_blueprint(trainee_analytics_bp)
    app.register_blueprint(trainee_session_bp, url_prefix='/api/trainee')
     
    with app.app_context():
        db.create_all()
    
    return app, socketio

if __name__ == '__main__':
    app, socketio = create_app()


    print("📋 Registered routes:")
    for rule in app.url_map.iter_rules():
        if 'trainee' in rule.rule:
            print(f"  {rule.methods} {rule.rule} -> {rule.endpoint}")

            
def register_socket_handlers():
    @socketio.on('connect')
    def handle_connect():
        print(f'✅ Client connected: {request.sid}')

    @socketio.on('trainee_connect')
    def handle_trainee_connect(data):
        """Trainee подключается к своей персональной комнате"""
        trainee_id = data.get('trainee_id')
        
        if not trainee_id:
            print("⚠️ No trainee_id provided")
            return
        
        room = f'trainee_{trainee_id}'
        join_room(room)
        print(f"✅ Trainee {trainee_id} joined personal room: {room}")

    @socketio.on('join_session')
    def on_join_session(data):
        session_id = data.get('session_id')
        if not session_id:
            return
        room = f"session_{session_id}"
        join_room(room)
        print(f'📍 Trainer joined room: {room}')

    @socketio.on('trainee_join_session')
    def handle_trainee_join(data):
        """Allow trainee to join their own session room"""
        session_id = data.get('session_id')
        trainee_id = data.get('trainee_id')
        
        print(f"🔍 Trainee {trainee_id} attempting to join session {session_id}")
        
        from models.session import SessionClient
        session_client = SessionClient.query.filter_by(
            session_id=session_id,
            client_id=trainee_id
        ).first()
        
        if not session_client:
            print(f"⚠️ Trainee {trainee_id} not authorized for session {session_id}")
            emit('error', {'message': 'Not authorized'})
            return
        
        room = f'session_{session_id}'
        join_room(room)
        print(f"✅ Trainee {trainee_id} joined session room: {room}")
        
        from models.program import ProgramExercise
        from models.workout_log import WorkoutLog
        
        program_exercises = ProgramExercise.query.filter_by(
            program_id=session_client.program_id
        ).order_by(ProgramExercise.order).all()
        
        current_exercise_data = None
        if session_client.current_exercise_index < len(program_exercises):
            current_pe = program_exercises[session_client.current_exercise_index]
            exercise = current_pe.exercise
            
            current_exercise_data = {
                'id': exercise.id,
                'name': exercise.name,
                'sets': current_pe.sets,
                'reps': current_pe.reps,
                'weight_kg': current_pe.weight_kg,
                'rest_seconds': current_pe.rest_seconds
            }
        
        sets_completed = []
        if current_exercise_data:
            logs = WorkoutLog.query.filter_by(
                session_id=session_id,
                client_id=trainee_id,
                exercise_id=current_exercise_data['id']
            ).order_by(WorkoutLog.set_number).all()
            
            sets_completed = [{
                'set_number': log.set_number,
                'reps_completed': log.reps_completed,
                'weight_kg': log.weight_kg
            } for log in logs]
        
        emit('session_state', {
            'session_id': session_id,
            'trainee_data': {
                'current_exercise': current_exercise_data,
                'sets_completed': sets_completed,
                'status': session_client.status,
                'rest_time_remaining': session_client.rest_time_remaining
            }
        })

    @socketio.on('leave_session')
    def on_leave_session(data):
        session_id = data.get('session_id')
        if not session_id:
            return
        room = f"session_{session_id}"
        leave_room(room)
        print(f'📤 Client left room: {room}')

    @socketio.on('disconnect')
    def handle_disconnect():
        print(f'🔌 Client disconnected: {request.sid}')

    socketio.run(app, debug=True, port=5000)
# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)
#
#     # Initialize extensions
#     db.init_app(app)
#     CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
#     socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')
#
#     app.extensions['socketio'] = socketio
#
#     # Import blueprints AFTER db.init_app()
#     from controllers.auth_controller import auth_bp
#     from controllers.client_controller import client_bp
#     from controllers.exercise_controller import exercise_bp
#     from controllers.program_controller import program_bp
#     from controllers.session_controller import session_bp
#     from controllers.trainer_history_controller import trainer_history_bp
#     from controllers.trainee_history_controller import trainee_history_bp
#     from controllers.trainer_analytics_controller import trainer_analytics_bp
#     from controllers.trainee_analytics_controller import trainee_analytics_bp
#     from controllers.trainee_session_controller import trainee_session_bp
#
#     app.register_blueprint(auth_bp)
#     app.register_blueprint(client_bp)
#     app.register_blueprint(exercise_bp)
#     app.register_blueprint(program_bp)
#     app.register_blueprint(session_bp)
#     app.register_blueprint(trainer_history_bp)
#     app.register_blueprint(trainee_history_bp)
#     app.register_blueprint(trainer_analytics_bp)
#     app.register_blueprint(trainee_analytics_bp)
#     app.register_blueprint(trainee_session_bp, url_prefix='/api/trainee')
#
#     with app.app_context():
#         db.create_all()
#
#     register_socket_handlers()
#
#     return app, socketio
#
# if __name__ == '__main__':
#     app, socketio = create_app()
#
#
#     print("📋 Registered routes:")
#     for rule in app.url_map.iter_rules():
#         if 'trainee' in rule.rule:
#             print(f"  {rule.methods} {rule.rule} -> {rule.endpoint}")
#
#
#     if __name__ == "__main__":
#         allow = os.getenv("ALLOW_UNSAFE_WERKZEUG", "1") == "1"
#         socketio.run(app, host="127.0.0.1", port=5000, debug=True, allow_unsafe_werkzeug=True)
