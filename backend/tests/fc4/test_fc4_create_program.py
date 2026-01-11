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


def create_trainer(app, email='trainer@example.com', role='trainer'):
    with app.app_context():
        trainer = User(
            email=email,
            full_name='Trainer User',
            role=role
        )
        trainer.set_password('password123')
        db.session.add(trainer)
        db.session.commit()
        return trainer.id, role


def create_client_record(app, trainer_id, name='Test Client'):
    with app.app_context():
        client_record = Client(
            trainer_id=trainer_id,
            name=name,
            age=30,
            fitness_level='Beginner',
            goals='Build strength',
            active=True
        )
        db.session.add(client_record)
        db.session.commit()
        return client_record.id


def create_exercises(app, count=5):
    with app.app_context():
        exercises = []
        for idx in range(count):
            exercise = Exercise(
                name=f'Exercise {idx}',
                category='upper_body',
                description=f'Description {idx}',
                equipment='bodyweight',
                difficulty='beginner'
            )
            db.session.add(exercise)
            exercises.append(exercise)
        db.session.commit()
        return [exercise.id for exercise in exercises]


def build_exercises_payload(exercise_ids, overrides=None):
    overrides = overrides or {}
    payload = []
    for exercise_id in exercise_ids:
        entry = {
            'exercise_id': exercise_id,
            'sets': 3,
            'reps': 10,
            'weight_kg': 20,
            'rest_seconds': 60
        }
        entry.update(overrides)
        payload.append(entry)
    return payload


def generate_auth_token(app, user_id, role):
    with app.app_context():
        return generate_token(user_id, role)


def test_create_program_success_persists(app, client):
    trainer_id, role = create_trainer(app)
    client_id = create_client_record(app, trainer_id)
    exercise_ids = create_exercises(app, count=5)
    token = generate_auth_token(app, trainer_id, role)

    payload = {
        'name': 'Strength Builder',
        'client_id': client_id,
        'notes': 'Focus on form.',
        'exercises': build_exercises_payload(exercise_ids)
    }

    response = client.post(
        '/api/programs',
        json=payload,
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 201

    data = response.get_json() or {}
    assert data.get('program_id') is not None
    assert data.get('id') == data['program_id']
    assert data.get('message') == 'Program created'

    with app.app_context():
        program = db.session.get(Program, data['program_id'])
        assert program is not None
        assert program.name == payload['name']
        assert program.client_id == payload['client_id']
        assert program.trainer_id == trainer_id
        assert program.notes == payload['notes']

        program_exercises = ProgramExercise.query.filter_by(program_id=program.id).all()
        assert len(program_exercises) == len(payload['exercises'])
        orders = sorted(pe.order for pe in program_exercises)
        assert orders == list(range(len(payload['exercises'])))
        first_ex = program_exercises[0]
        assert first_ex.sets == payload['exercises'][0]['sets']
        assert first_ex.reps == payload['exercises'][0]['reps']
        assert first_ex.weight_kg == payload['exercises'][0]['weight_kg']
        assert first_ex.rest_seconds == payload['exercises'][0]['rest_seconds']


def test_create_program_missing_token_returns_401(app, client):
    trainer_id, _ = create_trainer(app)
    client_id = create_client_record(app, trainer_id)
    exercise_ids = create_exercises(app, count=5)

    response = client.post(
        '/api/programs',
        json={
            'name': 'No Token',
            'client_id': client_id,
            'exercises': build_exercises_payload(exercise_ids)
        }
    )

    assert response.status_code == 401
    assert response.get_json() == {'error': 'Token is missing'}


def test_create_program_invalid_token_format_returns_401(app, client):
    trainer_id, _ = create_trainer(app)
    client_id = create_client_record(app, trainer_id)
    exercise_ids = create_exercises(app, count=5)

    response = client.post(
        '/api/programs',
        json={
            'name': 'Bad Token',
            'client_id': client_id,
            'exercises': build_exercises_payload(exercise_ids)
        },
        headers={'Authorization': 'Bearer'}
    )

    assert response.status_code == 401
    assert response.get_json() == {'error': 'Invalid token format'}


def test_create_program_invalid_token_returns_401(app, client):
    trainer_id, _ = create_trainer(app)
    client_id = create_client_record(app, trainer_id)
    exercise_ids = create_exercises(app, count=5)

    response = client.post(
        '/api/programs',
        json={
            'name': 'Expired Token',
            'client_id': client_id,
            'exercises': build_exercises_payload(exercise_ids)
        },
        headers={'Authorization': 'Bearer invalid.token.value'}
    )

    assert response.status_code == 401
    assert response.get_json() == {'error': 'Token is invalid or expired'}


def test_create_program_validation_missing_name(app, client):
    trainer_id, role = create_trainer(app)
    client_id = create_client_record(app, trainer_id)
    exercise_ids = create_exercises(app, count=5)
    token = generate_auth_token(app, trainer_id, role)

    response = client.post(
        '/api/programs',
        json={
            'name': '',
            'client_id': client_id,
            'exercises': build_exercises_payload(exercise_ids)
        },
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'Validation failed'
    assert 'Program name must be 3-100 characters' in data['details']


def test_create_program_validation_missing_client(app, client):
    trainer_id, role = create_trainer(app)
    exercise_ids = create_exercises(app, count=5)
    token = generate_auth_token(app, trainer_id, role)

    response = client.post(
        '/api/programs',
        json={
            'name': 'No Client',
            'exercises': build_exercises_payload(exercise_ids)
        },
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'Validation failed'
    assert 'Client is required' in data['details']


def test_create_program_validation_exercises_too_few(app, client):
    trainer_id, role = create_trainer(app)
    client_id = create_client_record(app, trainer_id)
    exercise_ids = create_exercises(app, count=4)
    token = generate_auth_token(app, trainer_id, role)

    response = client.post(
        '/api/programs',
        json={
            'name': 'Too Few Exercises',
            'client_id': client_id,
            'exercises': build_exercises_payload(exercise_ids)
        },
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'Validation failed'
    assert 'At least 5 exercises are required' in data['details']


def test_create_program_validation_exercises_too_many(app, client):
    trainer_id, role = create_trainer(app)
    client_id = create_client_record(app, trainer_id)
    token = generate_auth_token(app, trainer_id, role)

    response = client.post(
        '/api/programs',
        json={
            'name': 'Too Many Exercises',
            'client_id': client_id,
            'exercises': build_exercises_payload(list(range(1, 22)))
        },
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'Validation failed'
    assert 'Maximum 20 exercises allowed' in data['details']


def test_create_program_validation_invalid_exercise_values(app, client):
    trainer_id, role = create_trainer(app)
    client_id = create_client_record(app, trainer_id)
    exercise_ids = create_exercises(app, count=5)
    token = generate_auth_token(app, trainer_id, role)
    exercises = build_exercises_payload(exercise_ids)
    exercises[0].update({
        'sets': 0,
        'reps': 0,
        'weight_kg': -1,
        'rest_seconds': -1
    })

    response = client.post(
        '/api/programs',
        json={
            'name': 'Bad Exercise Values',
            'client_id': client_id,
            'exercises': exercises
        },
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'Validation failed'
    assert 'Sets must be between 1-10 for exercise' in data['details']
    assert 'Reps must be between 1-50 for exercise' in data['details']
    assert 'Weight must be between 0-500 kg for exercise' in data['details']
    assert 'Rest must be between 0-600 seconds for exercise' in data['details']


def test_create_program_validation_invalid_exercise_structure(app, client):
    trainer_id, role = create_trainer(app)
    client_id = create_client_record(app, trainer_id)
    exercise_ids = create_exercises(app, count=3)
    token = generate_auth_token(app, trainer_id, role)
    exercises = build_exercises_payload(exercise_ids)
    exercises.append({'sets': 3, 'reps': 10, 'weight_kg': 20, 'rest_seconds': 60})
    exercises.append({
        'exercise_id': 'bad-id',
        'sets': 3,
        'reps': 10,
        'weight_kg': 20,
        'rest_seconds': 60
    })

    response = client.post(
        '/api/programs',
        json={
            'name': 'Bad Exercise Structure',
            'client_id': client_id,
            'exercises': exercises
        },
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'Validation failed'
    assert 'Exercise ID is required' in data['details']
    assert 'Exercise ID must be an integer' in data['details']


def test_create_program_client_not_owned_returns_404(app, client):
    trainer_id, role = create_trainer(app)
    other_trainer_id, _ = create_trainer(app, email='trainer2@example.com')
    client_id = create_client_record(app, other_trainer_id, name='Other Client')
    exercise_ids = create_exercises(app, count=5)
    token = generate_auth_token(app, trainer_id, role)

    response = client.post(
        '/api/programs',
        json={
            'name': 'Wrong Client',
            'client_id': client_id,
            'exercises': build_exercises_payload(exercise_ids)
        },
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 404
    assert response.get_json() == {'error': 'Client not found or not owned by trainer'}


def test_create_program_invalid_exercise_id_returns_400(app, client):
    trainer_id, role = create_trainer(app)
    client_id = create_client_record(app, trainer_id)
    exercise_ids = create_exercises(app, count=4)
    exercise_ids.append(9999)
    token = generate_auth_token(app, trainer_id, role)

    response = client.post(
        '/api/programs',
        json={
            'name': 'Invalid Exercise',
            'client_id': client_id,
            'exercises': build_exercises_payload(exercise_ids)
        },
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 400
    assert response.get_json() == {'error': 'Exercise ID 9999 not found'}

    with app.app_context():
        assert Program.query.count() == 0
        assert ProgramExercise.query.count() == 0
