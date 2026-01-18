from flask import Blueprint, request, jsonify
from models import db
from models.user import User
from models.client import Client
from models.exercise import Exercise
from models.program import Program, ProgramExercise
from utils.jwt_utils import token_required

program_bp = Blueprint('program', __name__, url_prefix='/api/programs')

def _validate_exercises(exercises):
    errors = []

    if len(exercises) < 5:
        errors.append('At least 5 exercises are required')
    if len(exercises) > 20:
        errors.append('Maximum 20 exercises allowed')
    
    for ex in exercises:
        if not isinstance(ex, dict):
            errors.append('Exercise must be an object')
            continue
        if ex.get('exercise_id') is None:
            errors.append('Exercise ID is required')
        elif not isinstance(ex.get('exercise_id'), int):
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


def validate_program_data(data):
    errors = []

    if not data.get('name') or len(data['name']) < 3 or len(data['name']) > 100:
        errors.append('Program name must be 3-100 characters')

    if not data.get('client_id'):
        errors.append('Client is required')

    exercises = data.get('exercises', [])
    errors.extend(_validate_exercises(exercises))

    return errors


def validate_program_update_data(data):
    if data.get('exercises') is None:
        return ['Exercises are required']

    return _validate_exercises(data.get('exercises', []))

def serialize_program(program):
    return {
        'id': program.id,
        'trainer_id': program.trainer_id,
        'client_id': program.client_id,
        'name': program.name,
        'notes': program.notes,
        'created_at': program.created_at.isoformat() if program.created_at else None,
        'exercises': [
            {
                'id': exercise.id,
                'exercise_id': exercise.exercise_id,
                'order': exercise.order,
                'sets': exercise.sets,
                'reps': exercise.reps,
                'weight_kg': exercise.weight_kg,
                'rest_seconds': exercise.rest_seconds,
                'notes': exercise.notes
            }
            for exercise in sorted(program.exercises, key=lambda ex: ex.order)
        ]
    }

@program_bp.route('', methods=['GET'])
@token_required
def get_programs():
    trainer_id = request.user_id
    client_id = request.args.get('client_id', type=int)
    programs_query = Program.query.filter_by(trainer_id=trainer_id)

    if client_id:
        client = Client.query.filter_by(id=client_id, trainer_id=trainer_id).first()
        if not client:
            return jsonify({'error': 'Client not found or not owned by trainer'}), 404
        programs_query = programs_query.filter_by(client_id=client_id)

    programs = programs_query.order_by(Program.created_at.desc()).all()
    return jsonify([serialize_program(program) for program in programs]), 200

@program_bp.route('', methods=['POST'])
@token_required
def create_program():
    trainer_id = request.user_id
    data = request.get_json()
    

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
        exercise = db.session.get(Exercise, ex_data['exercise_id'])
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
    return jsonify({"message": "Program created", "program_id": program.id, "id": program.id}), 201


@program_bp.route('/<int:program_id>', methods=['PUT'])
@token_required
def update_program(program_id):
    trainer_id = request.user_id
    data = request.get_json() or {}

    errors = validate_program_update_data(data)
    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400

    program = Program.query.filter_by(id=program_id, trainer_id=trainer_id).first()
    if not program:
        return jsonify({'error': 'Program not found or not owned by trainer'}), 404

    program.name = data.get('name', program.name)
    program.notes = data.get('notes', program.notes)

    program.exercises.clear()
    db.session.flush()

    for idx, ex_data in enumerate(data['exercises']):
        exercise = db.session.get(Exercise, ex_data['exercise_id'])
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
    return jsonify({"message": "Program updated", "program_id": program.id}), 200


@program_bp.route('/<int:program_id>', methods=['DELETE'])
@token_required
def delete_program(program_id):
    trainer_id = request.user_id
    program = Program.query.filter_by(id=program_id, trainer_id=trainer_id).first()
    if not program:
        return jsonify({'error': 'Program not found or not owned by trainer'}), 404

    db.session.delete(program)
    db.session.commit()
    return jsonify({"message": "Program deleted", "program_id": program.id}), 200
