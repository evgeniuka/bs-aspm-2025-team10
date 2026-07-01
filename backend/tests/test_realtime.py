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


def test_session_revision_increments_on_each_mutation(client, seeded_trainer, seeded_product):
    _login(client, seeded_trainer)
    session_id = _start_session(client, seeded_product)
    client_id = seeded_product["clients"][0].id

    base_revision = client.get(f"/api/v1/sessions/{session_id}").json()["revision"]
    after_complete = client.post(f"/api/v1/sessions/{session_id}/clients/{client_id}/complete-set").json()
    assert after_complete["revision"] > base_revision
    after_undo = client.post(f"/api/v1/sessions/{session_id}/clients/{client_id}/undo-last-set").json()
    assert after_undo["revision"] > after_complete["revision"]


def test_rest_ends_at_set_when_resting_and_cleared_on_end(client, seeded_trainer, seeded_product):
    _login(client, seeded_trainer)
    session_id = _start_session(client, seeded_product)
    client_id = seeded_product["clients"][0].id

    resting = client.post(f"/api/v1/sessions/{session_id}/clients/{client_id}/complete-set").json()
    resting_client = next(item for item in resting["clients"] if item["client_id"] == client_id)
    assert resting_client["status"] == "resting"
    assert resting_client["rest_ends_at"] is not None

    ended = client.post(f"/api/v1/sessions/{session_id}/end").json()
    assert all(item["rest_ends_at"] is None for item in ended["clients"])
