# backend/controllers/trainee_session_controller.py

from flask import Blueprint, jsonify
from utils.jwt_utils import token_required
from models.session import Session, SessionClient
from models.program import ProgramExercise
from models.workout_log import WorkoutLog
from models.client import Client

trainee_session_bp = Blueprint('trainee_session', __name__)

@trainee_session_bp.route('/session', methods=['GET'])
@token_required
def get_trainee_active_session(current_user):  # ✅ ОБЯЗАТЕЛЬНО current_user КАК ПАРАМЕТР
    """Get trainee's active session data"""
    print(f"📡 Trainee user_id={current_user.id} requesting active session")
    
    if current_user.role != 'trainee':
        return jsonify({'error': 'Trainee only'}), 403
    
    # ✅ Найди Client ID по User ID
    client = Client.query.filter_by(user_id=current_user.id).first()
    
    if not client:
        print(f"❌ Client profile not found for user_id={current_user.id}")
        return jsonify({'error': 'Client profile not found'}), 404
    
    print(f"✅ Found client_id={client.id} for user_id={current_user.id}")
    
    # Find active session
    session_client = SessionClient.query.join(Session).filter(
        SessionClient.client_id == client.id,
        Session.status == 'active'
    ).first()
    
    if not session_client:
        print(f"❌ No active session found for client_id={client.id}")
        return jsonify({'error': 'No active session'}), 404
    
    session = session_client.session
    print(f"✅ Active session found: session_id={session.id}")
    
    # Get program exercises
    program_exercises = ProgramExercise.query.filter_by(
        program_id=session_client.program_id
    ).order_by(ProgramExercise.order).all()
    
    # Get current exercise
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
    
    # Get completed sets
    sets_completed = []
    if current_exercise_data:
        logs = WorkoutLog.query.filter_by(
            session_id=session.id,
            client_id=client.id,
            exercise_id=current_exercise_data['id']
        ).order_by(WorkoutLog.set_number).all()
        
        sets_completed = [{
            'set_number': log.set_number,
            'reps_completed': log.reps_completed,
            'weight_kg': log.weight_kg
        } for log in logs]
    
    response_data = {
        'session_id': session.id,
        'client_id': client.id,
        'trainer_name': session.trainer.full_name,
        'program_name': session_client.program.name,
        'status': session_client.status,
        'current_exercise': current_exercise_data,
        'sets_completed': sets_completed,
        'total_exercises': len(program_exercises),
        'exercises_completed': len(session_client.completed_exercises or []),
        'rest_time_remaining': session_client.rest_time_remaining or 0
    }
    
    print(f"✅ Returning session data")
    return jsonify(response_data), 200
