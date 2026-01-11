import pytest

from models import db
from models.client import Client
from models.exercise import Exercise
from models.program import Program, ProgramExercise
from models.user import User
from utils.jwt_utils import generate_token


def create_user(email, role="trainer", is_active=True):
    user = User(
        email=email,
        full_name="Test User",
        role=role,
        is_active=is_active,
    )
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


def auth_headers(app, user):
    with app.app_context():
        token = generate_token(user.id, user.role)
    return {"Authorization": f"Bearer {token}"}


def create_client(trainer_id, user_id=None, name="Client Name"):
    client = Client(
        trainer_id=trainer_id,
        user_id=user_id,
        name=name,
        age=30,
        fitness_level="Beginner",
        goals="Improve strength and endurance",
    )
    db.session.add(client)
    db.session.commit()
    return client


def create_exercise(name):
    exercise = Exercise(
        name=name,
        category="upper_body",
        description="Test description",
        equipment="bodyweight",
        difficulty="beginner",
    )
    db.session.add(exercise)
    db.session.commit()
    return exercise


def test_auth_register_login_and_me(client, app):
    register_payload = {
        "email": "trainer@example.com",
        "password": "password123",
        "full_name": "Trainer One",
        "role": "trainer",
    }
    register_response = client.post("/api/auth/register", json=register_payload)
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={"email": "trainer@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    token = login_response.get_json()["token"]

    me_response = client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 200


@pytest.mark.parametrize(
    "payload,expected_message",
    [
        ({"email": "missing-fields@example.com"}, "Missing required fields"),
        (
            {
                "email": "bad-role@example.com",
                "password": "password123",
                "full_name": "Bad Role",
                "role": "admin",
            },
            "Invalid role. Must be trainer or trainee",
        ),
        (
            {
                "email": "short-pass@example.com",
                "password": "short",
                "full_name": "Short Pass",
                "role": "trainer",
            },
            "Password must be at least 8 characters long",
        ),
    ],
)
def test_auth_register_invalid_payloads(client, payload, expected_message):
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    assert response.get_json()["error"] == expected_message


def test_auth_register_duplicate_email(client, app):
    with app.app_context():
        create_user("dupe@example.com")

    response = client.post(
        "/api/auth/register",
        json={
            "email": "dupe@example.com",
            "password": "password123",
            "full_name": "Dupe User",
            "role": "trainer",
        },
    )
    assert response.status_code == 409


def test_auth_login_error_paths(client, app):
    with app.app_context():
        active_user = create_user("active@example.com")
        inactive_user = create_user("inactive@example.com", is_active=False)

    response = client.post(
        "/api/auth/login",
        json={"email": active_user.email, "password": "wrongpass"},
    )
    assert response.status_code == 401

    response = client.post(
        "/api/auth/login",
        json={"email": inactive_user.email, "password": "password123"},
    )
    assert response.status_code == 403


def test_auth_me_user_not_found(client, app):
    with app.app_context():
        token = generate_token(9999, "trainer")

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404


def test_auth_logout(client, app):
    with app.app_context():
        user = create_user("logout@example.com")
    response = client.post("/api/auth/logout", headers=auth_headers(app, user))
    assert response.status_code == 200


def test_client_crud_and_my_client(client, app):
    with app.app_context():
        trainer = create_user("trainer@example.com")
        trainee = create_user("trainee@example.com", role="trainee")
        linked_client = create_client(trainer.id, user_id=trainee.id)

    response = client.get("/api/clients", headers=auth_headers(app, trainer))
    assert response.status_code == 200
    assert any(item["id"] == linked_client.id for item in response.get_json())

    create_response = client.post(
        "/api/clients",
        headers=auth_headers(app, trainer),
        json={
            "name": "New Client",
            "age": 35,
            "fitness_level": "Intermediate",
            "goals": "Build muscle and lose fat",
        },
    )
    assert create_response.status_code == 201

    invalid_response = client.post(
        "/api/clients",
        headers=auth_headers(app, trainer),
        json={
            "name": "A",
            "age": 10,
            "fitness_level": "Invalid",
            "goals": "short",
        },
    )
    assert invalid_response.status_code == 400

    update_response = client.put(
        f"/api/clients/{linked_client.id}",
        headers=auth_headers(app, trainer),
        json={"age": 10},
    )
    assert update_response.status_code == 400

    deactivate_response = client.post(
        f"/api/clients/{linked_client.id}/deactivate",
        headers=auth_headers(app, trainer),
    )
    assert deactivate_response.status_code == 200
    with app.app_context():
        refreshed = Client.query.get(linked_client.id)
        assert refreshed.active is False

    my_client_response = client.get(
        "/api/clients/my", headers=auth_headers(app, trainee)
    )
    assert my_client_response.status_code == 404


def test_client_my_client_happy_path(client, app):
    with app.app_context():
        trainer = create_user("trainer2@example.com")
        trainee = create_user("trainee2@example.com", role="trainee")
        client_profile = create_client(trainer.id, user_id=trainee.id)

    response = client.get("/api/clients/my", headers=auth_headers(app, trainee))
    assert response.status_code == 200
    assert response.get_json()["id"] == client_profile.id


def test_program_create_and_get(client, app):
    with app.app_context():
        trainer = create_user("prog-trainer@example.com")
        other_trainer = create_user("other-trainer@example.com")
        client_profile = create_client(trainer.id)
        exercises = [create_exercise(f"Exercise {i}") for i in range(5)]

    validation_response = client.post(
        "/api/programs",
        headers=auth_headers(app, trainer),
        json={
            "name": "Short Program",
            "client_id": client_profile.id,
            "exercises": [
                {
                    "exercise_id": exercises[0].id,
                    "sets": 3,
                    "reps": 10,
                    "weight_kg": 20,
                    "rest_seconds": 60,
                }
            ],
        },
    )
    assert validation_response.status_code == 400

    not_owned_response = client.post(
        "/api/programs",
        headers=auth_headers(app, other_trainer),
        json={
            "name": "Program",
            "client_id": client_profile.id,
            "exercises": [
                {
                    "exercise_id": exercises[0].id,
                    "sets": 3,
                    "reps": 10,
                    "weight_kg": 20,
                    "rest_seconds": 60,
                }
            ]
            * 5,
        },
    )
    assert not_owned_response.status_code == 404

    missing_exercise_response = client.post(
        "/api/programs",
        headers=auth_headers(app, trainer),
        json={
            "name": "Program",
            "client_id": client_profile.id,
            "exercises": [
                {
                    "exercise_id": 9999,
                    "sets": 3,
                    "reps": 10,
                    "weight_kg": 20,
                    "rest_seconds": 60,
                }
            ]
            * 5,
        },
    )
    assert missing_exercise_response.status_code == 400

    create_response = client.post(
        "/api/programs",
        headers=auth_headers(app, trainer),
        json={
            "name": "Strength Program",
            "client_id": client_profile.id,
            "exercises": [
                {
                    "exercise_id": exercise.id,
                    "sets": 3,
                    "reps": 10,
                    "weight_kg": 20,
                    "rest_seconds": 60,
                }
                for exercise in exercises
            ],
        },
    )
    assert create_response.status_code == 201

    with app.app_context():
        assert Program.query.count() == 1
        assert ProgramExercise.query.count() == 5

    missing_client_id_response = client.get(
        "/api/programs", headers=auth_headers(app, trainer)
    )
    assert missing_client_id_response.status_code == 400

    not_found_response = client.get(
        "/api/programs?client_id=9999", headers=auth_headers(app, trainer)
    )
    assert not_found_response.status_code == 404

    get_response = client.get(
        f"/api/programs?client_id={client_profile.id}",
        headers=auth_headers(app, trainer),
    )
    assert get_response.status_code == 200
    assert get_response.get_json()[0]["name"] == "Strength Program"


def test_exercise_filters(client, app):
    with app.app_context():
        create_exercise("Bench Press")
        create_exercise("Push Up")
        create_exercise("Deadlift")
        exercise = Exercise.query.filter_by(name="Deadlift").first()
        exercise.category = "lower_body"
        exercise.difficulty = "advanced"
        db.session.commit()

    response = client.get("/api/exercises?search=bench")
    assert response.status_code == 200
    assert any(item["name"] == "Bench Press" for item in response.get_json())

    response = client.get("/api/exercises?category=lower_body")
    assert response.status_code == 200
    assert all(item["category"] == "lower_body" for item in response.get_json())

    response = client.get("/api/exercises?difficulty=advanced")
    assert response.status_code == 200
    assert all(item["difficulty"] == "advanced" for item in response.get_json())
