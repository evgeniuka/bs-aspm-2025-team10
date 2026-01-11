from flask import Blueprint, request, jsonify
from models import db
from models.client import Client
from models.program import Program, ProgramExercise 
from models.session import Session, SessionClient
from utils.jwt_utils import token_required

session_bp = Blueprint('session', __name__, url_prefix='/api/sessions')

def validate_session_data(data):
    errors = []
    
    if not data.get('client_ids') or len(data['client_ids']) < 2:
        errors.append('At least 2 clients are required')
    if len(data['client_ids']) > 4:
        errors.append('Maximum 4 clients allowed')
    
    if not data.get('program_ids') or len(data['program_ids']) != len(data['client_ids']):
        errors.append('Each selected client must have a program assigned')
    
    for client_id in data['client_ids']:
        client = Client.query.filter_by(id=client_id).first()
        if not client:
            errors.append(f'Client ID {client_id} not found')
    
    for program_id in data['program_ids']:
        program = Program.query.get(program_id)
        if not program:
            errors.append(f'Program ID {program_id} not found')
    
    return errors

@session_bp.route('', methods=['POST'])
@token_required
def create_session():
    trainer_id = request.user_id
    data = request.get_json()
    
    errors = validate_session_data(data)
    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400
    
    session = Session(
        trainer_id=trainer_id,
        status='active'
    )
    db.session.add(session)
    db.session.flush()      

    for idx, (client_id, program_id) in enumerate(zip(data['client_ids'], data['program_ids'])):
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
    return jsonify({'message': 'Session created', 'session_id': session.id}), 201


@session_bp.route('/<int:session_id>', methods=['GET'])
@token_required
def get_session(session_id):
    trainer_id = request.user_id
    session = Session.query.filter_by(id=session_id, trainer_id=trainer_id).first_or_404()
    
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
            'id': sc.client.id,      
            'name': sc.client.name,           
            'program': {
                'id': sc.program.id,
                'name': sc.program.name,
                'exercises': exercises
            },
            'current_exercise_index': sc.current_exercise_index,
            'current_set': sc.current_set,
            'status': sc.status
        })

    return jsonify({
        'id': session.id,
        'trainer_id': session.trainer_id,
        'status': session.status,
        'created_at': session.start_time.isoformat(),
        'clients': clients_data
    }), 200

@session_bp.route('/<int:session_id>/end', methods=['POST'])
@token_required
def end_session(session_id):
    trainer_id = request.user_id
    session = Session.query.filter_by(id=session_id, trainer_id=trainer_id).first_or_404()
    
    session.status = 'completed'
    db.session.commit()
    
    return jsonify({'message': 'Session ended successfully'}), 200