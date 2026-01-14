import pytest

from controllers.program_controller import validate_program_data


def build_exercise_payload(**overrides):
    payload = {
        'exercise_id': 1,
        'sets': 3,
        'reps': 10,
        'weight_kg': 20,
        'rest_seconds': 60,
    }
    payload.update(overrides)
    return payload


def test_validate_program_data_missing_name():
    data = {
        'name': '',
        'client_id': 10,
        'exercises': [build_exercise_payload() for _ in range(5)],
    }

    errors = validate_program_data(data)

    assert 'Program name must be 3-100 characters' in errors


def test_validate_program_data_name_too_long():
    data = {
        'name': 'x' * 101,
        'client_id': 10,
        'exercises': [build_exercise_payload() for _ in range(5)],
    }

    errors = validate_program_data(data)

    assert 'Program name must be 3-100 characters' in errors


def test_validate_program_data_missing_client():
    data = {
        'name': 'Valid Program',
        'exercises': [build_exercise_payload() for _ in range(5)],
    }

    errors = validate_program_data(data)

    assert 'Client is required' in errors


def test_validate_program_data_exercises_too_few():
    data = {
        'name': 'Too Few',
        'client_id': 10,
        'exercises': [build_exercise_payload() for _ in range(4)],
    }

    errors = validate_program_data(data)

    assert 'At least 5 exercises are required' in errors


def test_validate_program_data_exercises_too_many():
    data = {
        'name': 'Too Many',
        'client_id': 10,
        'exercises': [build_exercise_payload() for _ in range(21)],
    }

    errors = validate_program_data(data)

    assert 'Maximum 20 exercises allowed' in errors


def test_validate_program_data_invalid_exercise_structure():
    data = {
        'name': 'Bad Exercise Structure',
        'client_id': 10,
        'exercises': [
            build_exercise_payload(),
            'not-a-dict',
            build_exercise_payload(exercise_id='bad-id'),
        ],
    }

    errors = validate_program_data(data)

    assert 'Exercise must be an object' in errors
    assert 'Exercise ID must be an integer' in errors


def test_validate_program_data_invalid_exercise_values():
    data = {
        'name': 'Bad Exercise Values',
        'client_id': 10,
        'exercises': [
            build_exercise_payload(sets=0, reps=0, weight_kg=-1, rest_seconds=-1)
            for _ in range(5)
        ],
    }

    errors = validate_program_data(data)

    assert 'Sets must be between 1-10 for exercise' in errors
    assert 'Reps must be between 1-50 for exercise' in errors
    assert 'Weight must be between 0-500 kg for exercise' in errors
    assert 'Rest must be between 0-600 seconds for exercise' in errors


def test_validate_program_data_valid_payload():
    data = {
        'name': 'Strength Builder',
        'client_id': 10,
        'exercises': [build_exercise_payload() for _ in range(5)],
    }

    errors = validate_program_data(data)

    assert errors == []
