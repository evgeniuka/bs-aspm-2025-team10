def _login(client, seeded_trainer):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": seeded_trainer.email, "password": "password123"},
    )
    assert response.status_code == 200


def _start_session(client, seeded_product):
    response = client.post(
        "/api/v1/sessions",
        json={
            "client_ids": [item.id for item in seeded_product["clients"]],
            "program_ids": [item.id for item in seeded_product["programs"]],
        },
    )
    assert response.status_code == 201
    return response.json()["session_id"]


def test_trainer_analytics_rolls_up_sessions_and_client_load(client, seeded_trainer, seeded_product):
    _login(client, seeded_trainer)
    session_id = _start_session(client, seeded_product)
    client_id = seeded_product["clients"][0].id

    complete_response = client.post(f"/api/v1/sessions/{session_id}/clients/{client_id}/complete-set")
    assert complete_response.status_code == 200
    end_response = client.post(f"/api/v1/sessions/{session_id}/end")
    assert end_response.status_code == 200

    response = client.get("/api/v1/analytics/trainer")

    assert response.status_code == 200
    analytics = response.json()
    assert analytics["total_sessions"] == 1
    assert analytics["completed_sessions"] == 1
    assert analytics["active_sessions"] == 0
    assert analytics["total_planned_sets"] == 12
    assert analytics["total_sets_completed"] == 1
    assert analytics["total_volume_kg"] == 160
    assert analytics["completion_rate"] == 8
    assert analytics["volume_by_day"][0]["sets_completed"] == 1
    assert analytics["volume_by_day"][0]["volume_kg"] == 160

    loaded_client = next(item for item in analytics["client_load"] if item["client_id"] == client_id)
    assert loaded_client["sessions"] == 1
    assert loaded_client["planned_sets"] == 6
    assert loaded_client["sets_completed"] == 1
    assert loaded_client["volume_kg"] == 160
