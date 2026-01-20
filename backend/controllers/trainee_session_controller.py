from flask import Blueprint, jsonify, request
from utils.jwt_utils import token_required
from models.session import Session, SessionClient
from models.program import ProgramExercise
from models.workout_log import WorkoutLog
from models.client import Client

trainee_session_bp = Blueprint('trainee_session', __name__)

@trainee_session_bp.route('/session', methods=['GET'])
@token_required
def get_trainee_active_session():
    user_id = request.user_id
    

    from models.user import User
    client = Client.query.filter_by(user_id=user_id).first()
    
    if not client:
        return jsonify({'error': 'Client profile not found'}), 404

    session_client = SessionClient.query.join(Session).filter(
        SessionClient.client_id == client.id,
        Session.status == 'active'
    ).order_by(Session.id.desc()).first()
    
    if not session_client:
        return jsonify({'error': 'No active session found'}), 404
    
    session = session_client.session
    
    program_exercises = ProgramExercise.query.filter_by(
        program_id=session_client.program_id
    ).order_by(ProgramExercise.id).all()
    
    total_exercises = len(program_exercises)
    current_exercise_data = None
    sets_completed = []

    if session_client.current_exercise_index < total_exercises:
        current_pe = program_exercises[session_client.current_exercise_index]
        exercise = current_pe.exercise
        
        current_exercise_data = {
            'id': exercise.id,
            'name': exercise.name,
            'sets': current_pe.sets,
            'reps': current_pe.reps,
            'weight_kg': current_pe.weight_kg,
            'rest_seconds': current_pe.rest_seconds,
            'description': exercise.description
        }
        
        logs = WorkoutLog.query.filter_by(
            session_id=session.id,
            client_id=client.id,
            exercise_id=exercise.id
        ).order_by(WorkoutLog.set_number).all()
        
        sets_completed = [{
            'set_number': log.set_number,
            'reps_completed': log.reps_completed,
            'weight_kg': log.weight_kg
        } for log in logs]

    completed_list = session_client.completed_exercises or []
    
    response_data = {
        'session_id': session.id,
        'client_id': client.id,
        'trainer_name': session.trainer.full_name,
        'program_name': session_client.program.name,
        'status': session_client.status,
        'current_exercise': current_exercise_data,
        'sets_completed': sets_completed,
        'total_exercises': total_exercises,
        'exercises_completed': len(completed_list),
        'rest_time_remaining': session_client.rest_time_remaining or 0
    }
    
    return jsonify(response_data), 200