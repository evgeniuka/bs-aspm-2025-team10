import pytest
from starlette.websockets import WebSocketDisconnect

from app.auth import hash_password
from app.models import User, UserRole


def test_session_websocket_receives_updates(client, seeded_trainer, seeded_product):
    login = client.post(
        "/api/v1/auth/login",
        json={"email": seeded_trainer.email, "password": "password123"},
    )
    assert login.status_code == 200
    started = client.post(
        "/api/v1/sessions",
        json={
            "client_ids": [item.id for item in seeded_product["clients"]],
            "program_ids": [item.id for item in seeded_product["programs"]],
        },
    )
    session_id = started.json()["session_id"]
    client_id = seeded_product["clients"][0].id

    with client.websocket_connect(f"/api/v1/sessions/ws/{session_id}") as websocket:
        joined = websocket.receive_json()
        assert joined["type"] == "session_joined"

        response = client.post(f"/api/v1/sessions/{session_id}/clients/{client_id}/complete-set")
        assert response.status_code == 200
        update = websocket.receive_json()
        assert update["type"] == "rest_started"
        assert update["session"]["id"] == session_id

        undo_response = client.post(f"/api/v1/sessions/{session_id}/clients/{client_id}/undo-last-set")
        assert undo_response.status_code == 200
        undo_update = websocket.receive_json()
        assert undo_update["type"] == "set_undone"
        undone_client = next(item for item in undo_update["session"]["clients"] if item["client_id"] == client_id)
        assert undone_client["sets_completed"] == []


def test_session_websocket_requires_auth(client):
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect("/api/v1/sessions/ws/999"):
            pass

    assert exc.value.code == 1008


def test_session_websocket_enforces_trainer_ownership(client, db, seeded_trainer, seeded_product):
    login = client.post(
        "/api/v1/auth/login",
        json={"email": seeded_trainer.email, "password": "password123"},
    )
    assert login.status_code == 200
    started = client.post(
        "/api/v1/sessions",
        json={
            "client_ids": [seeded_product["clients"][0].id],
            "program_ids": [seeded_product["programs"][0].id],
        },
    )
    assert started.status_code == 201
    session_id = started.json()["session_id"]

    other_trainer = User(
        email="other-ws@example.com",
        password_hash=hash_password("password123"),
        full_name="Other Trainer",
        role=UserRole.trainer,
    )
    db.add(other_trainer)
    db.commit()

    other_login = client.post(
        "/api/v1/auth/login",
        json={"email": other_trainer.email, "password": "password123"},
    )
    assert other_login.status_code == 200

    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect(f"/api/v1/sessions/ws/{session_id}"):
            pass

    assert exc.value.code == 1008
