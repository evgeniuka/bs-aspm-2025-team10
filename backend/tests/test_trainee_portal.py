from app.auth import hash_password
from app.models import User, UserRole


def _login(client, email: str, password: str = "password123"):
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response


def test_trainee_can_read_only_their_portal(client, db, seeded_product):
    trainee = User(
        email="client@example.com",
        password_hash=hash_password("password123"),
        full_name="Client One",
        role=UserRole.trainee,
    )
    db.add(trainee)
    db.flush()
    seeded_product["clients"][0].user_id = trainee.id
    db.commit()

    _login(client, trainee.email)

    portal_response = client.get("/api/v1/trainee/me")
    assert portal_response.status_code == 200
    portal = portal_response.json()
    assert portal["client"]["id"] == seeded_product["clients"][0].id
    assert {program["client_id"] for program in portal["programs"]} == {seeded_product["clients"][0].id}

    assert client.get("/api/v1/dashboard").status_code == 403
    assert client.get("/api/v1/clients").status_code == 403


def test_trainee_session_summary_is_scoped_to_current_client(client, db, seeded_trainer, seeded_product):
    trainee = User(
        email="client-summary@example.com",
        password_hash=hash_password("password123"),
        full_name="Client One",
        role=UserRole.trainee,
    )
    db.add(trainee)
    db.flush()
    seeded_product["clients"][0].user_id = trainee.id
    db.commit()

    _login(client, seeded_trainer.email)
    started = client.post(
        "/api/v1/sessions",
        json={
            "client_ids": [item.id for item in seeded_product["clients"]],
            "program_ids": [item.id for item in seeded_product["programs"]],
        },
    )
    assert started.status_code == 201
    session_id = started.json()["session_id"]
    complete_response = client.post(
        f"/api/v1/sessions/{session_id}/clients/{seeded_product['clients'][0].id}/complete-set"
    )
    assert complete_response.status_code == 200
    client.post(f"/api/v1/sessions/{session_id}/end")

    _login(client, trainee.email)
    summary_response = client.get(f"/api/v1/trainee/sessions/{session_id}/summary")
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["total_clients"] == 1
    assert [item["client_id"] for item in summary["clients"]] == [seeded_product["clients"][0].id]


def test_trainee_check_in_surfaces_in_trainer_readiness(client, db, seeded_trainer, seeded_product):
    trainee = User(
        email="client-checkin@example.com",
        password_hash=hash_password("password123"),
        full_name="Client One",
        role=UserRole.trainee,
    )
    db.add(trainee)
    db.flush()
    seeded_product["clients"][0].user_id = trainee.id
    db.commit()

    _login(client, trainee.email)
    check_in_response = client.put(
        "/api/v1/trainee/check-in/today",
        json={
            "energy_level": 2,
            "sleep_quality": 4,
            "soreness_level": 3,
            "pain_notes": "Right knee feels sensitive on stairs.",
            "training_goal": "Train upper body and avoid knee irritation.",
        },
    )
    assert check_in_response.status_code == 200
    check_in = check_in_response.json()
    assert check_in["readiness_status"] == "attention"
    assert "low energy" in check_in["risk_flags"]
    assert "pain noted" in check_in["risk_flags"]

    portal_response = client.get("/api/v1/trainee/me")
    assert portal_response.status_code == 200
    assert portal_response.json()["today_check_in"]["training_goal"] == "Train upper body and avoid knee irritation."

    _login(client, seeded_trainer.email)
    dashboard_response = client.get("/api/v1/dashboard")
    assert dashboard_response.status_code == 200
    readiness = {
        item["client"]["id"]: item
        for item in dashboard_response.json()["today_readiness"]
    }
    client_readiness = readiness[seeded_product["clients"][0].id]
    assert client_readiness["readiness_status"] == "attention"
    assert client_readiness["check_in"]["pain_notes"] == "Right knee feels sensitive on stairs."
    assert readiness[seeded_product["clients"][1].id]["readiness_status"] == "missing"


def test_trainer_cannot_use_trainee_portal(client, seeded_trainer):
    _login(client, seeded_trainer.email)

    assert client.get("/api/v1/trainee/me").status_code == 403
