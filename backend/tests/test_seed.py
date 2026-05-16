from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Client, Program, SessionStatus, TrainingGroup, TrainingSession, User
from app.seed import DEMO_EMAIL, DEMO_TRAINEE_EMAIL, run_seed


def test_clean_demo_seed_replaces_mutated_demo_data(db: Session):
    run_seed(reset_demo=True)
    db.expire_all()

    trainer = db.scalar(select(User).where(User.email == DEMO_EMAIL))
    trainee = db.scalar(select(User).where(User.email == DEMO_TRAINEE_EMAIL))
    maya = db.scalar(select(Client).where(Client.name == "Maya Levi", Client.trainer_id == trainer.id))
    assert trainer
    assert trainee
    assert maya
    assert maya.user_id == trainee.id

    db.add(
        Program(
            trainer_id=trainer.id,
            client_id=maya.id,
            name="Strength Block 1778787617071",
            focus="Strength Block",
        )
    )
    db.commit()

    run_seed(reset_demo=True)
    db.expire_all()

    demo_program_names = set(db.scalars(select(Program.name).join(Client).where(Client.trainer_id == trainer.id)))
    assert "Strength Block 1778787617071" not in demo_program_names
    assert "Maya Strength Block" in demo_program_names
    assert len(demo_program_names) == 30

    sessions = list(db.scalars(select(TrainingSession).where(TrainingSession.trainer_id == trainer.id)))
    assert sessions
    assert all(session.status == SessionStatus.completed for session in sessions)

    groups = list(db.scalars(select(TrainingGroup).where(TrainingGroup.trainer_id == trainer.id)))
    assert {group.name for group in groups} == {"Strength Crew", "Engine Builders", "Core Reset"}
