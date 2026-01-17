from flask import Blueprint, request, jsonify
from models import db
from models.user import User
from models.client import Client
from utils.jwt_utils import token_required, role_required
from utils.validation import validate_client_create_payload, validate_client_update_payload

client_bp = Blueprint('client', __name__, url_prefix='/api/clients')

@client_bp.route('', methods=['GET'])
@token_required
@role_required('trainer')
def get_clients():
    """GET /api/clients - Get all ACTIVE clients for current trainer"""
    trainer_id = request.user_id
    clients = Client.query.filter_by(trainer_id=trainer_id, active=True).all()
    return jsonify([c.to_dict() for c in clients]), 200

@client_bp.route('', methods=['POST'])
@token_required
@role_required('trainer')
def create_client():
    """POST /api/clients - Create new client for current trainer"""
    try:
        trainer_id = request.user_id
        if not trainer_id:
            return jsonify({'error': 'Invalid or missing token'}), 401
        
        data = request.get_json()

        error = validate_client_create_payload(data)
        if error:
            return jsonify({'error': error}), 400
        
        active_count = Client.query.filter_by(trainer_id=trainer_id, active=True).count()
        # if active_count >= 4:
        #     return jsonify({'error': 'Cannot have more than 4 active clients'}), 409
        
        user_id = None
        if data.get('user_email'):
            user = User.query.filter_by(email=data['user_email']).first()
            if user and user.role == 'trainee':
                user_id = user.id

        client = Client(
            trainer_id=trainer_id,
            user_id=user_id,
            name=data['name'],
            age=data['age'],
            fitness_level=data['fitness_level'],
            goals=data['goals']
        )
        db.session.add(client)
        db.session.commit()
        
        return jsonify(client.to_dict()), 201
        
    except Exception as e:
        print(f"Error creating client: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@client_bp.route('/<int:client_id>', methods=['PUT'])
@token_required
@role_required('trainer')
def update_client(client_id):
    """PUT /api/clients/<id> - Update client"""
    trainer_id = request.user_id
    client = Client.query.filter_by(id=client_id, trainer_id=trainer_id).first()
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    data = request.get_json()
    error = validate_client_update_payload(data)
    if error:
        return jsonify({'error': error}), 400
    if 'name' in data:
        client.name = data['name']
    if 'age' in data:
        client.age = data['age']
    if 'fitness_level' in data:
        client.fitness_level = data['fitness_level']
    if 'goals' in data:
        client.goals = data['goals']
    
    db.session.commit()
    return jsonify(client.to_dict()), 200

@client_bp.route('/<int:client_id>/deactivate', methods=['POST'])
@token_required
@role_required('trainer')
def deactivate_client(client_id):
    """POST /api/clients/<id>/deactivate - Deactivate (soft delete) client"""
    trainer_id = request.user_id
    client = Client.query.filter_by(id=client_id, trainer_id=trainer_id).first()
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    client.active = False
    db.session.commit()
    return jsonify({'message': 'Client deactivated'}), 200

@client_bp.route('/my', methods=['GET'])
@token_required
@role_required('trainee')
def get_my_client():
    """GET /api/clients/my — для Trainee Dashboard"""
    user_id = request.user_id
    client = Client.query.filter_by(user_id=user_id, active=True).first()
    if not client:
        return jsonify({'error': 'No client profile found'}), 404
    return jsonify(client.to_dict()), 200
