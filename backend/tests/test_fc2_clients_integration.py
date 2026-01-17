from models import db
from models.user import User
from models.client import Client


def _create_user(email, role, full_name="Test User", password="password123"):
    user = User(email=email, full_name=full_name, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def _auth_headers(user):
    from utils.jwt_utils import generate_token

    token = generate_token(user.id, user.role)
    return {"Authorization": f"Bearer {token}"}


def test_trainer_can_create_client(client):
    trainer = _create_user("trainer@example.com", "trainer", full_name="Trainer One")
    headers = _auth_headers(trainer)

    payload = {
        "name": "Alex Client",
        "age": 28,
        "fitness_level": "Intermediate",
        "goals": "Build strength and endurance"
    }
    response = client.post("/api/clients", json=payload, headers=headers)

    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == payload["name"]
    assert data["age"] == payload["age"]
    assert data["fitness_level"] == payload["fitness_level"]
    assert data["goals"] == payload["goals"]
    assert data["active"] is True
    assert data["user_id"] is None

    db_client = Client.query.filter_by(id=data["id"]).first()
    assert db_client is not None
    assert db_client.trainer_id == trainer.id
    assert db_client.name == payload["name"]


def test_trainer_can_list_clients(client):
    trainer = _create_user("trainer.list@example.com", "trainer", full_name="Trainer Two")
    headers = _auth_headers(trainer)

    other_trainer = _create_user("trainer.other@example.com", "trainer", full_name="Trainer Other")

    active_client = Client(
        trainer_id=trainer.id,
        name="Active Client",
        age=30,
        fitness_level="Beginner",
        goals="Improve flexibility and balance"
    )
    inactive_client = Client(
        trainer_id=trainer.id,
        name="Inactive Client",
        age=34,
        fitness_level="Advanced",
        goals="Run a marathon next year",
        active=False
    )
    db.session.add_all([active_client, inactive_client])
    db.session.commit()

    other_client = Client(
        trainer_id=other_trainer.id,
        name="Other Trainer Client",
        age=29,
        fitness_level="Intermediate",
        goals="Keep training plan consistent"
    )
    db.session.add(other_client)
    db.session.commit()

    response = client.get("/api/clients", headers=headers)

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "Active Client"
    assert data[0]["active"] is True
    assert "id" in data[0]
    assert "created_at" in data[0]


def test_create_client_missing_required_field_returns_400(client):
    trainer = _create_user("trainer.missing@example.com", "trainer", full_name="Trainer Three")
    headers = _auth_headers(trainer)

    payload = {
        "age": 22,
        "fitness_level": "Beginner",
        "goals": "Lose weight safely"
    }

    response = client.post("/api/clients", json=payload, headers=headers)

    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_create_client_invalid_field_format_returns_400(client):
    trainer = _create_user("trainer.invalid@example.com", "trainer", full_name="Trainer Four")
    headers = _auth_headers(trainer)

    payload = {
        "name": "Casey Client",
        "age": 27,
        "fitness_level": "Expert",
        "goals": "Increase endurance over time"
    }

    response = client.post("/api/clients", json=payload, headers=headers)

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Invalid fitness level"


def test_create_client_invalid_age_returns_400(client):
    trainer = _create_user("trainer.invalidage@example.com", "trainer", full_name="Trainer Six")
    headers = _auth_headers(trainer)

    payload = {
        "name": "Jordan Client",
        "age": 12,
        "fitness_level": "Beginner",
        "goals": "Improve overall fitness safely"
    }

    response = client.post("/api/clients", json=payload, headers=headers)

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Age must be between 16 and 100"


def test_create_client_short_goals_returns_400(client):
    trainer = _create_user("trainer.goals@example.com", "trainer", full_name="Trainer Seven")
    headers = _auth_headers(trainer)

    payload = {
        "name": "Morgan Client",
        "age": 26,
        "fitness_level": "Advanced",
        "goals": "Short"
    }

    response = client.post("/api/clients", json=payload, headers=headers)

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Goals must be at least 10 characters"


def test_create_client_links_existing_trainee_user(client):
    trainer = _create_user("trainer.link@example.com", "trainer", full_name="Trainer Eight")
    trainee = _create_user("trainee.link@example.com", "trainee", full_name="Trainee Link")
    headers = _auth_headers(trainer)

    payload = {
        "name": "Linked Client",
        "age": 31,
        "fitness_level": "Intermediate",
        "goals": "Build strength for upcoming race",
        "user_email": trainee.email
    }

    response = client.post("/api/clients", json=payload, headers=headers)

    assert response.status_code == 201
    data = response.get_json()
    assert data["user_id"] == trainee.id

    db_client = Client.query.filter_by(id=data["id"]).first()
    assert db_client.user_id == trainee.id


def test_update_nonexistent_client_returns_404(client):
    trainer = _create_user("trainer.notfound@example.com", "trainer", full_name="Trainer Five")
    headers = _auth_headers(trainer)

    response = client.put("/api/clients/9999", json={"name": "New Name"}, headers=headers)

    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Client not found"


def test_trainer_can_update_client_and_persist_changes(client):
    trainer = _create_user("trainer.update@example.com", "trainer", full_name="Trainer Nine")
    headers = _auth_headers(trainer)

    client_record = Client(
        trainer_id=trainer.id,
        name="Original Name",
        age=29,
        fitness_level="Beginner",
        goals="Increase mobility and stamina"
    )
    db.session.add(client_record)
    db.session.commit()

    payload = {
        "name": "Updated Name",
        "age": 31,
        "fitness_level": "Intermediate",
        "goals": "Improve mobility and build endurance"
    }

    response = client.put(f"/api/clients/{client_record.id}", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == payload["name"]
    assert data["age"] == payload["age"]
    assert data["fitness_level"] == payload["fitness_level"]
    assert data["goals"] == payload["goals"]

    db_client = Client.query.get(client_record.id)
    assert db_client.name == payload["name"]
    assert db_client.age == payload["age"]
    assert db_client.fitness_level == payload["fitness_level"]
    assert db_client.goals == payload["goals"]


def test_update_client_invalid_age_returns_400(client):
    trainer = _create_user("trainer.update.invalid@example.com", "trainer", full_name="Trainer Ten")
    headers = _auth_headers(trainer)

    client_record = Client(
        trainer_id=trainer.id,
        name="Age Test",
        age=25,
        fitness_level="Advanced",
        goals="Improve overall performance metrics"
    )
    db.session.add(client_record)
    db.session.commit()

    response = client.put(
        f"/api/clients/{client_record.id}",
        json={"age": 10},
        headers=headers
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Age must be between 16 and 100"


def test_trainer_cannot_update_other_trainers_client(client):
    trainer = _create_user("trainer.owner@example.com", "trainer", full_name="Trainer Owner")
    other_trainer = _create_user("trainer.otherowner@example.com", "trainer", full_name="Trainer Other")
    headers = _auth_headers(trainer)

    other_client = Client(
        trainer_id=other_trainer.id,
        name="Other Client",
        age=40,
        fitness_level="Beginner",
        goals="Maintain healthy routine"
    )
    db.session.add(other_client)
    db.session.commit()

    response = client.put(
        f"/api/clients/{other_client.id}",
        json={"name": "Unauthorized Update"},
        headers=headers
    )

    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Client not found"


def test_trainer_can_deactivate_client(client):
    trainer = _create_user("trainer.deactivate@example.com", "trainer", full_name="Trainer Eleven")
    headers = _auth_headers(trainer)

    client_record = Client(
        trainer_id=trainer.id,
        name="Deactivate Client",
        age=33,
        fitness_level="Intermediate",
        goals="Maintain conditioning for season"
    )
    db.session.add(client_record)
    db.session.commit()

    response = client.post(f"/api/clients/{client_record.id}/deactivate", headers=headers)

    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Client deactivated"

    db_client = Client.query.get(client_record.id)
    assert db_client.active is False


def test_deactivate_client_not_found_returns_404(client):
    trainer = _create_user("trainer.deactivate.missing@example.com", "trainer", full_name="Trainer Twelve")
    headers = _auth_headers(trainer)

    response = client.post("/api/clients/99999/deactivate", headers=headers)

    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Client not found"


def test_trainer_cannot_deactivate_other_trainers_client(client):
    trainer = _create_user("trainer.deactivate.owner@example.com", "trainer", full_name="Trainer Owner")
    other_trainer = _create_user("trainer.deactivate.other@example.com", "trainer", full_name="Trainer Other")
    headers = _auth_headers(trainer)

    other_client = Client(
        trainer_id=other_trainer.id,
        name="Other Trainer Client",
        age=38,
        fitness_level="Intermediate",
        goals="Improve speed and agility"
    )
    db.session.add(other_client)
    db.session.commit()

    response = client.post(f"/api/clients/{other_client.id}/deactivate", headers=headers)

    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Client not found"

    db_client = Client.query.get(other_client.id)
    assert db_client.active is True


def test_trainee_can_fetch_own_client_profile(client):
    trainer = _create_user("trainer.profile@example.com", "trainer", full_name="Trainer Thirteen")
    trainee = _create_user("trainee.profile@example.com", "trainee", full_name="Trainee Profile")
    headers = _auth_headers(trainee)

    client_record = Client(
        trainer_id=trainer.id,
        user_id=trainee.id,
        name="Profile Client",
        age=24,
        fitness_level="Beginner",
        goals="Build confidence in workouts"
    )
    db.session.add(client_record)
    db.session.commit()

    response = client.get("/api/clients/my", headers=headers)

    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == client_record.id
    assert data["user_id"] == trainee.id
    assert data["name"] == "Profile Client"


def test_trainee_without_client_profile_gets_404(client):
    trainee = _create_user("trainee.empty@example.com", "trainee", full_name="Trainee Empty")
    headers = _auth_headers(trainee)

    response = client.get("/api/clients/my", headers=headers)

    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "No client profile found"
