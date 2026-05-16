from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth import require_role
from app.database import get_db
from app.models import Client, Exercise, Program, ProgramExercise, User, UserRole
from app.schemas import ProgramCreate, ProgramRead, ProgramUpdate
from app.serializers import program_to_read

router = APIRouter(prefix="/programs", tags=["programs"])


def _program_query(program_id: int, trainer_id: int):
    return (
        select(Program)
        .options(selectinload(Program.exercises).selectinload(ProgramExercise.exercise))
        .where(Program.id == program_id, Program.trainer_id == trainer_id)
    )


def _validate_exercises(db: Session, exercise_ids: list[int]) -> None:
    exercises = db.scalars(select(Exercise).where(Exercise.id.in_(exercise_ids))).all()
    if len(exercises) != len(set(exercise_ids)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more exercises do not exist")


@router.get("", response_model=list[ProgramRead])
def list_programs(
    current_user: Annotated[User, Depends(require_role(UserRole.trainer))],
    db: Annotated[Session, Depends(get_db)],
    client_id: int | None = None,
    include_snapshots: bool = False,
) -> list[ProgramRead]:
    query = (
        select(Program)
        .options(selectinload(Program.exercises).selectinload(ProgramExercise.exercise))
        .where(Program.trainer_id == current_user.id)
        .order_by(Program.created_at.desc())
    )
    if not include_snapshots:
        query = query.where(Program.is_session_snapshot.is_(False))
    if client_id is not None:
        query = query.where(Program.client_id == client_id)
    return [program_to_read(program) for program in db.scalars(query)]


@router.get("/{program_id}", response_model=ProgramRead)
def get_program(
    program_id: int,
    current_user: Annotated[User, Depends(require_role(UserRole.trainer))],
    db: Annotated[Session, Depends(get_db)],
) -> ProgramRead:
    program = db.scalar(_program_query(program_id, current_user.id))
    if not program:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program not found")
    return program_to_read(program)


@router.post("", response_model=ProgramRead, status_code=status.HTTP_201_CREATED)
def create_program(
    payload: ProgramCreate,
    current_user: Annotated[User, Depends(require_role(UserRole.trainer))],
    db: Annotated[Session, Depends(get_db)],
) -> ProgramRead:
    client = db.scalar(select(Client).where(Client.id == payload.client_id, Client.trainer_id == current_user.id))
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    _validate_exercises(db, [item.exercise_id for item in payload.exercises])

    program = Program(
        trainer_id=current_user.id,
        client_id=payload.client_id,
        name=payload.name,
        focus=payload.focus,
        notes=payload.notes,
    )
    db.add(program)
    db.flush()
    for order_index, item in enumerate(payload.exercises):
        db.add(ProgramExercise(program_id=program.id, order_index=order_index, **item.model_dump()))
    db.commit()

    program = db.scalar(
        select(Program)
        .options(selectinload(Program.exercises).selectinload(ProgramExercise.exercise))
        .where(Program.id == program.id)
    )
    return program_to_read(program)


@router.patch("/{program_id}", response_model=ProgramRead)
def update_program(
    program_id: int,
    payload: ProgramUpdate,
    current_user: Annotated[User, Depends(require_role(UserRole.trainer))],
    db: Annotated[Session, Depends(get_db)],
) -> ProgramRead:
    program = db.scalar(_program_query(program_id, current_user.id))
    if not program:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program not found")

    _validate_exercises(db, [item.exercise_id for item in payload.exercises])
    program.name = payload.name
    program.focus = payload.focus
    program.notes = payload.notes
    program.exercises.clear()
    db.flush()
    for order_index, item in enumerate(payload.exercises):
        db.add(ProgramExercise(program_id=program.id, order_index=order_index, **item.model_dump()))
    db.commit()

    program = db.scalar(_program_query(program_id, current_user.id))
    return program_to_read(program)
