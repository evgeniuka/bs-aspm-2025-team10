from app.auth import hash_password
from app.models import Client, FitnessLevel, User, UserRole


def _login(client, email: str, password: str = "password123"):
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200


def _group_payload(seeded_product, *, client_count: int = 2):
    return {
        "name": "Saturday Strength Crew",
        "focus": "Strength Block",
        "notes": "Prepared strength group for the weekend slot.",
        "client_ids": [item.id for item in seeded_product["clients"][:client_count]],
        "exercises": [
            {"exercise_id": exercise.id, "sets": 3, "reps": 8, "weight_kg": 20, "rest_seconds": 60}
            for exercise in seeded_product["exercises"]
        ],
    }


def _add_clients(db, seeded_trainer, count: int) -> list[Client]:
    clients = [
        Client(
            trainer_id=seeded_trainer.id,
            name=f"Class Client {index + 1}",
            age=25 + index,
            fitness_level=FitnessLevel.intermediate,
            goals="Train consistently in a larger group class.",
        )
        for index in range(count)
    ]
    db.add_all(clients)
    db.commit()
    return clients


def test_trainer_can_create_update_and_start_saved_group(client, seeded_trainer, seeded_product):
    _login(client, seeded_trainer.email)

    create_response = client.post("/api/v1/groups", json=_group_payload(seeded_product))
    assert create_response.status_code == 201
    group = create_response.json()
    assert group["name"] == "Saturday Strength Crew"
    assert [item["name"] for item in group["clients"]] == ["Client One", "Client Two"]
    assert len(group["exercises"]) == 3

    updated_payload = _group_payload(seeded_product, client_count=1)
    updated_payload["name"] = "Solo Strength Prep"
    updated_payload["exercises"][0]["reps"] = 10
    update_response = client.patch(f"/api/v1/groups/{group['id']}", json=updated_payload)
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["name"] == "Solo Strength Prep"
    assert [item["name"] for item in updated["clients"]] == ["Client One"]
    assert updated["exercises"][0]["reps"] == 10

    start_response = client.post(f"/api/v1/groups/{group['id']}/sessions")
    assert start_response.status_code == 201
    session = start_response.json()["session"]
    assert len(session["clients"]) == 1
    assert session["clients"][0]["client_name"] == "Client One"
    assert session["clients"][0]["program"]["name"] == "Client One - Solo Strength Prep"
    assert session["clients"][0]["program"]["exercises"][0]["reps"] == 10


def test_group_session_supports_attendance_substitutes_and_program_overrides(client, seeded_trainer, seeded_product):
    _login(client, seeded_trainer.email)

    create_payload = _group_payload(seeded_product, client_count=1)
    create_response = client.post("/api/v1/groups", json=create_payload)
    assert create_response.status_code == 201
    group = create_response.json()

    override_program = seeded_product["programs"][1]
    start_response = client.post(
        f"/api/v1/groups/{group['id']}/sessions",
        json={
            "clients": [
                {"client_id": seeded_product["clients"][0].id, "program_id": None},
                {"client_id": seeded_product["clients"][1].id, "program_id": override_program.id},
            ]
        },
    )
    assert start_response.status_code == 201
    session = start_response.json()["session"]
    assert [item["client_name"] for item in session["clients"]] == ["Client One", "Client Two"]
    assert session["clients"][0]["program"]["name"] == "Client One - Saturday Strength Crew"
    assert session["clients"][0]["program"]["exercises"][0]["reps"] == 8
    assert session["clients"][1]["program"]["id"] == override_program.id
    assert session["clients"][1]["program"]["name"] == "Client Two Plan"


def test_saved_group_can_hold_and_start_ten_clients(client, db, seeded_trainer, seeded_product):
    _login(client, seeded_trainer.email)
    extra_clients = _add_clients(db, seeded_trainer, 8)
    group_clients = [*seeded_product["clients"], *extra_clients]

    payload = _group_payload(seeded_product)
    payload["name"] = "Ten Person Conditioning"
    payload["client_ids"] = [item.id for item in group_clients]

    create_response = client.post("/api/v1/groups", json=payload)
    assert create_response.status_code == 201
    group = create_response.json()
    assert len(group["clients"]) == 10

    start_response = client.post(f"/api/v1/groups/{group['id']}/sessions")
    assert start_response.status_code == 201
    session = start_response.json()["session"]
    assert len(session["clients"]) == 10
    assert [item["client_name"] for item in session["clients"]][:2] == ["Client One", "Client Two"]


def test_group_validation_and_trainer_ownership(client, db, seeded_trainer, seeded_product):
    _login(client, seeded_trainer.email)
    duplicate_payload = _group_payload(seeded_product)
    duplicate_payload["client_ids"] = [seeded_product["clients"][0].id, seeded_product["clients"][0].id]
    assert client.post("/api/v1/groups", json=duplicate_payload).status_code == 400

    other_trainer = User(
        email="other-trainer@example.com",
        password_hash=hash_password("password123"),
        full_name="Other Trainer",
        role=UserRole.trainer,
    )
    db.add(other_trainer)
    db.flush()
    seeded_product["clients"][0].trainer_id = other_trainer.id
    db.commit()

    invalid_payload = _group_payload(seeded_product, client_count=1)
    assert client.post("/api/v1/groups", json=invalid_payload).status_code == 400


def test_trainee_cannot_access_group_management(client, db, seeded_product):
    trainee = User(
        email="trainee-groups@example.com",
        password_hash=hash_password("password123"),
        full_name="Client One",
        role=UserRole.trainee,
    )
    db.add(trainee)
    db.flush()
    seeded_product["clients"][0].user_id = trainee.id
    db.commit()

    _login(client, trainee.email)
    assert client.get("/api/v1/groups").status_code == 403
    assert client.post("/api/v1/groups", json=_group_payload(seeded_product)).status_code == 403
