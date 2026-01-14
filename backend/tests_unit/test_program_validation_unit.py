from controllers import program_controller


def test_validate_program_data_requires_name():
    errors = program_controller.validate_program_data({"client_id": 1, "exercises": [{}] * 5})

    assert "Program name must be 3-100 characters" in errors


def test_validate_program_data_requires_client_id():
    errors = program_controller.validate_program_data({"name": "Plan", "exercises": [{}] * 5})

    assert "Client is required" in errors


def test_validate_program_data_requires_min_exercises():
    errors = program_controller.validate_program_data(
        {
            "name": "Plan",
            "client_id": 1,
            "exercises": [
                {"sets": 3, "reps": 10, "weight_kg": 0, "rest_seconds": 60}
                for _ in range(4)
            ],
        }
    )

    assert "At least 5 exercises are required" in errors


def test_validate_program_data_sets_out_of_range():
    errors = program_controller.validate_program_data(
        {
            "name": "Plan",
            "client_id": 1,
            "exercises": [
                {"sets": 0, "reps": 10, "weight_kg": 0, "rest_seconds": 60}
                for _ in range(5)
            ],
        }
    )

    assert "Sets must be between 1-10 for exercise" in errors


def test_validate_program_data_reps_out_of_range():
    errors = program_controller.validate_program_data(
        {
            "name": "Plan",
            "client_id": 1,
            "exercises": [
                {"sets": 3, "reps": 0, "weight_kg": 0, "rest_seconds": 60}
                for _ in range(5)
            ],
        }
    )

    assert "Reps must be between 1-50 for exercise" in errors


def test_validate_program_data_weight_out_of_range():
    errors = program_controller.validate_program_data(
        {
            "name": "Plan",
            "client_id": 1,
            "exercises": [
                {"sets": 3, "reps": 10, "weight_kg": 600, "rest_seconds": 60}
                for _ in range(5)
            ],
        }
    )

    assert "Weight must be between 0-500 kg for exercise" in errors


def test_validate_program_data_rest_out_of_range():
    errors = program_controller.validate_program_data(
        {
            "name": "Plan",
            "client_id": 1,
            "exercises": [
                {"sets": 3, "reps": 10, "weight_kg": 0, "rest_seconds": 700}
                for _ in range(5)
            ],
        }
    )

    assert "Rest must be between 0-600 seconds for exercise" in errors
