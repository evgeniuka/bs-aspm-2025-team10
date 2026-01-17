from flask import Blueprint, request, jsonify
from models import db
from models.user import User
from models.client import Client
from models.program import Program
from models.session import Session, SessionClient
from utils.jwt_utils import token_required

session_bp = Blueprint('session', __name__, url_prefix='/api/sessions')

def validate_session_data(data, trainer_id=None):
    errors = []

    if not data:
        return ['Invalid request payload']

    client_ids = data.get('client_ids') or []
    program_ids = data.get('program_ids') or []

    if len(client_ids) < 2:
        errors.append('At least 2 clients are required')
    if len(client_ids) > 4:
        errors.append('Maximum 4 clients allowed')

    if not program_ids or len(program_ids) != len(client_ids):
        errors.append('Each selected client must have a program assigned')

    client_lookup = {}
    for client_id in client_ids:
        client = Client.query.filter_by(id=client_id).first()
        if not client:
            errors.append(f'Client ID {client_id} not found')
            continue
        if trainer_id and client.trainer_id != trainer_id:
            errors.append(f'Client ID {client_id} not assigned to trainer')
            continue
        client_lookup[client_id] = client

    for client_id, program_id in zip(client_ids, program_ids):
        program = Program.query.get(program_id)
        if not program:
            errors.append(f'Program ID {program_id} not found')
            continue
        if trainer_id and program.trainer_id != trainer_id:
            errors.append(f'Program ID {program_id} not assigned to trainer')
            continue
        if program.client_id != client_id:
            errors.append(f'Program ID {program_id} is not assigned to Client ID {client_id}')

    return errors

@session_bp.route('', methods=['POST'])
@token_required
def create_session():
    trainer_id = request.user_id
    data = request.get_json()
    
    errors = validate_session_data(data, trainer_id=trainer_id)
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
    session = Session.query.get_or_404(session_id)
    if session.trainer_id != request.user_id:
        return jsonify({'error': 'Session not found'}), 404
    
    result = {
        'id': session.id,
        'trainer_id': session.trainer_id,
        'start_time': session.start_time.isoformat(),
        'status': session.status,
        'clients': []
    }
    
    for sc in session.clients:
        result['clients'].append({
            'client_id': sc.client_id,
            'client_name': sc.client.name,
            'program_id': sc.program_id,
            'program_name': sc.program.name,
            'current_exercise_index': sc.current_exercise_index,
            'current_set': sc.current_set,
            'status': sc.status
        })
    
    return jsonify(result), 200
