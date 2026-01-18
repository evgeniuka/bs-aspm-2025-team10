from models import db
from models.program import Program, ProgramExercise

from test_fc4_create_program import (
    _auth_headers,
    _build_exercises_payload,
    _create_client_record,
    _create_exercises,
    _create_user,
)


def _create_program_with_exercises(db_session, trainer, client_record, exercises, name="Program A"):
    program = Program(
        trainer_id=trainer.id,
        client_id=client_record.id,
        name=name,
        notes="Notes",
    )
    db_session.add(program)
    db_session.flush()

    for idx, exercise in enumerate(exercises):
        db_session.add(
            ProgramExercise(
                program_id=program.id,
                exercise_id=exercise.id,
                order=idx,
                sets=3,
                reps=10,
                weight_kg=20,
                rest_seconds=60,
                notes="",
            )
        )
    db_session.commit()
    return program


def test_trainer_can_only_view_own_programs(client, db_session):
    trainer_a = _create_user(db_session, email="trainer_a@example.com")
    trainer_b = _create_user(db_session, email="trainer_b@example.com")

    client_a = _create_client_record(db_session, trainer_a.id, name="Client A")
    client_b = _create_client_record(db_session, trainer_b.id, name="Client B")

    exercises_a = _create_exercises(db_session, count=5)
    exercises_b = _create_exercises(db_session, count=5)

    program_a = _create_program_with_exercises(
        db_session, trainer_a, client_a, exercises_a, name="Program A"
    )
    _create_program_with_exercises(
        db_session, trainer_b, client_b, exercises_b, name="Program B"
    )

    headers = _auth_headers(trainer_a)
    response = client.get("/api/programs", headers=headers)

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["id"] == program_a.id
    assert data[0]["trainer_id"] == trainer_a.id


def test_update_program_exercises(client, db_session):
    trainer = _create_user(db_session, email="trainer_update@example.com")
    client_record = _create_client_record(db_session, trainer.id)
    original_exercises = _create_exercises(db_session, count=5)
    program = _create_program_with_exercises(
        db_session, trainer, client_record, original_exercises, name="Original"
    )

    new_exercises = _create_exercises(db_session, count=5)
    payload = {
        "name": "Updated Program",
        "notes": "Updated notes",
        "exercises": _build_exercises_payload([exercise.id for exercise in new_exercises]),
    }

    headers = _auth_headers(trainer)
    response = client.put(
        f"/api/programs/{program.id}",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 200
    updated = db.session.get(Program, program.id)
    assert updated.name == payload["name"]
    assert updated.notes == payload["notes"]

    updated_exercises = ProgramExercise.query.filter_by(program_id=program.id).all()
    updated_ids = {exercise.exercise_id for exercise in updated_exercises}
    original_ids = {exercise.id for exercise in original_exercises}
    assert updated_ids == {exercise.id for exercise in new_exercises}
    assert updated_ids.isdisjoint(original_ids)


def test_delete_program_cascades(client, db_session):
    trainer = _create_user(db_session, email="trainer_delete@example.com")
    client_record = _create_client_record(db_session, trainer.id)
    exercises = _create_exercises(db_session, count=5)
    program = _create_program_with_exercises(
        db_session, trainer, client_record, exercises, name="Delete Me"
    )

    headers = _auth_headers(trainer)
    response = client.delete(
        f"/api/programs/{program.id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert db.session.get(Program, program.id) is None
    assert ProgramExercise.query.filter_by(program_id=program.id).count() == 0
