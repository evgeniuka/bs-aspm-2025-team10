import pytest

from app import create_app
from models import db
from models.client import Client
from models.exercise import Exercise
from models.program import Program, ProgramExercise
from models.user import User
from utils.jwt_utils import generate_token


@pytest.fixture
def app():
    app, _ = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        db.drop_all()
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_create_program_success(app, client):
    with app.app_context():
        trainer = User(
            email='trainer@example.com',
            full_name='Trainer User',
            role='trainer'
        )
        trainer.set_password('password123')
        db.session.add(trainer)
        db.session.flush()

        client_record = Client(
            trainer_id=trainer.id,
            name='Test Client',
            age=30,
            fitness_level='Beginner',
            goals='Build strength',
            active=True
        )
        db.session.add(client_record)

        exercises = []
        for idx in range(5):
            exercise = Exercise(
                name=f'Exercise {idx}',
                category='upper_body',
                description=f'Description {idx}',
                equipment='bodyweight',
                difficulty='beginner'
            )
            db.session.add(exercise)
            exercises.append(exercise)

        db.session.flush()

        token = generate_token(trainer.id, trainer.role)
        payload = {
            'name': 'Strength Builder',
            'client_id': client_record.id,
            'notes': 'Focus on form.',
            'exercises': [
                {
                    'exercise_id': exercise.id,
                    'sets': 3,
                    'reps': 10,
                    'weight_kg': 20,
                    'rest_seconds': 60
                }
                for exercise in exercises
            ]
        }
        db.session.commit()

    response = client.post(
        '/api/programs',
        json=payload,
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code in (200, 201)

    data = response.get_json() or {}
    program_id = (
        data.get('id')
        or data.get('program_id')
        or (data.get('program') or {}).get('id')
    )
    assert program_id is not None, f'Expected program id in response, got: {data}'

    with app.app_context():
        program = db.session.get(Program, program_id)
        assert program is not None
        assert program.name == payload['name']
        assert program.client_id == payload['client_id']

        program_exercises = ProgramExercise.query.filter_by(program_id=program_id).all()
        assert len(program_exercises) == len(payload['exercises'])
