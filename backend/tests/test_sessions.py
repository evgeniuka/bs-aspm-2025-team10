from app.auth import hash_password
from app.models import Client, FitnessLevel, Program, ProgramExercise, User, UserRole, WorkoutLog


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


def test_create_and_end_session_flow(client, seeded_trainer, seeded_product):
    _login(client, seeded_trainer)
    session_id = _start_session(client, seeded_product)

    session_response = client.get(f"/api/v1/sessions/{session_id}")
    assert session_response.status_code == 200
    assert len(session_response.json()["clients"]) == 2

    client_id = seeded_product["clients"][0].id
    complete_response = client.post(f"/api/v1/sessions/{session_id}/clients/{client_id}/complete-set")
    assert complete_response.status_code == 200
    updated_client = next(item for item in complete_response.json()["clients"] if item["client_id"] == client_id)
    assert updated_client["current_set"] == 2
    assert updated_client["status"] == "resting"

    start_response = client.post(f"/api/v1/sessions/{session_id}/clients/{client_id}/start-next-set")
    assert start_response.status_code == 200
    updated_client = next(item for item in start_response.json()["clients"] if item["client_id"] == client_id)
    assert updated_client["status"] == "working"

    end_response = client.post(f"/api/v1/sessions/{session_id}/end")
    assert end_response.status_code == 200
    ended = end_response.json()
    assert ended["status"] == "completed"
    assert all(item["status"] == "completed" for item in ended["clients"])
    assert all(item["rest_time_remaining"] == 0 for item in ended["clients"])

    active_response = client.get("/api/v1/sessions/active")
    assert active_response.status_code == 200
    assert active_response.json() is None


def test_start_session_is_idempotent_while_active(client, seeded_trainer, seeded_product):
    _login(client, seeded_trainer)
    first_session_id = _start_session(client, seeded_product)
    second_session_id = _start_session(client, seeded_product)

    assert second_session_id == first_session_id


def test_start_session_accepts_one_client(client, seeded_trainer, seeded_product):
    _login(client, seeded_trainer)
    response = client.post(
        "/api/v1/sessions",
        json={
            "client_ids": [seeded_product["clients"][0].id],
            "program_ids": [seeded_product["programs"][0].id],
        },
    )

    assert response.status_code == 201
    assert len(response.json()["session"]["clients"]) == 1


def test_session_summary_and_client_detail_analytics(client, seeded_trainer, seeded_product):
    _login(client, seeded_trainer)
    session_id = _start_session(client, seeded_product)
    client_id = seeded_product["clients"][0].id

    complete_response = client.post(f"/api/v1/sessions/{session_id}/clients/{client_id}/complete-set")
    assert complete_response.status_code == 200
    client.post(f"/api/v1/sessions/{session_id}/end")

    summary_response = client.get(f"/api/v1/sessions/{session_id}/summary")
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["total_planned_sets"] == 12
    assert summary["total_sets_completed"] == 1
    assert summary["total_volume_kg"] == 160
    client_summary = next(item for item in summary["clients"] if item["client_id"] == client_id)
    assert client_summary["planned_sets"] == 6
    assert client_summary["sets_completed"] == 1
    assert client_summary["exercises"][0]["volume_kg"] == 160

    notes_response = client.patch(
        f"/api/v1/sessions/{session_id}/clients/{client_id}/summary",
        json={"coach_notes": "  Keep knee tracking clean.  ", "next_focus": "Tempo squats"},
    )
    assert notes_response.status_code == 200
    updated_client = next(item for item in notes_response.json()["clients"] if item["client_id"] == client_id)
    assert updated_client["coach_notes"] == "Keep knee tracking clean."
    assert updated_client["next_focus"] == "Tempo squats"

    detail_response = client.get(f"/api/v1/clients/{client_id}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["client"]["id"] == client_id
    assert detail["analytics"]["total_sessions"] == 1
    assert detail["analytics"]["total_sets"] == 1
    assert detail["analytics"]["total_volume_kg"] == 160
    assert detail["recent_sessions"][0]["coach_notes"] == "Keep knee tracking clean."


def test_complete_set_accepts_actual_reps_and_weight(client, seeded_trainer, seeded_product):
    _login(client, seeded_trainer)
    session_id = _start_session(client, seeded_product)
    client_id = seeded_product["clients"][0].id
    exercise_id = seeded_product["exercises"][0].id

    response = client.post(
        f"/api/v1/sessions/{session_id}/clients/{client_id}/complete-set",
        json={"exercise_id": exercise_id, "set_number": 1, "reps_completed": 9, "weight_kg": 22.5},
    )

    assert response.status_code == 200
    updated_client = next(item for item in response.json()["clients"] if item["client_id"] == client_id)
    assert updated_client["sets_completed"][0]["reps_completed"] == 9
    assert updated_client["sets_completed"][0]["weight_kg"] == 22.5
    assert updated_client["sets_completed"][0]["volume_kg"] == 202.5

    summary_response = client.get(f"/api/v1/sessions/{session_id}/summary")
    client_summary = next(item for item in summary_response.json()["clients"] if item["client_id"] == client_id)
    assert client_summary["volume_kg"] == 202.5
    assert client_summary["exercises"][0]["sets"][0]["reps_completed"] == 9
    assert client_summary["exercises"][0]["sets"][0]["weight_kg"] == 22.5


def test_duplicate_exercise_occurrences_are_logged_independently(client, db, seeded_trainer, seeded_product):
    _login(client, seeded_trainer)
    training_client = seeded_product["clients"][0]
    exercise = seeded_product["exercises"][0]
    program = Program(
        trainer_id=seeded_trainer.id,
        client_id=training_client.id,
        name="Duplicate Squat Block",
        focus="Strength Block",
    )
    db.add(program)
    db.flush()
    first_occurrence = ProgramExercise(
        program_id=program.id,
        exercise_id=exercise.id,
        order_index=0,
        sets=1,
        reps=8,
        weight_kg=20,
        rest_seconds=30,
    )
    second_occurrence = ProgramExercise(
        program_id=program.id,
        exercise_id=exercise.id,
        order_index=1,
        sets=1,
        reps=6,
        weight_kg=22.5,
        rest_seconds=45,
    )
    db.add_all([first_occurrence, second_occurrence])
    db.commit()

    response = client.post(
        "/api/v1/sessions",
        json={"client_ids": [training_client.id], "program_ids": [program.id]},
    )
    assert response.status_code == 201
    session_id = response.json()["session_id"]

    first_response = client.post(
        f"/api/v1/sessions/{session_id}/clients/{training_client.id}/complete-set",
        json={
            "program_exercise_id": first_occurrence.id,
            "exercise_id": exercise.id,
            "set_number": 1,
            "reps_completed": 8,
            "weight_kg": 20,
        },
    )
    assert first_response.status_code == 200
    first_state = next(item for item in first_response.json()["clients"] if item["client_id"] == training_client.id)
    assert first_state["current_exercise_index"] == 1

    second_response = client.post(
        f"/api/v1/sessions/{session_id}/clients/{training_client.id}/complete-set",
        json={
            "program_exercise_id": second_occurrence.id,
            "exercise_id": exercise.id,
            "set_number": 1,
            "reps_completed": 6,
            "weight_kg": 22.5,
        },
    )
    assert second_response.status_code == 200

    logs = db.query(WorkoutLog).order_by(WorkoutLog.id).all()
    assert [log.program_exercise_id for log in logs] == [first_occurrence.id, second_occurrence.id]
    assert sum(log.reps_completed * log.weight_kg for log in logs) == 295

    summary_response = client.get(f"/api/v1/sessions/{session_id}/summary")
    summary_client = summary_response.json()["clients"][0]
    assert summary_client["sets_completed"] == 2
    assert summary_client["volume_kg"] == 295
    assert [item["sets_completed"] for item in summary_client["exercises"]] == [1, 1]


def test_complete_set_rejects_stale_expected_state(client, db, seeded_trainer, seeded_product):
    _login(client, seeded_trainer)
    session_id = _start_session(client, seeded_product)
    client_id = seeded_product["clients"][0].id
    exercise_id = seeded_product["exercises"][0].id

    response = client.post(
        f"/api/v1/sessions/{session_id}/clients/{client_id}/complete-set",
        json={"exercise_id": exercise_id, "set_number": 2, "reps_completed": 8, "weight_kg": 20},
    )

    assert response.status_code == 409
    assert db.query(WorkoutLog).count() == 0
    session_response = client.get(f"/api/v1/sessions/{session_id}")
    session_client = next(item for item in session_response.json()["clients"] if item["client_id"] == client_id)
    assert session_client["current_set"] == 1
    assert session_client["sets_completed"] == []


def test_undo_last_set_restores_current_state(client, db, seeded_trainer, seeded_product):
    _login(client, seeded_trainer)
    session_id = _start_session(client, seeded_product)
    client_id = seeded_product["clients"][0].id

    complete_response = client.post(f"/api/v1/sessions/{session_id}/clients/{client_id}/complete-set")
    assert complete_response.status_code == 200
    resting_client = next(item for item in complete_response.json()["clients"] if item["client_id"] == client_id)
    assert resting_client["current_set"] == 2
    assert resting_client["status"] == "resting"
    assert resting_client["rest_time_remaining"] == 30

    undo_response = client.post(f"/api/v1/sessions/{session_id}/clients/{client_id}/undo-last-set")

    assert undo_response.status_code == 200
    assert db.query(WorkoutLog).count() == 0
    undone_client = next(item for item in undo_response.json()["clients"] if item["client_id"] == client_id)
    assert undone_client["current_exercise_index"] == 0
    assert undone_client["current_set"] == 1
    assert undone_client["status"] == "working"
    assert undone_client["rest_time_remaining"] == 0
    assert undone_client["sets_completed"] == []


def test_undo_last_set_rejects_empty_or_completed_session(client, seeded_trainer, seeded_product):
    _login(client, seeded_trainer)
    session_id = _start_session(client, seeded_product)
    client_id = seeded_product["clients"][0].id

    empty_response = client.post(f"/api/v1/sessions/{session_id}/clients/{client_id}/undo-last-set")
    assert empty_response.status_code == 400

    client.post(f"/api/v1/sessions/{session_id}/clients/{client_id}/complete-set")
    client.post(f"/api/v1/sessions/{session_id}/end")
    completed_response = client.post(f"/api/v1/sessions/{session_id}/clients/{client_id}/undo-last-set")
    assert completed_response.status_code == 409


def test_history_endpoints_enforce_trainer_ownership(client, db, seeded_trainer, seeded_product):
    _login(client, seeded_trainer)
    session_id = _start_session(client, seeded_product)

    other_trainer = User(
        email="other@example.com",
        password_hash=hash_password("password123"),
        full_name="Other Trainer",
        role=UserRole.trainer,
    )
    db.add(other_trainer)
    db.flush()
    other_client = Client(
        trainer_id=other_trainer.id,
        name="Other Client",
        age=28,
        fitness_level=FitnessLevel.beginner,
        goals="Private goal",
    )
    db.add(other_client)
    db.commit()

    response = client.post(
        "/api/v1/auth/login",
        json={"email": other_trainer.email, "password": "password123"},
    )
    assert response.status_code == 200

    assert client.get(f"/api/v1/sessions/{session_id}/summary").status_code == 404
    assert client.get(f"/api/v1/clients/{seeded_product['clients'][0].id}").status_code == 404
    assert (
        client.post(f"/api/v1/sessions/{session_id}/clients/{seeded_product['clients'][0].id}/complete-set").status_code
        == 404
    )
    assert (
        client.post(f"/api/v1/sessions/{session_id}/clients/{seeded_product['clients'][0].id}/undo-last-set").status_code
        == 404
    )
