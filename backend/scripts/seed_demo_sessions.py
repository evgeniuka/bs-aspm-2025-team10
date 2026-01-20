import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from models import db
from models.user import User
from models.client import Client
from models.exercise import Exercise
from models.program import Program, ProgramExercise
from models.session import Session, SessionClient
from models.workout_log import WorkoutLog
from datetime import datetime, timedelta
import random

app, _ = create_app()
app.app_context().push()


trainer = User.query.filter_by(email="daniel@fitcoach.com").first()
if not trainer:
    raise Exception("Trainer daniel@fitcoach.com не найден")

trainee_users = User.query.filter_by(role='trainee').all()
if not trainee_users:
    raise Exception("Not found any trainee users")

exercises = Exercise.query.all()
if not exercises:
    raise Exception("No exercises found in the database")

print(f"🎯 Found: {len(trainee_users)} clients, {len(exercises)} exercises")


def create_program_for_client(client_id, user_name, exercises_pool):
    program = Program(
        trainer_id=trainer.id,
        client_id=client_id,
        name=f"{user_name}'s Program",
        notes="This is a demo program."
    )
    db.session.add(program)
    db.session.flush()
    
    min_count = min(5, len(exercises_pool))
    max_count = min(10, len(exercises_pool))
    k = random.randint(min_count, max_count)
    selected_exercises = random.sample(exercises_pool, k=k)
    
    for idx, ex in enumerate(selected_exercises):
        pe = ProgramExercise(
            program_id=program.id,
            exercise_id=ex.id,
            order=idx,
            sets=random.choice([3, 4]),
            reps=random.choice([8, 10, 12]),
            weight_kg=round(random.uniform(10.0, 80.0), 1),
            rest_seconds=random.choice([60, 90, 120])
        )
        db.session.add(pe)
    
    return program


def generate_session_for_client(client, program, session_date, days_since_start):
    session = Session(
        trainer_id=trainer.id,
        status='completed',
        start_time=session_date,
        end_time=session_date + timedelta(minutes=random.randint(45, 75))
    )
    db.session.add(session)
    db.session.flush()
    

    progress_factor = min(1.0 + (days_since_start / 90) * 0.3, 1.5)
    
    sc = SessionClient(
        session_id=session.id,
        client_id=client.id,
        program_id=program.id,
        status='completed',
        current_exercise_index=len(program.exercises) - 1,
        current_set=program.exercises[-1].sets,
        completed_exercises=[pe.exercise_id for pe in program.exercises]
    )
    db.session.add(sc)
    
    for pe in program.exercises:
        adjusted_weight = round(pe.weight_kg * progress_factor, 1)
        for set_num in range(1, pe.sets + 1):
            log = WorkoutLog(
                session_id=session.id,
                client_id=client.id,
                exercise_id=pe.exercise_id,
                set_number=set_num,
                reps_completed=pe.reps,
                weight_kg=adjusted_weight,
                timestamp=session.start_time + timedelta(seconds=random.randint(10, 300))
            )
            db.session.add(log)
    

    client.last_workout_date = session.start_time.date()
    return session


for user in trainee_users:
    print(f"\n🔄 client: {user.full_name} ({user.email})")
    

    client = Client.query.filter_by(user_id=user.id).first()
    if not client:
        client = Client(
            trainer_id=trainer.id,
            user_id=user.id,
            name=user.full_name,
            age=random.randint(20, 45),
            fitness_level=random.choice(['Beginner', 'Intermediate', 'Advanced']),
            goals="Improve overall fitness and strength"
        )
        db.session.add(client)
        db.session.flush()
        print(f"  ✅ Created client: {client.name}")
    

    program = Program.query.filter_by(client_id=client.id).first()
    if not program:

        client_exercises = list(exercises)
        program = create_program_for_client(client.id, user.full_name, client_exercises)
        db.session.flush()
        print(f"  ✅ Created program: {program.name} ({len(program.exercises)} exercises)")
    

    today = datetime.utcnow().date()
    start_date = today - timedelta(days=90)
    current_date = start_date
    sessions_created = 0
    
    while current_date <= today:
        if current_date.weekday() in [0, 2, 4]:  
            session_datetime = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=18)
            days_since_start = (current_date - start_date).days
            session = generate_session_for_client(client, program, session_datetime, days_since_start)
            sessions_created += 1
        current_date += timedelta(days=1)
    
    print(f"  ✅ Created sessions: {sessions_created}")


try:
    db.session.commit()
    print("\n✨ All data successfully loaded!")
except Exception as e:
    db.session.rollback()
    print(f"\n❌ Error saving data: {e}")
    raise