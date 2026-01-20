from flask import Blueprint, request, jsonify
from models import db
from models.client import Client
from models.session import Session, SessionClient
from models.program import Program, ProgramExercise
from models.workout_log import WorkoutLog
from utils.jwt_utils import token_required

trainer_history_bp = Blueprint('trainer_history', __name__, url_prefix='/api/clients')

@trainer_history_bp.route('/<int:client_id>/sessions', methods=['GET'])
@token_required
def get_client_sessions(client_id):
    """Get all completed sessions for a specific client (trainer only)"""
    trainer_id = request.user_id
    

    client = Client.query.filter_by(id=client_id, trainer_id=trainer_id).first()
    if not client:
        return jsonify({'error': 'Client not found or access denied'}), 403
    

    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    status_filter = request.args.get('status', 'completed', type=str)
    

    sessions_query = Session.query.join(SessionClient).filter(
        SessionClient.client_id == client_id,
        Session.status == status_filter
    ).order_by(Session.start_time.desc())
    
    total = sessions_query.count()
    sessions = sessions_query.limit(limit).offset(offset).all()
    
    sessions_data = []
    for session in sessions:

        sc = SessionClient.query.filter_by(
            session_id=session.id,
            client_id=client_id
        ).first()
        
        if not sc:
            continue
        

        program = Program.query.get(sc.program_id)
        total_exercises = ProgramExercise.query.filter_by(program_id=sc.program_id).count()
        exercises_completed = len(sc.completed_exercises) if sc.completed_exercises else 0
        completion_percentage = round((exercises_completed / total_exercises) * 100) if total_exercises > 0 else 0
        

        logs = WorkoutLog.query.filter_by(
            session_id=session.id,
            client_id=client_id
        ).all()
        
        total_sets = len(logs)
        

        total_volume = 0
        for log in logs:
            if log.weight_kg and log.reps_completed:
                total_volume += log.weight_kg * log.reps_completed
        

        if session.end_time and session.start_time:
            duration_minutes = int((session.end_time - session.start_time).total_seconds() / 60)
        else:
            duration_minutes = 0
        
        sessions_data.append({
            'session_id': session.id,
            'program_name': program.name if program else 'Unknown Program',
            'started_at': session.start_time.isoformat(),
            'ended_at': session.end_time.isoformat() if session.end_time else None,
            'duration_minutes': duration_minutes,
            'exercises_completed': exercises_completed,
            'total_exercises': total_exercises,
            'completion_percentage': completion_percentage,
            'total_sets': total_sets,
            'total_volume': total_volume
        })
    
    return jsonify({
        'total': total,
        'sessions': sessions_data
    }), 200


@trainer_history_bp.route('/sessions/<int:session_id>/details', methods=['GET'])
@token_required
def get_session_details(session_id):
    """Get detailed breakdown of a session (trainer only)"""
    trainer_id = request.user_id
    

    session = Session.query.get(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    

    if session.trainer_id != trainer_id:
        return jsonify({'error': 'Access denied'}), 403
    

    session_clients = SessionClient.query.filter_by(session_id=session_id).all()
    
    if not session_clients:
        return jsonify({'error': 'No clients in this session'}), 404
    

    sc = session_clients[0]
    client = Client.query.get(sc.client_id)
    program = Program.query.get(sc.program_id)
    
   
    program_exercises = ProgramExercise.query.filter_by(
        program_id=sc.program_id
    ).order_by(ProgramExercise.order).all()
    

    logs = WorkoutLog.query.filter_by(
        session_id=session_id,
        client_id=sc.client_id
    ).order_by(WorkoutLog.timestamp).all()
    

    exercises_data = []
    for pe in program_exercises:
        exercise = pe.exercise
        
        
        exercise_logs = [log for log in logs if log.exercise_id == exercise.id]
        
        actual_sets = []
        for log in exercise_logs:
            actual_sets.append({
                'set': log.set_number,
                'reps': log.reps_completed,
                'weight_kg': log.weight_kg
            })
        
  
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
    

    duration_minutes = 0
    if session.end_time and session.start_time:
        duration_minutes = int((session.end_time - session.start_time).total_seconds() / 60)
    
    return jsonify({
        'session_id': session.id,
        'client_name': client.name,
        'program_name': program.name,
        'started_at': session.start_time.isoformat(),
        'duration_minutes': duration_minutes,
        'exercises': exercises_data
    }), 200


