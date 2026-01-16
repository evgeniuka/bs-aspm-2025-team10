from flask import Blueprint, request, jsonify
from models import db
from models.client import Client
from models.session import Session, SessionClient
from models.workout_log import WorkoutLog
from models.exercise import Exercise
from utils.jwt_utils import token_required
from sqlalchemy import func
from datetime import datetime, timedelta

trainee_analytics_bp = Blueprint('trainee_analytics', __name__, url_prefix='/api/trainee')

@trainee_analytics_bp.route('/analytics', methods=['GET'])
@token_required
def get_trainee_analytics():
    """Get analytics for authenticated trainee"""
    user_id = request.user_id
    
    client = Client.query.filter_by(user_id=user_id).first()
    if not client:
        return jsonify({'error': 'Client profile not found'}), 404
    
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    total_sessions = Session.query.join(SessionClient).filter(
        SessionClient.client_id == client.id,
        Session.status == 'completed',
        Session.start_time >= start_date
    ).count()
    
    total_volume_result = db.session.query(
        func.sum(WorkoutLog.weight_kg * WorkoutLog.reps_completed)
    ).join(Session).filter(
        WorkoutLog.client_id == client.id,
        Session.status == 'completed',
        Session.start_time >= start_date
    ).scalar()
    total_volume = int(total_volume_result) if total_volume_result else 0
    
    sessions = Session.query.join(SessionClient).filter(
        SessionClient.client_id == client.id,
        Session.status == 'completed',
        Session.start_time >= start_date
    ).all()
    
    total_time_minutes = 0
    for session in sessions:
        if session.end_time and session.start_time:
            total_time_minutes += int((session.end_time - session.start_time).total_seconds() / 60)
    
    personal_records = db.session.query(
        Exercise.name,
        func.max(WorkoutLog.weight_kg).label('max_weight')
    ).join(WorkoutLog).join(Session).filter(
        WorkoutLog.client_id == client.id,
        Session.status == 'completed'
    ).group_by(Exercise.id).order_by(func.max(WorkoutLog.weight_kg).desc()).limit(5).all()
    
    pr_data = [
        {
            'exercise_name': pr.name,
            'max_weight': float(pr.max_weight)
        }
        for pr in personal_records
    ]
    
    volume_over_time = []
    current_date = start_date
    while current_date <= datetime.utcnow():
        week_end = current_date + timedelta(days=7)
        
        week_volume_result = db.session.query(
            func.sum(WorkoutLog.weight_kg * WorkoutLog.reps_completed)
        ).join(Session).filter(
            WorkoutLog.client_id == client.id,
            Session.status == 'completed',
            Session.start_time >= current_date,
            Session.start_time < week_end
        ).scalar()
        
        volume_over_time.append({
            'week_start': current_date.strftime('%Y-%m-%d'),
            'volume': int(week_volume_result) if week_volume_result else 0
        })
        
        current_date = week_end
    
    return jsonify({
        'overview': {
            'total_sessions': total_sessions,
            'total_volume_kg': total_volume,
            'total_time_minutes': total_time_minutes
        },
        'personal_records': pr_data,
        'volume_over_time': volume_over_time,
        'period_days': days
    }), 200
