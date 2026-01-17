from flask import Blueprint, request, jsonify
from models import db
from models.user import User
from models.client import Client
from models.exercise import Exercise
from models.program import Program, ProgramExercise
from utils.jwt_utils import token_required


program_bp = Blueprint('program', __name__, url_prefix='/api/programs')

def validate_program_data(data):
    errors = []

    if not isinstance(data, dict):
        return ['Invalid request payload']
    
    if not data.get('name') or len(data['name']) < 3 or len(data['name']) > 100:
        errors.append('Program name must be 3-100 characters')
    
    if not data.get('client_id'):
        errors.append('Client is required')
    
    exercises = data.get('exercises', [])
    if len(exercises) < 5:
        errors.append('At least 5 exercises are required')
    if len(exercises) > 20:
        errors.append('Maximum 20 exercises allowed')
    
    for ex in exercises:
        if 'exercise_id' not in ex:
            errors.append('Exercise ID is required')
            continue
        if not isinstance(ex.get('exercise_id'), int):
            errors.append('Exercise ID must be an integer')
        if not (1 <= ex.get('sets', 0) <= 10):
            errors.append(f'Sets must be between 1-10 for exercise')
        if not (1 <= ex.get('reps', 0) <= 50):
            errors.append(f'Reps must be between 1-50 for exercise')
        if not (0 <= ex.get('weight_kg', -1) <= 500):
            errors.append(f'Weight must be between 0-500 kg for exercise')
        if not (0 <= ex.get('rest_seconds', -1) <= 600):
            errors.append(f'Rest must be between 0-600 seconds for exercise')
    
    return errors

@program_bp.route('', methods=['POST'])
@token_required
def create_program():
    trainer_id = request.user_id
    data = request.get_json() or {}
    

    errors = validate_program_data(data)
    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400
    
    client = Client.query.filter_by(id=data['client_id'], trainer_id=trainer_id).first()
    if not client:
        return jsonify({'error': 'Client not found or not owned by trainer'}), 404
    
    program = Program(
        trainer_id=trainer_id,
        client_id=data['client_id'],
        name=data['name'],
        notes=data.get('notes')
    )
    db.session.add(program)
    db.session.flush() 
    
    for idx, ex_data in enumerate(data['exercises']):
        exercise = Exercise.query.get(ex_data['exercise_id'])
        if not exercise:
            db.session.rollback()
            return jsonify({'error': f'Exercise ID {ex_data["exercise_id"]} not found'}), 400
        
        program_ex = ProgramExercise(
            program_id=program.id,
            exercise_id=ex_data['exercise_id'],
            order=idx,
            sets=ex_data['sets'],
            reps=ex_data['reps'],
            weight_kg=ex_data['weight_kg'],
            rest_seconds=ex_data['rest_seconds'],
            notes=ex_data.get('notes')
        )
        db.session.add(program_ex)
    
    db.session.commit()
    return jsonify({'message': 'Program created', 'program_id': program.id, 'id': program.id}), 201

@program_bp.route('', methods=['GET'])
@token_required
def get_programs():
    trainer_id = request.user_id
    client_id = request.args.get('client_id')
    
    if not client_id:
        return jsonify({'error': 'client_id query param is required'}), 400
    
    client = Client.query.filter_by(id=client_id, trainer_id=trainer_id).first()
    if not client:
        return jsonify({'error': 'Client not found or not owned by trainer'}), 404
    
    programs = Program.query.filter_by(client_id=client_id).all()
    result = []
    for p in programs:
        exercises = ProgramExercise.query.filter_by(program_id=p.id).order_by(
            ProgramExercise.order
        ).all()
        result.append(
            {
                'id': p.id,
                'client_id': p.client_id,
                'trainer_id': p.trainer_id,
                'name': p.name,
                'notes': p.notes,
                'created_at': p.created_at.isoformat(),
                'exercises': [
                    {
                        'id': ex.id,
                        'exercise_id': ex.exercise_id,
                        'order': ex.order,
                        'sets': ex.sets,
                        'reps': ex.reps,
                        'weight_kg': ex.weight_kg,
                        'rest_seconds': ex.rest_seconds,
                    }
                    for ex in exercises
                ],
            }
        )
    
    return jsonify(result), 200
