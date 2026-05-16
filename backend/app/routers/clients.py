from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth import require_role
from app.database import get_db
from app.models import Client, Program, ProgramExercise, SessionClient, TrainingSession, User, UserRole
from app.schemas import ClientCreate, ClientDetailRead, ClientRead, ClientUpdate
from app.serializers import client_analytics_to_read, client_session_summary_to_read, program_to_read

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("", response_model=list[ClientRead])
def list_clients(
    current_user: Annotated[User, Depends(require_role(UserRole.trainer))],
    db: Annotated[Session, Depends(get_db)],
) -> list[Client]:
    return list(
        db.scalars(
            select(Client)
            .where(Client.trainer_id == current_user.id, Client.active.is_(True))
            .order_by(Client.name)
        )
    )


@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def create_client(
    payload: ClientCreate,
    current_user: Annotated[User, Depends(require_role(UserRole.trainer))],
    db: Annotated[Session, Depends(get_db)],
) -> Client:
    client = Client(trainer_id=current_user.id, **payload.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.patch("/{client_id}", response_model=ClientRead)
def update_client(
    client_id: int,
    payload: ClientUpdate,
    current_user: Annotated[User, Depends(require_role(UserRole.trainer))],
    db: Annotated[Session, Depends(get_db)],
) -> Client:
    client = db.scalar(
        select(Client).where(
            Client.id == client_id,
            Client.trainer_id == current_user.id,
            Client.active.is_(True),
        )
    )
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    client.name = payload.name
    client.age = payload.age
    client.fitness_level = payload.fitness_level
    client.goals = payload.goals
    db.commit()
    db.refresh(client)
    return client


@router.get("/{client_id}", response_model=ClientDetailRead)
def get_client_detail(
    client_id: int,
    current_user: Annotated[User, Depends(require_role(UserRole.trainer))],
    db: Annotated[Session, Depends(get_db)],
) -> ClientDetailRead:
    client = db.scalar(
        select(Client).where(
            Client.id == client_id,
            Client.trainer_id == current_user.id,
            Client.active.is_(True),
        )
    )
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    programs = list(
        db.scalars(
            select(Program)
            .options(selectinload(Program.exercises).selectinload(ProgramExercise.exercise))
            .where(
                Program.trainer_id == current_user.id,
                Program.client_id == client_id,
                Program.is_session_snapshot.is_(False),
            )
            .order_by(Program.created_at.desc())
        )
    )
    session_clients = list(
        db.scalars(
            select(SessionClient)
            .options(
                selectinload(SessionClient.session),
                selectinload(SessionClient.client),
                selectinload(SessionClient.program)
                .selectinload(Program.exercises)
                .selectinload(ProgramExercise.exercise),
            )
            .join(TrainingSession, TrainingSession.id == SessionClient.session_id)
            .where(SessionClient.client_id == client_id, TrainingSession.trainer_id == current_user.id)
            .order_by(TrainingSession.started_at.desc())
        )
    )
    return ClientDetailRead(
        client=client,
        programs=[program_to_read(program) for program in programs],
        analytics=client_analytics_to_read(db, session_clients),
        recent_sessions=[client_session_summary_to_read(db, item) for item in session_clients[:8]],
    )


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_client(
    client_id: int,
    current_user: Annotated[User, Depends(require_role(UserRole.trainer))],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    client = db.scalar(select(Client).where(Client.id == client_id, Client.trainer_id == current_user.id))
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    client.active = False
    db.commit()
