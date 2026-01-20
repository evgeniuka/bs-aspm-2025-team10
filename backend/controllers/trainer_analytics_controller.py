from flask import Blueprint, request, jsonify
from models import db
from models.client import Client
from models.session import Session, SessionClient
from models.workout_log import WorkoutLog
from models.exercise import Exercise
from utils.jwt_utils import token_required
from sqlalchemy import func
from datetime import datetime, timedelta

trainer_analytics_bp = Blueprint('trainer_analytics', __name__, url_prefix='/api/clients')

@trainer_analytics_bp.route('/<int:client_id>/analytics', methods=['GET'])
@token_required
def get_client_analytics(client_id):
    """Get comprehensive analytics for a specific client (trainer only)"""
    trainer_id = request.user_id
    
    client = Client.query.filter_by(id=client_id, trainer_id=trainer_id).first()
    if not client:
        return jsonify({'error': 'Client not found or access denied'}), 403
    

    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    

    total_sessions = Session.query.join(SessionClient).filter(
        SessionClient.client_id == client_id,
        Session.status == 'completed',
        Session.start_time >= start_date
    ).count()
    

    total_volume_result = db.session.query(
        func.sum(WorkoutLog.weight_kg * WorkoutLog.reps_completed)
    ).join(Session).filter(
        WorkoutLog.client_id == client_id,
        Session.status == 'completed',
        Session.start_time >= start_date
    ).scalar()
    total_volume = int(total_volume_result) if total_volume_result else 0
    

    sessions = Session.query.join(SessionClient).filter(
        SessionClient.client_id == client_id,
        Session.status == 'completed',
        Session.start_time >= start_date
    ).all()
    
    total_time_minutes = 0
    for session in sessions:
        if session.end_time and session.start_time:
            total_time_minutes += int((session.end_time - session.start_time).total_seconds() / 60)
    

    completion_rates = []
    for session in sessions:
        sc = SessionClient.query.filter_by(
            session_id=session.id,
            client_id=client_id
        ).first()
        if sc and sc.program_id:
            from models.program import ProgramExercise
            total_exercises = ProgramExercise.query.filter_by(program_id=sc.program_id).count()
            completed = len(sc.completed_exercises) if sc.completed_exercises else 0
            if total_exercises > 0:
                completion_rates.append((completed / total_exercises) * 100)
    
    avg_completion_rate = round(sum(completion_rates) / len(completion_rates)) if completion_rates else 0
    

    volume_over_time = []
    current_date = start_date
    while current_date <= datetime.utcnow():
        week_end = current_date + timedelta(days=7)
        
        week_volume_result = db.session.query(
            func.sum(WorkoutLog.weight_kg * WorkoutLog.reps_completed)
        ).join(Session).filter(
            WorkoutLog.client_id == client_id,
            Session.status == 'completed',
            Session.start_time >= current_date,
            Session.start_time < week_end
        ).scalar()
        
        week_volume = int(week_volume_result) if week_volume_result else 0
        
        volume_over_time.append({
            'week_start': current_date.strftime('%Y-%m-%d'),
            'volume': week_volume
        })
        
        current_date = week_end
    

    exercise_performance = db.session.query(
        Exercise.name,
        func.sum(WorkoutLog.weight_kg * WorkoutLog.reps_completed).label('total_volume'),
        func.count(WorkoutLog.id).label('total_sets')
    ).join(WorkoutLog).join(Session).filter(
        WorkoutLog.client_id == client_id,
        Session.status == 'completed',
        Session.start_time >= start_date
    ).group_by(Exercise.id).order_by(func.sum(WorkoutLog.weight_kg * WorkoutLog.reps_completed).desc()).limit(5).all()
    
    exercise_data = [
        {
            'exercise_name': ex.name,
            'total_volume': int(ex.total_volume) if ex.total_volume else 0,
            'total_sets': ex.total_sets
        }
        for ex in exercise_performance
    ]
    

    weekly_frequency = db.session.query(
        func.date_trunc('week', Session.start_time).label('week'),
        func.count(Session.id).label('sessions_count')
    ).join(SessionClient).filter(
        SessionClient.client_id == client_id,
        Session.status == 'completed',
        Session.start_time >= start_date
    ).group_by('week').order_by('week').all()
    
    frequency_data = [
        {
            'week': wf.week.strftime('%Y-%m-%d'),
            'sessions': wf.sessions_count
        }
        for wf in weekly_frequency
    ]

    key_exercises = ['Bench Press', 'Squat', 'Deadlift', 'Overhead Press']
    strength_progression = {}
    
    for exercise_name in key_exercises:
        exercise = Exercise.query.filter_by(name=exercise_name).first()
        if not exercise:
            continue
        
        progression = db.session.query(
            func.date(Session.start_time).label('date'),
            func.max(WorkoutLog.weight_kg).label('max_weight')
        ).join(Session).filter(
            WorkoutLog.client_id == client_id,
            WorkoutLog.exercise_id == exercise.id,
            Session.status == 'completed',
            Session.start_time >= start_date
        ).group_by(func.date(Session.start_time)).order_by(func.date(Session.start_time)).all()
        
        if progression:
            strength_progression[exercise_name] = [
                {
                    'date': p.date.strftime('%Y-%m-%d'),
                    'max_weight': float(p.max_weight)
                }
                for p in progression
            ]
    
    return jsonify({
        'overview': {
            'total_sessions': total_sessions,
            'total_volume_kg': total_volume,
            'total_time_minutes': total_time_minutes,
            'avg_completion_rate': avg_completion_rate
        },
        'volume_over_time': volume_over_time,
        'exercise_performance': exercise_data,
        'weekly_frequency': frequency_data,
        'strength_progression': strength_progression,
        'period_days': days
    }), 200


@trainer_analytics_bp.route('/<int:client_id>/analytics/comparison', methods=['GET'])
@token_required
def get_client_comparison(client_id):
    """Compare client's progress against their own baseline (trainer only)"""
    trainer_id = request.user_id
    

    client = Client.query.filter_by(id=client_id, trainer_id=trainer_id).first()
    if not client:
        return jsonify({'error': 'Client not found or access denied'}), 403
    

    now = datetime.utcnow()
    current_period_start = now - timedelta(days=7)
    previous_period_start = now - timedelta(days=14)
    previous_period_end = current_period_start
    

    current_volume = db.session.query(
        func.sum(WorkoutLog.weight_kg * WorkoutLog.reps_completed)
    ).join(Session).filter(
        WorkoutLog.client_id == client_id,
        Session.status == 'completed',
        Session.start_time >= current_period_start
    ).scalar() or 0
    
    current_sessions = Session.query.join(SessionClient).filter(
        SessionClient.client_id == client_id,
        Session.status == 'completed',
        Session.start_time >= current_period_start
    ).count()
    

    previous_volume = db.session.query(
        func.sum(WorkoutLog.weight_kg * WorkoutLog.reps_completed)
    ).join(Session).filter(
        WorkoutLog.client_id == client_id,
        Session.status == 'completed',
        Session.start_time >= previous_period_start,
        Session.start_time < previous_period_end
    ).scalar() or 0
    
    previous_sessions = Session.query.join(SessionClient).filter(
        SessionClient.client_id == client_id,
        Session.status == 'completed',
        Session.start_time >= previous_period_start,
        Session.start_time < previous_period_end
    ).count()
    

    volume_change = ((current_volume - previous_volume) / previous_volume * 100) if previous_volume > 0 else 0
    session_change = ((current_sessions - previous_sessions) / previous_sessions * 100) if previous_sessions > 0 else 0
    
    return jsonify({
        'current_period': {
            'volume': int(current_volume),
            'sessions': current_sessions
        },
        'previous_period': {
            'volume': int(previous_volume),
            'sessions': previous_sessions
        },
        'changes': {
            'volume_change_percent': round(volume_change, 1),
            'session_change_percent': round(session_change, 1)
        }
    }), 200
