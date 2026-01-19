from flask_socketio import SocketIOTestClient

from models import db
from models.client import Client
from models.exercise import Exercise
from models.program import Program, ProgramExercise
from models.session import SessionClient
from models.workout_log import WorkoutLog


def _seed_session_with_program(app, client, trainer_token, exercise_sets, rest_seconds=30):
    with app.app_context():
        client_ids = []
        program_ids = []
        for idx in range(2):
            client_record = Client(
                trainer_id=trainer_token["user_id"],
                user_id=None,
                name=f"Client {idx + 1}",
                age=25 + idx,
                fitness_level="Beginner",
                goals="Strength",
            )
            db.session.add(client_record)
            db.session.flush()
            client_ids.append(client_record.id)

            program = Program(
                trainer_id=trainer_token["user_id"],
                client_id=client_record.id,
                name=f"Program {idx + 1}",
                notes=None,
            )
            db.session.add(program)
            db.session.flush()
            program_ids.append(program.id)

        exercises = []
        for idx, sets in enumerate(exercise_sets, start=1):
            exercise = Exercise(
                name=f"Exercise {idx}",
                category="lower_body",
                description=f"Exercise {idx} desc",
                equipment="barbell",
                difficulty="beginner",
            )
            db.session.add(exercise)
            db.session.flush()

            program_exercise = ProgramExercise(
                program_id=program_ids[0],
                exercise_id=exercise.id,
                order=idx,
                sets=sets,
                reps=8,
                weight_kg=60.0,
                rest_seconds=rest_seconds if idx == 1 else 0,
                notes=None,
            )
            db.session.add(program_exercise)
            exercises.append(exercise)

        db.session.commit()
        exercise_ids = [exercise.id for exercise in exercises]
        primary_client_id = client_ids[0]
        primary_program_id = program_ids[0]

    payload = {"client_ids": client_ids, "program_ids": program_ids}
    response = client.post(
        "/api/sessions",
        json=payload,
        headers={"Authorization": f"Bearer {trainer_token['token']}"},
    )
    session_id = response.get_json()["session_id"]

    return {
        "session_id": session_id,
        "client_id": primary_client_id,
        "program_id": primary_program_id,
        "exercise_ids": exercise_ids,
        "rest_seconds": rest_seconds,
    }


def _join_session_room(test_client, session_id, trainee_id=None):
    if trainee_id is None:
        test_client.emit("join_session", {"session_id": session_id})
    else:
        test_client.emit("trainee_join_session", {"session_id": session_id, "trainee_id": trainee_id})


def _find_event(received, name):
    return [item for item in received if item["name"] == name]


def test_fc7_mark_complete_logs_set_and_returns_progress(client, app, trainer_token):
    seeded = _seed_session_with_program(app, client, trainer_token, exercise_sets=[2, 1], rest_seconds=45)

    response = client.post(
        f"/api/sessions/{seeded['session_id']}/complete-set",
        json={
            "client_id": seeded["client_id"],
            "exercise_id": seeded["exercise_ids"][0],
            "set_number": 1,
        },
        headers={"Authorization": f"Bearer {trainer_token['token']}"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["message"] == "Set marked as complete"
    updated_client = payload["updated_client"]
    assert updated_client["current_set"] == 2
    assert updated_client["status"] == "resting"
    assert updated_client["rest_time_remaining"] == seeded["rest_seconds"]

    with app.app_context():
        logs = WorkoutLog.query.filter_by(
            session_id=seeded["session_id"],
            client_id=seeded["client_id"],
            exercise_id=seeded["exercise_ids"][0],
        ).all()
        assert len(logs) == 1
        assert logs[0].set_number == 1


def test_fc7_mark_complete_broadcasts_session_update(client, app, trainer_token):
    seeded = _seed_session_with_program(app, client, trainer_token, exercise_sets=[1, 1], rest_seconds=30)
    socketio = app.extensions["socketio"]

    trainer_ws = SocketIOTestClient(app, socketio, flask_test_client=client)
    trainee_http = app.test_client()
    trainee_ws = SocketIOTestClient(app, socketio, flask_test_client=trainee_http)

    _join_session_room(trainer_ws, seeded["session_id"])
    _join_session_room(trainee_ws, seeded["session_id"], trainee_id=seeded["client_id"])

    trainer_ws.get_received()
    trainee_ws.get_received()

    response = client.post(
        f"/api/sessions/{seeded['session_id']}/complete-set",
        json={
            "client_id": seeded["client_id"],
            "exercise_id": seeded["exercise_ids"][0],
            "set_number": 1,
        },
        headers={"Authorization": f"Bearer {trainer_token['token']}"},
    )

    assert response.status_code == 200

    trainer_events = _find_event(trainer_ws.get_received(), "session_update")
    trainee_events = _find_event(trainee_ws.get_received(), "session_update")

    assert trainer_events
    response = client.post(
        f"/api/sessions/{seeded['session_id']}/complete-set",
        json={
            "client_id": seeded["client_id"],
            "exercise_id": seeded["exercise_ids"][0],
            "set_number": 1,
        },
        headers={"Authorization": f"Bearer {trainer_token['token']}"},
    )

    assert response.status_code == 200

    import time
    time.sleep(0.1)  # 💤 Ждём, чтобы событие успело дойти

    trainer_events = _find_event(trainer_ws.get_received(), "session_update")
    trainee_events = _find_event(trainee_ws.get_received(), "session_update")

    assert trainer_events
    assert trainee_events


def test_fc7_mark_complete_advances_to_next_exercise(client, app, trainer_token):
    seeded = _seed_session_with_program(app, client, trainer_token, exercise_sets=[2, 1], rest_seconds=10)

    for set_number in (1, 2):
        response = client.post(
            f"/api/sessions/{seeded['session_id']}/complete-set",
            json={
                "client_id": seeded["client_id"],
                "exercise_id": seeded["exercise_ids"][0],
                "set_number": set_number,
            },
            headers={"Authorization": f"Bearer {trainer_token['token']}"},
        )

    assert response.status_code == 200
    updated_client = response.get_json()["updated_client"]
    assert updated_client["current_exercise_index"] == 1
    assert updated_client["current_set"] == 1
    assert updated_client["status"] == "active"

    with app.app_context():
        session_client = SessionClient.query.filter_by(
            session_id=seeded["session_id"],
            client_id=seeded["client_id"],
        ).first()
        assert seeded["exercise_ids"][0] in (session_client.completed_exercises or [])


def test_fc7_mark_complete_marks_program_completed(client, app, trainer_token):
    seeded = _seed_session_with_program(app, client, trainer_token, exercise_sets=[1, 1], rest_seconds=5)

    client.post(
        f"/api/sessions/{seeded['session_id']}/complete-set",
        json={
            "client_id": seeded["client_id"],
            "exercise_id": seeded["exercise_ids"][0],
            "set_number": 1,
        },
        headers={"Authorization": f"Bearer {trainer_token['token']}"},
    )

    response = client.post(
        f"/api/sessions/{seeded['session_id']}/complete-set",
        json={
            "client_id": seeded["client_id"],
            "exercise_id": seeded["exercise_ids"][1],
            "set_number": 1,
        },
        headers={"Authorization": f"Bearer {trainer_token['token']}"},
    )

    assert response.status_code == 200
    updated_client = response.get_json()["updated_client"]
    assert updated_client["status"] == "completed"

    with app.app_context():
        session_client = SessionClient.query.filter_by(
            session_id=seeded["session_id"],
            client_id=seeded["client_id"],
        ).first()
        assert session_client.status == "completed"
        assert len(session_client.completed_exercises or []) == 2


def test_mark_set_complete(client, app, trainer_token):
    seeded = _seed_session_with_program(app, client, trainer_token, exercise_sets=[4], rest_seconds=20)

    response = client.post(
        f"/api/sessions/{seeded['session_id']}/complete-set",
        json={
            "client_id": seeded["client_id"],
            "exercise_id": seeded["exercise_ids"][0],
            "set_number": 1,
        },
        headers={"Authorization": f"Bearer {trainer_token['token']}"},
    )

    assert response.status_code == 200
    updated_client = response.get_json()["updated_client"]
    assert len(updated_client["sets_completed"]) == 1

    with app.app_context():
        logs = WorkoutLog.query.filter_by(
            session_id=seeded["session_id"],
            client_id=seeded["client_id"],
            exercise_id=seeded["exercise_ids"][0],
        ).all()
        assert len(logs) == 1


def test_state_transition_to_resting(client, app, trainer_token):
    seeded = _seed_session_with_program(app, client, trainer_token, exercise_sets=[4], rest_seconds=60)

    client.post(
        f"/api/sessions/{seeded['session_id']}/complete-set",
        json={
            "client_id": seeded["client_id"],
            "exercise_id": seeded["exercise_ids"][0],
            "set_number": 1,
        },
        headers={"Authorization": f"Bearer {trainer_token['token']}"},
    )

    with app.app_context():
        session_client = SessionClient.query.filter_by(
            session_id=seeded["session_id"],
            client_id=seeded["client_id"],
        ).first()
        assert session_client.status == "resting"
        assert session_client.rest_time_remaining == seeded["rest_seconds"]


def test_state_transition_to_next_exercise(client, app, trainer_token):
    seeded = _seed_session_with_program(app, client, trainer_token, exercise_sets=[2, 1], rest_seconds=0)

    for set_number in (1, 2):
        client.post(
            f"/api/sessions/{seeded['session_id']}/complete-set",
            json={
                "client_id": seeded["client_id"],
                "exercise_id": seeded["exercise_ids"][0],
                "set_number": set_number,
            },
            headers={"Authorization": f"Bearer {trainer_token['token']}"},
        )

    with app.app_context():
        session_client = SessionClient.query.filter_by(
            session_id=seeded["session_id"],
            client_id=seeded["client_id"],
        ).first()
        assert session_client.current_exercise_index == 1
        assert session_client.status == "active"


def test_state_transition_to_completed(client, app, trainer_token):
    seeded = _seed_session_with_program(app, client, trainer_token, exercise_sets=[1, 1], rest_seconds=0)

    for exercise_id in seeded["exercise_ids"]:
        client.post(
            f"/api/sessions/{seeded['session_id']}/complete-set",
            json={
                "client_id": seeded["client_id"],
                "exercise_id": exercise_id,
                "set_number": 1,
            },
            headers={"Authorization": f"Bearer {trainer_token['token']}"},
        )

    with app.app_context():
        session_client = SessionClient.query.filter_by(
            session_id=seeded["session_id"],
            client_id=seeded["client_id"],
        ).first()
        assert session_client.status == "completed"
        assert set(session_client.completed_exercises or []) == set(seeded["exercise_ids"])


def test_websocket_event_emitted(client, app, trainer_token):
    seeded = _seed_session_with_program(app, client, trainer_token, exercise_sets=[1], rest_seconds=0)
    socketio = app.extensions["socketio"]

    trainer_ws = SocketIOTestClient(app, socketio, flask_test_client=client)
    _join_session_room(trainer_ws, seeded["session_id"])
    trainer_ws.get_received()

    response = client.post(
        f"/api/sessions/{seeded['session_id']}/complete-set",
        json={
            "client_id": seeded["client_id"],
            "exercise_id": seeded["exercise_ids"][0],
            "set_number": 1,
        },
        headers={"Authorization": f"Bearer {trainer_token['token']}"},
    )

    assert response.status_code == 200

    import time
    time.sleep(0.1)  # 💤 ждём немного, чтобы событие дошло до WebSocket

    trainer_events = _find_event(trainer_ws.get_received(), "session_update")
    assert trainer_events
    assert trainer_events


def test_concurrent_set_completion(client, app, trainer_token):
    seeded = _seed_session_with_program(app, client, trainer_token, exercise_sets=[2], rest_seconds=0)

    for _ in range(2):
        client.post(
            f"/api/sessions/{seeded['session_id']}/complete-set",
            json={
                "client_id": seeded["client_id"],
                "exercise_id": seeded["exercise_ids"][0],
                "set_number": 1,
            },
            headers={"Authorization": f"Bearer {trainer_token['token']}"},
        )

    with app.app_context():
        logs = WorkoutLog.query.filter_by(
            session_id=seeded["session_id"],
            client_id=seeded["client_id"],
            exercise_id=seeded["exercise_ids"][0],
            set_number=1,
        ).all()
        session_client = SessionClient.query.filter_by(
            session_id=seeded["session_id"],
            client_id=seeded["client_id"],
        ).first()

        assert len(logs) == 1
        assert session_client.current_set == 2
