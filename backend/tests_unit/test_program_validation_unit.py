import copy

from controllers import program_controller


def _base_payload():
    return {
        "name": "Strength Plan",
        "client_id": 10,
        "exercises": [
            {
                "exercise_id": 1,
                "sets": 3,
                "reps": 10,
                "weight_kg": 50,
                "rest_seconds": 60,
            }
            for _ in range(5)
        ],
    }


def test_validate_program_data_requires_name():
    payload = _base_payload()
    payload["name"] = ""
    errors = program_controller.validate_program_data(payload)
    assert "Program name must be 3-100 characters" in errors


def test_validate_program_data_rejects_short_name():
    payload = _base_payload()
    payload["name"] = "ab"
    errors = program_controller.validate_program_data(payload)
    assert "Program name must be 3-100 characters" in errors


def test_validate_program_data_rejects_long_name():
    payload = _base_payload()
    payload["name"] = "a" * 101
    errors = program_controller.validate_program_data(payload)
    assert "Program name must be 3-100 characters" in errors


def test_validate_program_data_requires_client_id():
    payload = _base_payload()
    payload["client_id"] = None
    errors = program_controller.validate_program_data(payload)
    assert "Client is required" in errors


def test_validate_program_data_enforces_exercise_count_min():
    payload = _base_payload()
    payload["exercises"] = payload["exercises"][:4]
    errors = program_controller.validate_program_data(payload)
    assert "At least 5 exercises are required" in errors


def test_validate_program_data_enforces_exercise_count_max():
    payload = _base_payload()
    payload["exercises"] = payload["exercises"] * 5
    errors = program_controller.validate_program_data(payload)
    assert "Maximum 20 exercises allowed" in errors


def test_validate_program_data_validates_exercise_fields():
    payload = _base_payload()
    invalid_exercise = copy.deepcopy(payload["exercises"][0])
    invalid_exercise.update({"sets": 0, "reps": 51, "weight_kg": -5, "rest_seconds": 601})
    payload["exercises"] = [invalid_exercise] * 5
    errors = program_controller.validate_program_data(payload)
    assert "Sets must be between 1-10 for exercise" in errors
    assert "Reps must be between 1-50 for exercise" in errors
    assert "Weight must be between 0-500 kg for exercise" in errors
    assert "Rest must be between 0-600 seconds for exercise" in errors


def test_validate_program_data_accepts_valid_payload():
    payload = _base_payload()
    errors = program_controller.validate_program_data(payload)
    assert errors == []
