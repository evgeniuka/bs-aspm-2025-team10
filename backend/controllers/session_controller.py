from flask import Blueprint, request, jsonify
from models import db
from models.user import User
from models.client import Client
from models.program import Program
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