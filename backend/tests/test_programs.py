def _login(client, seeded_trainer):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": seeded_trainer.email, "password": "password123"},
    )
    assert response.status_code == 200


def test_get_and_update_program(client, seeded_trainer, seeded_product):
    _login(client, seeded_trainer)
    program = seeded_product["programs"][0]
    exercises = seeded_product["exercises"]

    get_response = client.get(f"/api/v1/programs/{program.id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == program.id

    update_response = client.patch(
        f"/api/v1/programs/{program.id}",
        json={
            "name": "Updated Strength Plan",
            "notes": "Adjusted after intake.",
            "exercises": [
                {"exercise_id": exercises[1].id, "sets": 4, "reps": 10, "weight_kg": 24, "rest_seconds": 45},
                {"exercise_id": exercises[0].id, "sets": 3, "reps": 8, "weight_kg": 30, "rest_seconds": 60},
                {"exercise_id": exercises[2].id, "sets": 2, "reps": 30, "weight_kg": 0, "rest_seconds": 30},
            ],
        },
    )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["name"] == "Updated Strength Plan"
    assert updated["notes"] == "Adjusted after intake."
    assert [item["order_index"] for item in updated["exercises"]] == [0, 1, 2]
    assert updated["exercises"][0]["sets"] == 4
    assert updated["exercises"][0]["exercise"]["name"] == "Row"


def test_program_list_hides_session_snapshots_by_default(client, db, seeded_trainer, seeded_product):
    _login(client, seeded_trainer)
    snapshot = seeded_product["programs"][0]
    snapshot.is_session_snapshot = True
    db.commit()

    default_response = client.get("/api/v1/programs")
    assert default_response.status_code == 200
    assert all(program["id"] != snapshot.id for program in default_response.json())

    include_response = client.get("/api/v1/programs?include_snapshots=true")
    assert include_response.status_code == 200
    assert any(program["id"] == snapshot.id for program in include_response.json())
