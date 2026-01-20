from flask import Blueprint, request, jsonify, current_app
from models import db
from models.client import Client
from models.program import Program, ProgramExercise 
from models.session import Session, SessionClient
from utils.jwt_utils import token_required
from models.workout_log import WorkoutLog
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.attributes import flag_modified
from datetime import datetime

session_bp = Blueprint('session', __name__, url_prefix='/api/sessions')

def validate_session_data(data, trainer_id=None):
    errors = []
    client_ids = data.get('client_ids') or []
    program_ids = data.get('program_ids') or []
    
    if not data.get('client_ids') or len(client_ids) < 2:
        errors.append('At least 2 clients are required')
    if len(client_ids) > 4:
        errors.append('Maximum 4 clients allowed')
    
    if not data.get('program_ids') or len(program_ids) != len(client_ids):
        errors.append('Each selected client must have a program assigned')
    
    for client_id in client_ids:
        client = Client.query.filter_by(id=client_id).first()
        if not client:
            errors.append(f'Client ID {client_id} not found')
    
    for program_id in program_ids:
        program = Program.query.get(program_id)
        if not program:
            errors.append(f'Program ID {program_id} not found')

    for client_id, program_id in zip(client_ids, program_ids):
        program = Program.query.get(program_id)
        if not program:
            continue
        if program.client_id != client_id:
            errors.append(f'Program ID {program_id} is not assigned to Client ID {client_id}')
            continue
        if trainer_id is not None and program.trainer_id != trainer_id:
            errors.append(f'Program ID {program_id} is not assigned to Client ID {client_id}')
    
    return errors

@session_bp.route('', methods=['POST'])
@token_required
def create_session():
    trainer_id = request.user_id
    data = request.get_json()
    
    print(f"📋 Creating session for trainer {trainer_id}")
    print(f"📋 Request data: {data}")
    
    errors = validate_session_data(data, trainer_id=trainer_id)
    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400
    
    session = Session(
        trainer_id=trainer_id,
        status='active'
    )
    db.session.add(session)
    db.session.flush()
    
    print(f"✅ Session created with ID: {session.id}")

    for idx, (client_id, program_id) in enumerate(zip(data['client_ids'], data['program_ids'])):
        print(f"➕ Adding client {client_id} to session {session.id}")
        session_client = SessionClient(
            session_id=session.id,
            client_id=client_id,
            program_id=program_id,
            current_exercise_index=0,
            current_set=1,
            status='ready'
        )
        db.session.add(session_client)
    
    db.session.commit()
    
    print(f"📤 Sending session_started to {len(data['client_ids'])} trainees...")
    
    try:
        socketio = current_app.extensions['socketio']
        for client_id in data['client_ids']:
            room = f'trainee_{client_id}'
            print(f"📤 Emitting 'session_started' to room: {room}")
            
            socketio.emit('session_started', {
                'session_id': session.id,
                'message': 'Your trainer has started a session'
            }, room=room)
            
            print(f"✅ Sent 'session_started' to trainee {client_id}")
    except Exception as e:
        print(f"❌ WebSocket emit failed: {e}")
        import traceback
        traceback.print_exc()
    
    return jsonify({'message': 'Session created', 'session_id': session.id}), 201



@session_bp.route('/<int:session_id>', methods=['GET'])
@token_required
def get_session(session_id):
    trainer_id = request.user_id
    session = Session.query.filter_by(id=session_id, trainer_id=trainer_id).first()
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    clients_data = []
    for sc in session.clients:
        program_exercises = ProgramExercise.query.filter_by(program_id=sc.program_id).all()
        exercises = [{
            'id': pe.exercise.id,
            'name': pe.exercise.name,
            'category': pe.exercise.category,
            'difficulty': pe.exercise.difficulty,
            'description': pe.exercise.description,
            'equipment': pe.exercise.equipment,
            'sets': pe.sets,
            'reps': pe.reps,
            'weight_kg': pe.weight_kg,
            'rest_seconds': pe.rest_seconds
        } for pe in program_exercises]

        clients_data.append({
            'client_id': sc.client.id,
            'client_name': sc.client.name,
            'program_id': sc.program.id,
            'program_name': sc.program.name,
            'id': sc.client.id,      
            'name': sc.client.name,           
            'program': {
                'id': sc.program.id,
                'name': sc.program.name,
                'exercises': exercises
            },
            'current_exercise_index': sc.current_exercise_index,
            'current_set': sc.current_set,
            'status': sc.status,
            'completed_exercises': sc.completed_exercises or [],
            'rest_time_remaining': sc.rest_time_remaining or 0
        })

    return jsonify({
        'id': session.id,
        'trainer_id': session.trainer_id,
        'status': session.status,
        'created_at': session.start_time.isoformat(),
        'clients': clients_data
    }), 200


@session_bp.route('/<int:session_id>/complete-set', methods=['POST'])
@token_required
def complete_set(session_id):
    trainer_id = request.user_id
    data = request.get_json()
    
    required_fields = ['client_id', 'exercise_id', 'set_number']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    session = Session.query.filter_by(id=session_id, trainer_id=trainer_id).first_or_404()
    session_client = SessionClient.query.filter_by(
        session_id=session_id, 
        client_id=data['client_id']
    ).first_or_404()
    
    program_exercise = ProgramExercise.query.filter_by(
        program_id=session_client.program_id,
        exercise_id=data['exercise_id']
    ).first()
    
    if not program_exercise:
        return jsonify({'error': 'Exercise not found in program'}), 404
    
    existing_log = WorkoutLog.query.filter_by(
        session_id=session_id,
        client_id=data['client_id'],
        exercise_id=data['exercise_id'],
        set_number=data['set_number'],
    ).first()

    if existing_log is None:
        workout_log = WorkoutLog(
            session_id=session_id,
            client_id=data['client_id'],
            exercise_id=data['exercise_id'],
            set_number=data['set_number'],
            reps_completed=program_exercise.reps,
            weight_kg=program_exercise.weight_kg
        )
        db.session.add(workout_log)

        current_set = session_client.current_set
        total_sets = program_exercise.sets

        if current_set < total_sets:
            session_client.current_set += 1
            session_client.status = 'resting'
            session_client.rest_time_remaining = program_exercise.rest_seconds
        else:
            if session_client.completed_exercises is None:
                session_client.completed_exercises = []
            
            session_client.completed_exercises.append(data['exercise_id'])
            flag_modified(session_client, 'completed_exercises')  
            
            session_client.current_exercise_index += 1
            session_client.current_set = 1
            session_client.rest_time_remaining = 0
            
            total_exercises = ProgramExercise.query.filter_by(program_id=session_client.program_id).count()
            
            if session_client.current_exercise_index >= total_exercises:
                session_client.status = 'completed'
            else:
                session_client.status = 'active'
    
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        session_client = SessionClient.query.filter_by(
            session_id=session_id,
            client_id=data['client_id']
        ).first_or_404()

    updated_client_data = {
        'current_exercise_index': session_client.current_exercise_index,
        'current_set': session_client.current_set,
        'status': session_client.status,
        'rest_time_remaining': session_client.rest_time_remaining,
        'completed_exercises': session_client.completed_exercises
    }

    sets_completed = WorkoutLog.query.filter_by(
        session_id=session_id,
        client_id=data['client_id'],
        exercise_id=data['exercise_id'],
    ).order_by(WorkoutLog.set_number).all()
    updated_client_data['sets_completed'] = [
        {
            'set_number': log.set_number,
            'reps_completed': log.reps_completed,
            'weight_kg': log.weight_kg
        } for log in sets_completed
    ]
    
    try:
        socketio = current_app.extensions['socketio']
        socketio.emit('session_update', {
            'session_id': session_id,
            'client_id': data['client_id'],
            'action': 'set_complete',
            'updated_client_data': updated_client_data
        }, room=f'session_{session_id}')
        print(f"✅ WebSocket emit successful for client {data['client_id']}")
    except Exception as e:
        print(f"⚠️ WebSocket emit failed: {e}")
    
    return jsonify({
        'message': 'Set marked as complete',
        'updated_client': updated_client_data
    }), 200


@session_bp.route('/<int:session_id>/start-next-set', methods=['POST'])
@token_required
def start_next_set(session_id):
    trainer_id = request.user_id
    data = request.get_json()
    client_id = data.get('client_id')
    

    session = Session.query.filter_by(id=session_id, trainer_id=trainer_id).first_or_404()
    session_client = SessionClient.query.filter_by(
        session_id=session_id, 
        client_id=client_id
    ).first_or_404()

    session_client.status = 'working'  
    session_client.rest_time_remaining = 0  
    
    db.session.commit()

    updated_data = {
        'status': 'working',
        'rest_time_remaining': 0,
        'current_set': session_client.current_set
    }

    try:
        socketio = current_app.extensions['socketio']
        socketio.emit('session_update', {
            'session_id': session_id,
            'client_id': client_id,
            'action': 'set_started',
            'updated_client_data': updated_data
        }, room=f'session_{session_id}')
        print(f"✅ WebSocket: Client {client_id} is now WORKING")
    except Exception as e:
        print(f"⚠️ Socket error: {e}")

    return jsonify({'message': 'Next set started', 'updated_client': updated_data}), 200


@session_bp.route('/<int:session_id>/end', methods=['POST'])
@token_required
def end_session(session_id):
    trainer_id = request.user_id
    session = Session.query.filter_by(id=session_id, trainer_id=trainer_id).first()
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    if session.status == 'completed':
        return jsonify({'error': 'Session already ended'}), 400
    
    session.status = 'completed'
    session.end_time = datetime.utcnow()
    duration_minutes = int((session.end_time - session.start_time).total_seconds() / 60)
    
    clients_summary = []
    for sc in session.clients:
        sc.client.last_workout_date = session.start_time.date()
        
        total_exercises = ProgramExercise.query.filter_by(program_id=sc.program_id).count()
        exercises_completed = len(sc.completed_exercises) if sc.completed_exercises else 0
        completion_percentage = round((exercises_completed / total_exercises) * 100, 1) if total_exercises > 0 else 0
        
        clients_summary.append({
            'client_id': sc.client.id,
            'client_name': sc.client.name,
            'exercises_completed': exercises_completed,
            'total_exercises': total_exercises,
            'completion_percentage': completion_percentage
        })
    
    db.session.commit()
    
    summary = {
        'session_id': session_id,
        'start_time': session.start_time.isoformat(),
        'end_time': session.end_time.isoformat(),
        'duration_minutes': duration_minutes,
        'clients': clients_summary
    }
    
    try:
        socketio = current_app.extensions['socketio']
        socketio.emit('session_ended', {
            'session_id': session_id,
            'message': 'Session ended by trainer'
        }, room=f'session_{session_id}')
        print(f"✅ Session ended WebSocket emit successful")
    except Exception as e:
        print(f"⚠️ WebSocket emit failed: {e}")
    
    return jsonify({
        'success': True,
        'message': 'Session ended successfully',
        'summary': summary
    }), 200
