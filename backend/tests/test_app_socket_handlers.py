from flask_socketio import SocketIOTestClient

from app import register_socket_handlers
from models import db
from models.client import Client
from models.exercise import Exercise
from models.program import Program, ProgramExercise
from models.session import Session, SessionClient
from models.workout_log import WorkoutLog


def _ensure_socket_handlers(app):
    if not getattr(app, "_socket_handlers_registered", False):
        register_socket_handlers(app)
        app._socket_handlers_registered = True


def _create_session_state(app):
    with app.app_context():
        client_record = Client(
            trainer_id=1,
            user_id=None,
            name="Socket Client",
            age=27,
            fitness_level="Beginner",
            goals="Endurance",
        )
        db.session.add(client_record)
        db.session.flush()

        program = Program(
            trainer_id=1,
            client_id=client_record.id,
            name="Socket Program",
            notes=None,
        )
        db.session.add(program)
        db.session.flush()

        exercise = Exercise(
            name="Socket Exercise",
            category="lower_body",
            description="Socket Exercise desc",
            equipment="barbell",
            difficulty="beginner",
        )
        db.session.add(exercise)
        db.session.flush()

        program_exercise = ProgramExercise(
            program_id=program.id,
            exercise_id=exercise.id,
            order=1,
            sets=3,
            reps=8,
            weight_kg=50.0,
            rest_seconds=30,
            notes=None,
        )
        db.session.add(program_exercise)

        session = Session(trainer_id=1, status="active")
        db.session.add(session)
        db.session.flush()

        session_client = SessionClient(
            session_id=session.id,
            client_id=client_record.id,
            program_id=program.id,
            current_exercise_index=0,
            current_set=1,
            status="active",
            rest_time_remaining=15,
        )
        db.session.add(session_client)

        db.session.add(
            WorkoutLog(
                session_id=session.id,
                client_id=client_record.id,
                exercise_id=exercise.id,
                set_number=1,
                reps_completed=8,
                weight_kg=50.0,
            )
        )
        db.session.commit()

        return session.id, client_record.id


def test_socket_handlers_join_and_leave_session(client, app):
    _ensure_socket_handlers(app)
    socketio = app.extensions["socketio"]
    ws_client = SocketIOTestClient(app, socketio, flask_test_client=client)

    ws_client.emit("join_session", {"session_id": 123})
    ws_client.emit("leave_session", {"session_id": 123})

    ws_client.disconnect()


def test_socket_handlers_trainee_connect_missing_id(client, app):
    _ensure_socket_handlers(app)
    socketio = app.extensions["socketio"]
    ws_client = SocketIOTestClient(app, socketio, flask_test_client=client)

    ws_client.emit("trainee_connect", {})
    ws_client.disconnect()


def test_socket_handlers_trainee_join_session_unauthorized(client, app):
    _ensure_socket_handlers(app)
    socketio = app.extensions["socketio"]
    ws_client = SocketIOTestClient(app, socketio, flask_test_client=client)

    ws_client.emit("trainee_join_session", {"session_id": 77, "trainee_id": 55})
    events = ws_client.get_received()

    error_events = [event for event in events if event["name"] == "error"]
    assert error_events
    assert error_events[0]["args"][0]["message"] == "Not authorized"

    ws_client.disconnect()


def test_socket_handlers_trainee_join_session_emits_state(client, app):
    _ensure_socket_handlers(app)
    session_id, trainee_id = _create_session_state(app)
    socketio = app.extensions["socketio"]
    ws_client = SocketIOTestClient(app, socketio, flask_test_client=client)

    ws_client.emit("trainee_join_session", {"session_id": session_id, "trainee_id": trainee_id})
    events = ws_client.get_received()

    session_events = [event for event in events if event["name"] == "session_state"]
    assert session_events
    payload = session_events[0]["args"][0]
    assert payload["session_id"] == session_id
    assert payload["trainee_data"]["current_exercise"]["name"] == "Socket Exercise"
    assert payload["trainee_data"]["sets_completed"][0]["set_number"] == 1

    ws_client.disconnect()
