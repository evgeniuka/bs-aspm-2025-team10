from app.auth import hash_password
from app.models import FitnessLevel, Program, User, UserRole


def _login(client, email: str, password: str = "password123"):
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200


def test_trainer_can_create_update_and_archive_client(client, seeded_trainer):
    _login(client, seeded_trainer.email)

    create_response = client.post(
        "/api/v1/clients",
        json={
            "name": "New Client",
            "age": 36,
            "fitness_level": "Beginner",
            "goals": "Build a consistent twice-weekly training routine.",
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()

    update_response = client.patch(
        f"/api/v1/clients/{created['id']}",
        json={
            "name": "New Client Updated",
            "age": 37,
            "fitness_level": "Intermediate",
            "goals": "Progress strength while keeping conditioning steady.",
        },
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["name"] == "New Client Updated"
    assert updated["age"] == 37
    assert updated["fitness_level"] == "Intermediate"

    archive_response = client.delete(f"/api/v1/clients/{created['id']}")
    assert archive_response.status_code == 204
    listed = client.get("/api/v1/clients").json()
    assert all(item["id"] != created["id"] for item in listed)


def test_trainer_cannot_update_other_trainer_client(client, db, seeded_trainer, seeded_product):
    other_trainer = User(
        email="other-client-owner@example.com",
        password_hash=hash_password("password123"),
        full_name="Other Trainer",
        role=UserRole.trainer,
    )
    db.add(other_trainer)
    db.flush()
    seeded_product["clients"][0].trainer_id = other_trainer.id
    db.commit()

    _login(client, seeded_trainer.email)
    response = client.patch(
        f"/api/v1/clients/{seeded_product['clients'][0].id}",
        json={
            "name": "Should Not Update",
            "age": 30,
            "fitness_level": "Beginner",
            "goals": "This should not be visible to another trainer.",
        },
    )
    assert response.status_code == 404


def test_client_detail_hides_session_snapshot_programs(client, db, seeded_trainer, seeded_product):
    _login(client, seeded_trainer.email)
    snapshot = Program(
        trainer_id=seeded_trainer.id,
        client_id=seeded_product["clients"][0].id,
        name="Client One - Strength Crew",
        focus="Strength Block",
        notes="Session snapshot from saved group: Strength Crew.",
        is_session_snapshot=True,
    )
    db.add(snapshot)
    db.commit()

    detail = client.get(f"/api/v1/clients/{seeded_product['clients'][0].id}").json()
    assert all(program["name"] != "Client One - Strength Crew" for program in detail["programs"])
