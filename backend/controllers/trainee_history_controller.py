from flask import Blueprint, request, jsonify
from models import db
from models.session import Session, SessionClient
from models.program import Program, ProgramExercise
from models.workout_log import WorkoutLog
from models.client import Client
from utils.jwt_utils import token_required

trainee_history_bp = Blueprint('trainee_history', __name__, url_prefix='/api/trainee')

@trainee_history_bp.route('/sessions', methods=['GET'])
@token_required
def get_trainee_sessions():
    """Get all sessions for authenticated trainee"""
    user_id = request.user_id
    
    client = Client.query.filter_by(user_id=user_id).first()
    if not client:
        return jsonify({'error': 'Client profile not found'}), 404
    
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    

    sessions_query = Session.query.join(SessionClient).filter(
        SessionClient.client_id == client.id,
        Session.status == 'completed'
    ).order_by(Session.start_time.desc())
    
    total = sessions_query.count()
    sessions = sessions_query.limit(limit).offset(offset).all()
    
    sessions_data = []
    for session in sessions:
        sc = SessionClient.query.filter_by(
            session_id=session.id,
            client_id=client.id
        ).first()
        
        if not sc:
            continue
        
        total_exercises = ProgramExercise.query.filter_by(program_id=sc.program_id).count()
        exercises_completed = len(sc.completed_exercises) if sc.completed_exercises else 0
        completion_percentage = round((exercises_completed / total_exercises) * 100) if total_exercises > 0 else 0
        
        logs = WorkoutLog.query.filter_by(
            session_id=session.id,
            client_id=client.id
        ).all()
        
        total_volume = sum(
            (log.weight_kg or 0) * (log.reps_completed or 0)
            for log in logs
        )
        
        # Calculate Duration
        duration_minutes = 0
        if session.end_time and session.start_time:
            duration_minutes = int((session.end_time - session.start_time).total_seconds() / 60)
        
        # Safely get Trainer Name (checks common attribute names to avoid 500 errors)
        trainer_name = "Unknown Trainer"
        if session.trainer:
            # Tries full_name first, then name, then defaults to "Trainer"
            trainer_name = getattr(session.trainer, 'full_name', getattr(session.trainer, 'name', 'Trainer'))
        
        sessions_data.append({
            'session_id': session.id,
            'program_name': sc.program.name if sc.program else 'Unknown Program',
            'trainer_name': trainer_name,
            'started_at': session.start_time.isoformat() if session.start_time else None,
            'duration_minutes': duration_minutes,
            'exercises_completed': exercises_completed,
            'total_exercises': total_exercises,
            'completion_percentage': completion_percentage,
            'total_volume': total_volume
        })
    
    return jsonify({
        'total': total,
        'sessions': sessions_data
    }), 200

@trainee_history_bp.route('/sessions/<int:session_id>/details', methods=['GET'])
@token_required
def get_trainee_session_details(session_id):
    """Get detailed breakdown of a session (trainee only)"""
    user_id = request.user_id
    
    # Get client record linked to the authenticated user
    client = Client.query.filter_by(user_id=user_id).first()
    if not client:
        return jsonify({'error': 'Client profile not found'}), 404
    
    # Get session
    session = Session.query.get(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    # Verify this client was part of this session
    session_client = SessionClient.query.filter_by(
        session_id=session_id,
        client_id=client.id
    ).first()
    
    if not session_client:
        return jsonify({'error': 'Access denied: You were not part of this session'}), 403
    
    # Get program details
    program = Program.query.get(session_client.program_id)
    
    # Get program exercises
    program_exercises = ProgramExercise.query.filter_by(
        program_id=session_client.program_id
    ).order_by(ProgramExercise.order).all()
    
    # Get workout logs
    logs = WorkoutLog.query.filter_by(
        session_id=session_id,
        client_id=client.id
    ).order_by(WorkoutLog.timestamp).all()
    
    # Build exercises data
    exercises_data = []
    for pe in program_exercises:
        exercise = pe.exercise
        
        # Get actual performance from logs
        exercise_logs = [log for log in logs if log.exercise_id == exercise.id]
        
        actual_sets = []
        for log in exercise_logs:
            actual_sets.append({
                'set': log.set_number,
                'reps': log.reps_completed,
                'weight_kg': log.weight_kg
            })
        
        # Calculate volume
        volume = sum(
            (log.weight_kg or 0) * (log.reps_completed or 0)
            for log in exercise_logs
        )
        
        exercises_data.append({
            'exercise_id': exercise.id,
            'exercise_name': exercise.name,
            'planned': {
                'sets': pe.sets,
                'reps': pe.reps,
                'weight_kg': pe.weight_kg
            },
            'actual': actual_sets,
            'volume': volume
        })
    
    # Calculate duration
    duration_minutes = 0
    if session.end_time and session.start_time:
        duration_minutes = int((session.end_time - session.start_time).total_seconds() / 60)
    
    # Get trainer name
    trainer_name = "Unknown Trainer"
    if session.trainer:
        trainer_name = getattr(session.trainer, 'full_name', getattr(session.trainer, 'name', 'Trainer'))
    
    return jsonify({
        'session_id': session.id,
        'client_name': client.name,
        'program_name': program.name if program else 'Unknown Program',
        'trainer_name': trainer_name,
        'started_at': session.start_time.isoformat(),
        'duration_minutes': duration_minutes,
        'exercises': exercises_data
    }), 200