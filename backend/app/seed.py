from argparse import ArgumentParser, Namespace
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth import hash_password
from app.database import Base, SessionLocal, engine
from app.models import (
    Client,
    ClientCheckIn,
    Exercise,
    FitnessLevel,
    Program,
    ProgramExercise,
    SessionClient,
    SessionClientStatus,
    SessionStatus,
    TrainingGroup,
    TrainingGroupExercise,
    TrainingGroupMember,
    TrainingSession,
    User,
    UserRole,
    WorkoutLog,
    utc_today,
)

DEMO_EMAIL = "trainer@fitcoach.dev"
DEMO_PASSWORD = "demo-password"
DEMO_TRAINEE_EMAIL = "maya@fitcoach.dev"
DEMO_TRAINEE_PASSWORD = "demo-password"
DEMO_TRAINEE_NAME = "Maya Levi"

EXERCISES = [
    ("Goblet Squat", "Strength", "Kettlebell", "Beginner", "Squat pattern with front-loaded weight."),
    ("Dumbbell Bench Press", "Strength", "Dumbbells", "Intermediate", "Horizontal push for chest and triceps."),
    ("Romanian Deadlift", "Strength", "Barbell", "Intermediate", "Hip hinge focused on posterior chain."),
    ("TRX Row", "Strength", "TRX", "Beginner", "Bodyweight pulling pattern."),
    ("Walking Lunge", "Strength", "Bodyweight", "Intermediate", "Single-leg strength and balance."),
    ("Plank Hold", "Core", "Mat", "Beginner", "Anti-extension core hold."),
    ("Bike Sprint", "Conditioning", "Bike", "Advanced", "Short interval conditioning."),
    ("Lat Pulldown", "Strength", "Cable", "Beginner", "Vertical pulling movement."),
    ("Dead Bug", "Core", "Mat", "Beginner", "Controlled anti-extension core drill."),
    ("Pallof Press", "Core", "Cable", "Intermediate", "Anti-rotation press for trunk control."),
    ("Farmer Carry", "Conditioning", "Dumbbells", "Beginner", "Loaded carry for grip and trunk endurance."),
    ("Step Up", "Strength", "Box", "Beginner", "Single-leg lower-body pattern."),
    ("Tempo Split Squat", "Strength", "Bodyweight", "Intermediate", "Controlled split squat with steady tempo."),
    ("Assault Bike Interval", "Conditioning", "Bike", "Advanced", "High-output interval for conditioning."),
]

CLIENTS = [
    ("Maya Levi", 29, FitnessLevel.intermediate, "Build strength while training around a busy work schedule."),
    ("Noam Cohen", 34, FitnessLevel.beginner, "Improve conditioning and reduce lower-back discomfort."),
    ("Sara Gold", 42, FitnessLevel.advanced, "Prepare for a trail race with strength maintenance."),
    ("Daniel Stein", 25, FitnessLevel.intermediate, "Gain muscle and improve consistency."),
    ("Amir Haddad", 38, FitnessLevel.intermediate, "Return to strength training after a shoulder rehab block."),
    ("Lior Katz", 31, FitnessLevel.beginner, "Build consistency, basic movement skill, and weekly routine."),
    ("Elena Mor", 46, FitnessLevel.advanced, "Maintain strength while preparing for a road marathon."),
    ("Tomer Bar", 27, FitnessLevel.intermediate, "Improve hypertrophy, conditioning, and training adherence."),
    ("Ruth Kaplan", 52, FitnessLevel.beginner, "Improve mobility, balance, and confidence with loaded movement."),
    ("Adam Weiss", 35, FitnessLevel.advanced, "Build power and conditioning for recreational basketball."),
]

PROGRAM_VARIANTS = [
    (
        "Strength Block",
        "Progressive strength session for the live coach cockpit.",
        [
            ("Goblet Squat", 3, 8, 24, 75),
            ("Dumbbell Bench Press", 3, 10, 22, 75),
            ("Romanian Deadlift", 3, 8, 32, 90),
            ("TRX Row", 3, 12, 0, 60),
        ],
    ),
    (
        "Conditioning Circuit",
        "Higher-tempo conditioning session with simple coaching checkpoints.",
        [
            ("Bike Sprint", 4, 12, 0, 45),
            ("Walking Lunge", 3, 10, 12, 45),
            ("Farmer Carry", 3, 40, 24, 60),
            ("Plank Hold", 3, 30, 0, 45),
        ],
    ),
    (
        "Core Stability",
        "Lower-load session for trunk control, movement quality, and recovery days.",
        [
            ("Dead Bug", 3, 10, 0, 40),
            ("Pallof Press", 3, 12, 12, 45),
            ("Step Up", 3, 10, 10, 50),
            ("Tempo Split Squat", 3, 8, 0, 60),
        ],
    ),
]

DEMO_CHECK_INS = {
    "Maya Levi": {
        "energy_level": 4,
        "sleep_quality": 4,
        "soreness_level": 2,
        "pain_notes": None,
        "training_goal": "Keep hinge control sharp and leave the session feeling strong.",
    },
    "Noam Cohen": {
        "energy_level": 3,
        "sleep_quality": 2,
        "soreness_level": 3,
        "pain_notes": "Lower back feels tight after a long commute.",
        "training_goal": "Move well without aggravating the back.",
    },
    "Sara Gold": {
        "energy_level": 5,
        "sleep_quality": 4,
        "soreness_level": 1,
        "pain_notes": None,
        "training_goal": "Push conditioning but keep legs fresh for the weekend run.",
    },
}

DEMO_GROUPS = [
    {
        "name": "Strength Crew",
        "focus": "Strength Block",
        "notes": "Small-group strength template for clients ready to progress the main lifts.",
        "clients": ["Maya Levi", "Daniel Stein", "Amir Haddad"],
    },
    {
        "name": "Engine Builders",
        "focus": "Conditioning Circuit",
        "notes": "Large endurance group with simple stations, clear pacing targets, and quick attendance checks.",
        "clients": [
            "Maya Levi",
            "Noam Cohen",
            "Sara Gold",
            "Daniel Stein",
            "Amir Haddad",
            "Lior Katz",
            "Elena Mor",
            "Tomer Bar",
            "Ruth Kaplan",
            "Adam Weiss",
        ],
    },
    {
        "name": "Core Reset",
        "focus": "Core Stability",
        "notes": "Lower-load control session for trunk, balance, and recovery-day coaching.",
        "clients": ["Noam Cohen", "Ruth Kaplan", "Lior Katz"],
    },
]

DEMO_HISTORY = [
    {
        "days_ago": 18,
        "clients": {
            "Maya Levi": ("Strength Block", 0.94, "Strong hinge pattern. Keep the final set crisp.", "Brace before every hinge rep."),
            "Noam Cohen": ("Core Stability", 0.9, "Moved well with lower back staying quiet.", "Keep the warm-up slow and controlled."),
            "Sara Gold": ("Conditioning Circuit", 0.98, "Good pace without losing posture.", "Keep cadence steady before adding intensity."),
        },
    },
    {
        "days_ago": 12,
        "clients": {
            "Maya Levi": ("Core Stability", 1.0, "Control improved on split squat tempo.", "Add load only if control stays clean."),
            "Daniel Stein": ("Strength Block", 0.96, "Consistent effort across the main lifts.", "Progress bench press next session."),
            "Sara Gold": ("Strength Block", 1.02, "Strength maintenance looked solid.", "Keep accessory work short before race week."),
        },
    },
    {
        "days_ago": 7,
        "clients": {
            "Maya Levi": ("Conditioning Circuit", 0.97, "Recovered quickly between intervals.", "Keep breathing rhythm through carries."),
            "Noam Cohen": ("Strength Block", 0.92, "Squat depth improved while staying pain-free.", "Repeat loads before progressing."),
            "Amir Haddad": ("Core Stability", 0.9, "Shoulder tolerated pressing prep well.", "Stay below discomfort on rows."),
        },
    },
    {
        "days_ago": 2,
        "clients": {
            "Maya Levi": ("Strength Block", 1.04, "Best session this block. Hinge control held under load.", "Build from Romanian deadlift next."),
            "Sara Gold": ("Core Stability", 1.0, "Low fatigue session landed well.", "Prioritize freshness for the long run."),
            "Daniel Stein": ("Conditioning Circuit", 0.95, "Good work rate, needs steadier pacing.", "Start slower and finish stronger."),
        },
    },
]


def run_seed(*, reset_demo: bool = False) -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        trainer = db.scalar(select(User).where(User.email == DEMO_EMAIL))
        if not trainer:
            trainer = User(
                email=DEMO_EMAIL,
                password_hash=hash_password(DEMO_PASSWORD),
                full_name="Daniel Trainer",
                role=UserRole.trainer,
            )
            db.add(trainer)
            db.flush()
        else:
            trainer.password_hash = hash_password(DEMO_PASSWORD)
            trainer.full_name = "Daniel Trainer"
            trainer.role = UserRole.trainer
            trainer.is_active = True

        trainee = db.scalar(select(User).where(User.email == DEMO_TRAINEE_EMAIL))
        if not trainee:
            trainee = User(
                email=DEMO_TRAINEE_EMAIL,
                password_hash=hash_password(DEMO_TRAINEE_PASSWORD),
                full_name=DEMO_TRAINEE_NAME,
                role=UserRole.trainee,
            )
            db.add(trainee)
            db.flush()
        else:
            trainee.password_hash = hash_password(DEMO_TRAINEE_PASSWORD)
            trainee.full_name = DEMO_TRAINEE_NAME
            trainee.role = UserRole.trainee
            trainee.is_active = True

        if reset_demo:
            reset_demo_data(db, trainer)

        existing_exercises = {exercise.name: exercise for exercise in db.scalars(select(Exercise))}
        for name, category, equipment, difficulty, description in EXERCISES:
            if name not in existing_exercises:
                db.add(
                    Exercise(
                        name=name,
                        category=category,
                        equipment=equipment,
                        difficulty=difficulty,
                        description=description,
                    )
                )
        db.commit()

        exercises = {exercise.name: exercise for exercise in db.scalars(select(Exercise).order_by(Exercise.id))}
        existing_clients = {
            client.name: client for client in db.scalars(select(Client).where(Client.trainer_id == trainer.id))
        }
        for index, (name, age, level, goals) in enumerate(CLIENTS):
            client = existing_clients.get(name)
            if not client:
                client = Client(
                    trainer_id=trainer.id,
                    name=name,
                    age=age,
                    fitness_level=level,
                    goals=goals,
                )
                db.add(client)
                db.flush()
            if name == DEMO_TRAINEE_NAME and client.user_id is None:
                client.user_id = trainee.id
            existing_programs = {
                program.name: program
                for program in db.scalars(
                    select(Program).where(Program.trainer_id == trainer.id, Program.client_id == client.id)
                )
            }
            for variant_name, notes, exercise_plan in PROGRAM_VARIANTS:
                program_name = f"{name.split()[0]} {variant_name}"
                if program_name in existing_programs:
                    existing_programs[program_name].focus = existing_programs[program_name].focus or variant_name
                    continue
                program = Program(
                    trainer_id=trainer.id,
                    client_id=client.id,
                    name=program_name,
                    focus=variant_name,
                    notes=notes,
                )
                db.add(program)
                db.flush()
                load_offset = index * 2
                for order_index, (exercise_name, sets, reps, weight_kg, rest_seconds) in enumerate(exercise_plan):
                    exercise = exercises[exercise_name]
                    db.add(
                        ProgramExercise(
                            program_id=program.id,
                            exercise_id=exercise.id,
                            order_index=order_index,
                            sets=sets,
                            reps=reps,
                            weight_kg=weight_kg + load_offset if weight_kg else 0,
                            rest_seconds=rest_seconds,
                        )
                    )
        db.flush()

        clients_by_name = {
            client.name: client for client in db.scalars(select(Client).where(Client.trainer_id == trainer.id))
        }
        submitted_on = utc_today()
        for client_name, check_in_data in DEMO_CHECK_INS.items():
            demo_client = clients_by_name.get(client_name)
            if not demo_client:
                continue
            check_in = db.scalar(
                select(ClientCheckIn).where(
                    ClientCheckIn.client_id == demo_client.id,
                    ClientCheckIn.submitted_on == submitted_on,
                )
            )
            if not check_in:
                check_in = ClientCheckIn(client_id=demo_client.id, submitted_on=submitted_on)
                db.add(check_in)
            for field_name, value in check_in_data.items():
                setattr(check_in, field_name, value)

        ensure_demo_groups(db, trainer, clients_by_name, exercises)
        ensure_demo_history(db, trainer, clients_by_name)
        db.commit()
    finally:
        db.close()


def reset_demo_data(db: Session, trainer: User) -> None:
    groups = list(db.scalars(select(TrainingGroup).where(TrainingGroup.trainer_id == trainer.id)))
    for group in groups:
        db.delete(group)
    db.flush()

    sessions = list(
        db.scalars(
            select(TrainingSession)
            .options(selectinload(TrainingSession.clients))
            .where(TrainingSession.trainer_id == trainer.id)
        )
    )
    for session in sessions:
        db.query(WorkoutLog).filter(WorkoutLog.session_id == session.id).delete(synchronize_session=False)
        db.delete(session)
    db.flush()

    clients = list(
        db.scalars(
            select(Client)
            .options(
                selectinload(Client.programs).selectinload(Program.exercises),
                selectinload(Client.check_ins),
            )
            .where(Client.trainer_id == trainer.id)
        )
    )
    for client in clients:
        db.delete(client)
    db.flush()


def ensure_demo_groups(
    db: Session,
    trainer: User,
    clients_by_name: dict[str, Client],
    exercises_by_name: dict[str, Exercise],
) -> None:
    plans_by_focus = {name: plan for name, _, plan in PROGRAM_VARIANTS}
    existing_groups = {
        group.name: group
        for group in db.scalars(
            select(TrainingGroup)
            .options(
                selectinload(TrainingGroup.members),
                selectinload(TrainingGroup.exercises),
            )
            .where(TrainingGroup.trainer_id == trainer.id)
        )
    }

    for group_data in DEMO_GROUPS:
        group = existing_groups.get(group_data["name"])
        if not group:
            group = TrainingGroup(trainer_id=trainer.id, name=group_data["name"])
            db.add(group)
            db.flush()
        group.name = group_data["name"]
        group.focus = group_data["focus"]
        group.notes = group_data["notes"]
        group.active = True
        group.members.clear()
        group.exercises.clear()
        db.flush()

        for order_index, client_name in enumerate(group_data["clients"]):
            client = clients_by_name.get(client_name)
            if client:
                group.members.append(TrainingGroupMember(client_id=client.id, order_index=order_index))

        for order_index, (exercise_name, sets, reps, weight_kg, rest_seconds) in enumerate(plans_by_focus[group_data["focus"]]):
            exercise = exercises_by_name[exercise_name]
            group.exercises.append(
                TrainingGroupExercise(
                    exercise_id=exercise.id,
                    order_index=order_index,
                    sets=sets,
                    reps=reps,
                    weight_kg=weight_kg,
                    rest_seconds=rest_seconds,
                )
            )


def ensure_demo_history(db: Session, trainer: User, clients_by_name: dict[str, Client]) -> None:
    existing_session = db.scalar(select(TrainingSession.id).where(TrainingSession.trainer_id == trainer.id).limit(1))
    if existing_session:
        return

    now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
    for session_index, session_plan in enumerate(DEMO_HISTORY):
        started_at = now - timedelta(days=session_plan["days_ago"], hours=2)
        ended_at = started_at + timedelta(minutes=52 + session_index * 4)
        session = TrainingSession(
            trainer_id=trainer.id,
            status=SessionStatus.completed,
            started_at=started_at,
            ended_at=ended_at,
        )
        db.add(session)
        db.flush()

        for client_name, (focus, effort, coach_notes, next_focus) in session_plan["clients"].items():
            client = clients_by_name.get(client_name)
            if not client:
                continue
            program = db.scalar(
                select(Program)
                .options(selectinload(Program.exercises).selectinload(ProgramExercise.exercise))
                .where(
                    Program.trainer_id == trainer.id,
                    Program.client_id == client.id,
                    Program.focus == focus,
                )
            )
            if not program:
                continue
            ordered_exercises = sorted(program.exercises, key=lambda item: item.order_index)
            session_client = SessionClient(
                session_id=session.id,
                client_id=client.id,
                program_id=program.id,
                current_exercise_index=len(ordered_exercises),
                current_set=1,
                status=SessionClientStatus.completed,
                completed_exercises=[exercise.id for exercise in ordered_exercises],
                rest_time_remaining=0,
                coach_notes=coach_notes,
                next_focus=next_focus,
            )
            db.add(session_client)
            client.last_workout_date = max(client.last_workout_date or ended_at, ended_at)
            add_demo_workout_logs(db, session, client, ordered_exercises, effort)


def add_demo_workout_logs(
    db: Session,
    session: TrainingSession,
    client: Client,
    exercises: list[ProgramExercise],
    effort: float,
) -> None:
    for exercise_index, planned in enumerate(exercises[:3]):
        completed_sets = max(1, planned.sets - (1 if exercise_index == 2 and effort < 0.96 else 0))
        for set_number in range(1, completed_sets + 1):
            reps_completed = max(1, round(planned.reps * effort))
            weight_kg = round((planned.weight_kg * effort) * 2) / 2 if planned.weight_kg else 0
            db.add(
                WorkoutLog(
                    session_id=session.id,
                    client_id=client.id,
                    program_exercise_id=planned.id,
                    exercise_id=planned.exercise_id,
                    set_number=set_number,
                    reps_completed=reps_completed,
                    weight_kg=weight_kg,
                    created_at=session.started_at + timedelta(minutes=exercise_index * 12 + set_number * 3),
                )
            )


def parse_args() -> Namespace:
    parser = ArgumentParser(description="Seed FitCoach Pro demo data.")
    parser.add_argument(
        "--reset-demo",
        action="store_true",
        help="Remove demo trainer data before recreating a clean portfolio dataset.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_seed(reset_demo=args.reset_demo)
    reset_label = " with clean reset" if args.reset_demo else ""
    print(f"Seed complete{reset_label}. Demo login: {DEMO_EMAIL} / {DEMO_PASSWORD}")
