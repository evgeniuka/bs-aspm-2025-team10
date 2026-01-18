from models import db
from models.client import Client
from models.exercise import Exercise
from models.program import Program, ProgramExercise
from models.user import User
from utils.jwt_utils import generate_token


def _create_user(db_session, email="trainer@example.com", role="trainer"):
    user = User(
        email=email,
        full_name="Trainer User",
        role=role,
    )
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()
    return user


def _create_client_record(db_session, trainer_id, name="Test Client"):
    client_record = Client(
        trainer_id=trainer_id,
        name=name,
        age=30,
        fitness_level="Beginner",
        goals="Build strength",
        active=True,
    )
    db_session.add(client_record)
    db_session.commit()
    return client_record


def _create_exercises(db_session, count=5):
    exercises = []
    for idx in range(count):
        exercise = Exercise(
            name=f"Exercise {idx}",
            category="upper_body",
            description=f"Description {idx}",
            equipment="bodyweight",
            difficulty="beginner",
        )
        db_session.add(exercise)
        exercises.append(exercise)
    db_session.commit()
    return exercises


def _build_exercises_payload(exercise_ids, overrides=None):
    overrides = overrides or {}
    payload = []
    for exercise_id in exercise_ids:
        entry = {
            "exercise_id": exercise_id,
            "sets": 3,
            "reps": 10,
            "weight_kg": 20,
            "rest_seconds": 60,
        }
        entry.update(overrides)
        payload.append(entry)
    return payload


def _auth_headers(user):
    token = generate_token(user.id, user.role)
    return {"Authorization": f"Bearer {token}"}


def test_create_program_success_persists(client, db_session):
    trainer = _create_user(db_session)
    client_record = _create_client_record(db_session, trainer.id)
    exercises = _create_exercises(db_session, count=5)
    headers = _auth_headers(trainer)

    payload = {
        "name": "Strength Builder",
        "client_id": client_record.id,
        "notes": "Focus on form.",
        "exercises": _build_exercises_payload([exercise.id for exercise in exercises]),
    }

    response = client.post(
        "/api/programs",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 201

    data = response.get_json() or {}
    assert data.get("program_id") is not None
    assert data.get("id") == data["program_id"]
    assert data.get("message") == "Program created"

    program = db.session.get(Program, data["program_id"])
    assert program is not None
    assert program.name == payload["name"]
    assert program.client_id == payload["client_id"]
    assert program.trainer_id == trainer.id
    assert program.notes == payload["notes"]

    program_exercises = ProgramExercise.query.filter_by(program_id=program.id).all()
    assert len(program_exercises) == len(payload["exercises"])
    orders = sorted(pe.order for pe in program_exercises)
    assert orders == list(range(len(payload["exercises"])))
    first_ex = program_exercises[0]
    assert first_ex.sets == payload["exercises"][0]["sets"]
    assert first_ex.reps == payload["exercises"][0]["reps"]
    assert first_ex.weight_kg == payload["exercises"][0]["weight_kg"]
    assert first_ex.rest_seconds == payload["exercises"][0]["rest_seconds"]


def test_create_program_missing_token_returns_401(client, db_session):
    trainer = _create_user(db_session)
    client_record = _create_client_record(db_session, trainer.id)
    exercises = _create_exercises(db_session, count=5)

    response = client.post(
        "/api/programs",
        json={
            "name": "No Token",
            "client_id": client_record.id,
            "exercises": _build_exercises_payload([exercise.id for exercise in exercises]),
        },
    )

    assert response.status_code == 401
    assert response.get_json() == {"error": "Token is missing"}


def test_create_program_invalid_token_format_returns_401(client, db_session):
    trainer = _create_user(db_session)
    client_record = _create_client_record(db_session, trainer.id)
    exercises = _create_exercises(db_session, count=5)

    response = client.post(
        "/api/programs",
        json={
            "name": "Bad Token",
            "client_id": client_record.id,
            "exercises": _build_exercises_payload([exercise.id for exercise in exercises]),
        },
        headers={"Authorization": "Bearer"},
    )

    assert response.status_code == 401
    assert response.get_json() == {"error": "Invalid token format"}


def test_create_program_invalid_token_returns_401(client, db_session):
    trainer = _create_user(db_session)
    client_record = _create_client_record(db_session, trainer.id)
    exercises = _create_exercises(db_session, count=5)

    response = client.post(
        "/api/programs",
        json={
            "name": "Expired Token",
            "client_id": client_record.id,
            "exercises": _build_exercises_payload([exercise.id for exercise in exercises]),
        },
        headers={"Authorization": "Bearer invalid.token.value"},
    )

    assert response.status_code == 401
    assert response.get_json() == {"error": "Token is invalid or expired"}


def test_create_program_validation_missing_name(client, db_session):
    trainer = _create_user(db_session)
    client_record = _create_client_record(db_session, trainer.id)
    exercises = _create_exercises(db_session, count=5)
    headers = _auth_headers(trainer)

    response = client.post(
        "/api/programs",
        json={
            "name": "",
            "client_id": client_record.id,
            "exercises": _build_exercises_payload([exercise.id for exercise in exercises]),
        },
        headers=headers,
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Validation failed"
    assert "Program name must be 3-100 characters" in data["details"]


def test_create_program_validation_missing_client(client, db_session):
    trainer = _create_user(db_session)
    exercises = _create_exercises(db_session, count=5)
    headers = _auth_headers(trainer)

    response = client.post(
        "/api/programs",
        json={
            "name": "No Client",
            "exercises": _build_exercises_payload([exercise.id for exercise in exercises]),
        },
        headers=headers,
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Validation failed"
    assert "Client is required" in data["details"]


def test_create_program_validation_exercises_too_few(client, db_session):
    trainer = _create_user(db_session)
    client_record = _create_client_record(db_session, trainer.id)
    exercises = _create_exercises(db_session, count=4)
    headers = _auth_headers(trainer)

    response = client.post(
        "/api/programs",
        json={
            "name": "Too Few Exercises",
            "client_id": client_record.id,
            "exercises": _build_exercises_payload([exercise.id for exercise in exercises]),
        },
        headers=headers,
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Validation failed"
    assert "At least 5 exercises are required" in data["details"]


def test_create_program_validation_exercises_too_many(client, db_session):
    trainer = _create_user(db_session)
    client_record = _create_client_record(db_session, trainer.id)
    headers = _auth_headers(trainer)

    response = client.post(
        "/api/programs",
        json={
            "name": "Too Many Exercises",
            "client_id": client_record.id,
            "exercises": _build_exercises_payload(list(range(1, 22))),
        },
        headers=headers,
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Validation failed"
    assert "Maximum 20 exercises allowed" in data["details"]


def test_create_program_validation_invalid_exercise_values(client, db_session):
    trainer = _create_user(db_session)
    client_record = _create_client_record(db_session, trainer.id)
    exercises = _create_exercises(db_session, count=5)
    headers = _auth_headers(trainer)
    exercise_payload = _build_exercises_payload([exercise.id for exercise in exercises])
    exercise_payload[0].update(
        {
            "sets": 0,
            "reps": 0,
            "weight_kg": -1,
            "rest_seconds": -1,
        }
    )

    response = client.post(
        "/api/programs",
        json={
            "name": "Bad Exercise Values",
            "client_id": client_record.id,
            "exercises": exercise_payload,
        },
        headers=headers,
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Validation failed"
    assert "Sets must be between 1-10 for exercise" in data["details"]
    assert "Reps must be between 1-50 for exercise" in data["details"]
    assert "Weight must be between 0-500 kg for exercise" in data["details"]
    assert "Rest must be between 0-600 seconds for exercise" in data["details"]


def test_create_program_validation_invalid_exercise_structure(client, db_session):
    trainer = _create_user(db_session)
    client_record = _create_client_record(db_session, trainer.id)
    exercises = _create_exercises(db_session, count=3)
    headers = _auth_headers(trainer)
    exercise_payload = _build_exercises_payload([exercise.id for exercise in exercises])
    exercise_payload.append(
        {"sets": 3, "reps": 10, "weight_kg": 20, "rest_seconds": 60}
    )
    exercise_payload.append(
        {
            "exercise_id": "bad-id",
            "sets": 3,
            "reps": 10,
            "weight_kg": 20,
            "rest_seconds": 60,
        }
    )

    response = client.post(
        "/api/programs",
        json={
            "name": "Bad Exercise Structure",
            "client_id": client_record.id,
            "exercises": exercise_payload,
        },
        headers=headers,
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Validation failed"
    assert "Exercise ID is required" in data["details"]
    assert "Exercise ID must be an integer" in data["details"]


def test_create_program_client_not_owned_returns_404(client, db_session):
    trainer = _create_user(db_session)
    other_trainer = _create_user(db_session, email="trainer2@example.com")
    client_record = _create_client_record(db_session, other_trainer.id, name="Other Client")
    exercises = _create_exercises(db_session, count=5)
    headers = _auth_headers(trainer)

    response = client.post(
        "/api/programs",
        json={
            "name": "Wrong Client",
            "client_id": client_record.id,
            "exercises": _build_exercises_payload([exercise.id for exercise in exercises]),
        },
        headers=headers,
    )

    assert response.status_code == 404
    assert response.get_json() == {"error": "Client not found or not owned by trainer"}


def test_create_program_invalid_exercise_id_returns_400(client, db_session):
    trainer = _create_user(db_session)
    client_record = _create_client_record(db_session, trainer.id)
    exercises = _create_exercises(db_session, count=4)
    headers = _auth_headers(trainer)
    exercise_ids = [exercise.id for exercise in exercises]
    exercise_ids.append(9999)

    response = client.post(
        "/api/programs",
        json={
            "name": "Invalid Exercise",
            "client_id": client_record.id,
            "exercises": _build_exercises_payload(exercise_ids),
        },
        headers=headers,
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Exercise ID 9999 not found"}

    assert Program.query.count() == 0
    assert ProgramExercise.query.count() == 0


def test_get_programs_for_client_returns_assigned_program(client, db_session):
    trainer = _create_user(db_session)
    client_record = _create_client_record(db_session, trainer.id)
    exercises = _create_exercises(db_session, count=5)
    headers = _auth_headers(trainer)
    payload = {
        "name": "Client Program",
        "client_id": client_record.id,
        "notes": "Structured plan.",
        "exercises": _build_exercises_payload([exercise.id for exercise in exercises]),
    }

    create_response = client.post(
        "/api/programs",
        json=payload,
        headers=headers,
    )

    assert create_response.status_code == 201

    response = client.get(
        f"/api/programs?client_id={client_record.id}",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    program = data[0]
    assert program["id"] == create_response.get_json()["program_id"]
    assert program["client_id"] == client_record.id
    assert program["trainer_id"] == trainer.id
    assert program["name"] == payload["name"]
    assert program["notes"] == payload["notes"]
    exercise_list = program["exercises"]
    assert len(exercise_list) == len(payload["exercises"])
    assert [exercise["order"] for exercise in exercise_list] == list(
        range(len(payload["exercises"]))
    )
    assert exercise_list[0]["sets"] == payload["exercises"][0]["sets"]
    assert exercise_list[0]["reps"] == payload["exercises"][0]["reps"]
    assert exercise_list[0]["weight_kg"] == payload["exercises"][0]["weight_kg"]
    assert exercise_list[0]["rest_seconds"] == payload["exercises"][0]["rest_seconds"]


def test_get_programs_without_client_id_returns_trainer_programs(client, db_session):
    trainer = _create_user(db_session)
    client_record = _create_client_record(db_session, trainer.id)
    exercises = _create_exercises(db_session, count=5)
    headers = _auth_headers(trainer)

    payload = {
        "name": "Trainer Programs",
        "client_id": client_record.id,
        "notes": "Top picks",
        "exercises": _build_exercises_payload([exercise.id for exercise in exercises]),
    }

    create_response = client.post(
        "/api/programs",
        json=payload,
        headers=headers,
    )

    assert create_response.status_code == 201

    response = client.get(
        "/api/programs",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["name"] == payload["name"]


def test_get_programs_client_not_owned_returns_404(client, db_session):
    trainer = _create_user(db_session)
    other_trainer = _create_user(db_session, email="trainer3@example.com")
    client_record = _create_client_record(db_session, other_trainer.id, name="Other Client")
    headers = _auth_headers(trainer)

    response = client.get(
        f"/api/programs?client_id={client_record.id}",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.get_json() == {"error": "Client not found or not owned by trainer"}
