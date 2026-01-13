import pytest

from models import db
from models.client import Client
from models.exercise import Exercise
from models.user import User
from utils.jwt_utils import generate_token


def create_user(app, email, role="trainer", password="password123", full_name="Test User"):
    with app.app_context():
        user = User(email=email, full_name=full_name, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user.id


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_auth_register_login_me_logout(client, app):
    register_payload = {
        "email": "newtrainer@example.com",
        "password": "password123",
        "full_name": "New Trainer",
        "role": "trainer",
    }
    register_response = client.post("/api/auth/register", json=register_payload)
    assert register_response.status_code == 201
    register_data = register_response.get_json()
    assert isinstance(register_data["token"], str)
    assert register_data["user"]["email"] == register_payload["email"]

    login_response = client.post(
        "/api/auth/login",
        json={"email": register_payload["email"], "password": register_payload["password"]},
    )
    assert login_response.status_code == 200
    login_data = login_response.get_json()
    assert isinstance(login_data["token"], str)
    assert login_data["user"]["email"] == register_payload["email"]

    me_response = client.get("/api/auth/me", headers=auth_headers(login_data["token"]))
    assert me_response.status_code == 200
    assert me_response.get_json()["email"] == register_payload["email"]

    logout_response = client.post(
        "/api/auth/logout",
        headers=auth_headers(login_data["token"]),
    )
    assert logout_response.status_code == 200
    assert logout_response.get_json()["message"] == "Logged out successfully"


def test_client_crud_flow(client, app, trainer_token):
    trainee_email = "trainee@example.com"
    create_user(app, trainee_email, role="trainee", full_name="Trainee User")

    create_payload = {
        "name": "Client One",
        "age": 30,
        "fitness_level": "Beginner",
        "goals": "Build strength and stamina",
        "user_email": trainee_email,
    }
    create_response = client.post(
        "/api/clients",
        json=create_payload,
        headers=auth_headers(trainer_token["token"]),
    )
    assert create_response.status_code == 201
    created_client = create_response.get_json()
    assert created_client["name"] == create_payload["name"]
    assert created_client["user_id"] is not None

    list_response = client.get(
        "/api/clients",
        headers=auth_headers(trainer_token["token"]),
    )
    assert list_response.status_code == 200
    clients = list_response.get_json()
    assert any(item["id"] == created_client["id"] for item in clients)

    update_response = client.put(
        f"/api/clients/{created_client['id']}",
        json={"name": "Client One Updated"},
        headers=auth_headers(trainer_token["token"]),
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["name"] == "Client One Updated"

    deactivate_response = client.post(
        f"/api/clients/{created_client['id']}/deactivate",
        headers=auth_headers(trainer_token["token"]),
    )
    assert deactivate_response.status_code == 200
    assert deactivate_response.get_json()["message"] == "Client deactivated"


def test_get_my_client_for_trainee(client, app):
    trainer_id = create_user(app, "trainer2@example.com", role="trainer")
    trainee_id = create_user(app, "trainee2@example.com", role="trainee")

    with app.app_context():
        client_model = Client(
            trainer_id=trainer_id,
            user_id=trainee_id,
            name="Linked Client",
            age=28,
            fitness_level="Intermediate",
            goals="Improve endurance",
        )
        db.session.add(client_model)
        db.session.commit()

    token = generate_token(trainee_id, "trainee")
    response = client.get("/api/clients/my", headers=auth_headers(token))
    assert response.status_code == 200
    assert response.get_json()["user_id"] == trainee_id


def test_exercises_filters(client, app):
    with app.app_context():
        db.session.add_all(
            [
                Exercise(
                    name="Bench Press",
                    category="upper_body",
                    description="Bench press",
                    equipment="barbell",
                    difficulty="intermediate",
                ),
                Exercise(
                    name="Plank",
                    category="core",
                    description="Plank hold",
                    equipment="bodyweight",
                    difficulty="beginner",
                ),
            ]
        )
        db.session.commit()

    response = client.get("/api/exercises?search=bench")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["name"] == "Bench Press"

    response = client.get("/api/exercises?category=core")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["name"] == "Plank"


def test_program_create_and_list(client, app, trainer_token):
    with app.app_context():
        client_model = Client(
            trainer_id=trainer_token["user_id"],
            user_id=None,
            name="Program Client",
            age=32,
            fitness_level="Beginner",
            goals="Gain muscle",
        )
        db.session.add(client_model)
        db.session.flush()

        exercise_ids = []
        for idx in range(5):
            exercise = Exercise(
                name=f"Exercise {idx}",
                category="full_body",
                description="Desc",
                equipment="bodyweight",
                difficulty="beginner",
            )
            db.session.add(exercise)
            db.session.flush()
            exercise_ids.append(exercise.id)

        db.session.commit()
        client_id = client_model.id

    program_payload = {
        "name": "Starter Program",
        "client_id": client_id,
        "notes": "Notes",
        "exercises": [
            {
                "exercise_id": exercise_id,
                "sets": 3,
                "reps": 10,
                "weight_kg": 0,
                "rest_seconds": 60,
            }
            for exercise_id in exercise_ids
        ],
    }

    create_response = client.post(
        "/api/programs",
        json=program_payload,
        headers=auth_headers(trainer_token["token"]),
    )
    assert create_response.status_code == 201
    create_data = create_response.get_json()
    assert isinstance(create_data["program_id"], int)

    list_response = client.get(
        f"/api/programs?client_id={client_id}",
        headers=auth_headers(trainer_token["token"]),
    )
    assert list_response.status_code == 200
    programs = list_response.get_json()
    assert len(programs) == 1
    assert programs[0]["name"] == "Starter Program"
    assert len(programs[0]["exercises"]) == 5


def test_program_requires_client_id(client, trainer_token):
    response = client.get(
        "/api/programs",
        headers=auth_headers(trainer_token["token"]),
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "client_id is required"
