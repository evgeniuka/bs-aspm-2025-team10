from models import db
from models.client import Client
from models.exercise import Exercise
from models.program import Program, ProgramExercise
from models.session import SessionClient
from models.workout_log import WorkoutLog


def _seed_session_with_program(app, client, trainer_token, sets_per_exercise, rest_seconds=30):
    with app.app_context():
        client_ids = []
        program_ids = []

        for idx in range(2):
            client_record = Client(
                trainer_id=trainer_token["user_id"],
                user_id=None,
                name=f"Client {idx + 1}",
                age=24 + idx,
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

        exercise_ids = []
        for idx, sets in enumerate(sets_per_exercise, start=1):
            exercise = Exercise(
                name=f"Exercise {idx}",
                category="lower_body",
                description=f"Exercise {idx} desc",
                equipment="barbell",
                difficulty="beginner",
            )
            db.session.add(exercise)
            db.session.flush()
            exercise_ids.append(exercise.id)

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

        filler_exercise = Exercise(
            name="Filler Exercise",
            category="upper_body",
            description="Filler desc",
            equipment="dumbbell",
            difficulty="beginner",
        )
        db.session.add(filler_exercise)
        db.session.flush()
        db.session.add(
            ProgramExercise(
                program_id=program_ids[1],
                exercise_id=filler_exercise.id,
                order=1,
                sets=1,
                reps=6,
                weight_kg=20.0,
                rest_seconds=0,
                notes=None,
            )
        )

        db.session.commit()

    response = client.post(
        "/api/sessions",
        json={"client_ids": client_ids, "program_ids": program_ids},
        headers={"Authorization": f"Bearer {trainer_token['token']}"},
    )
    session_id = response.get_json()["session_id"]

    return {
        "session_id": session_id,
        "client_id": client_ids[0],
        "program_id": program_ids[0],
        "exercise_ids": exercise_ids,
        "rest_seconds": rest_seconds,
    }


class DummySocketIO:
    def __init__(self):
        self.emitted = []

    def emit(self, name, payload, room=None):
        self.emitted.append({"name": name, "payload": payload, "room": room})


def test_fc7_complete_set_logs_workout_and_returns_updated_state(client, app, trainer_token):
    seeded = _seed_session_with_program(app, client, trainer_token, sets_per_exercise=[2], rest_seconds=40)

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
    assert len(updated_client["sets_completed"]) == 1

    with app.app_context():
        logs = WorkoutLog.query.filter_by(
            session_id=seeded["session_id"],
            client_id=seeded["client_id"],
            exercise_id=seeded["exercise_ids"][0],
        ).all()
        assert len(logs) == 1
        assert logs[0].set_number == 1


def test_fc7_complete_set_advances_to_next_exercise(client, app, trainer_token):
    seeded = _seed_session_with_program(app, client, trainer_token, sets_per_exercise=[2, 1], rest_seconds=10)

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
    assert seeded["exercise_ids"][0] in (updated_client["completed_exercises"] or [])

    with app.app_context():
        session_client = SessionClient.query.filter_by(
            session_id=seeded["session_id"],
            client_id=seeded["client_id"],
        ).first()
        assert session_client.current_exercise_index == 1
        assert session_client.status == "active"


def test_fc7_complete_set_marks_program_completed(client, app, trainer_token):
    seeded = _seed_session_with_program(app, client, trainer_token, sets_per_exercise=[1, 1], rest_seconds=0)

    for exercise_id in seeded["exercise_ids"]:
        response = client.post(
            f"/api/sessions/{seeded['session_id']}/complete-set",
            json={
                "client_id": seeded["client_id"],
                "exercise_id": exercise_id,
                "set_number": 1,
            },
            headers={"Authorization": f"Bearer {trainer_token['token']}"},
        )

    assert response.status_code == 200
    updated_client = response.get_json()["updated_client"]
    assert updated_client["status"] == "completed"
    assert set(updated_client["completed_exercises"] or []) == set(seeded["exercise_ids"])

    with app.app_context():
        session_client = SessionClient.query.filter_by(
            session_id=seeded["session_id"],
            client_id=seeded["client_id"],
        ).first()
        assert session_client.status == "completed"


def test_fc7_complete_set_emits_websocket_update(client, app, trainer_token, monkeypatch):
    seeded = _seed_session_with_program(app, client, trainer_token, sets_per_exercise=[1], rest_seconds=0)
    dummy_socketio = DummySocketIO()
    monkeypatch.setitem(app.extensions, "socketio", dummy_socketio)

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
    session_events = [
        event for event in dummy_socketio.emitted if event["name"] == "session_update"
    ]
    assert session_events
    assert session_events[0]["payload"]["session_id"] == seeded["session_id"]
    assert session_events[0]["payload"]["client_id"] == seeded["client_id"]
    assert session_events[0]["room"] == f"session_{seeded['session_id']}"
