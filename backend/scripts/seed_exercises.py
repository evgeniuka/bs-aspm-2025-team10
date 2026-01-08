import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from models import db
from models.exercise import Exercise

app, _ = create_app()
app.app_context().push()

if Exercise.query.count() > 0:
    print("ℹExercises already seeded.")
    sys.exit(0)

exercises_data = [
    {"name": "Barbell Squat", "category": "lower_body", "equipment": "barbell", "difficulty": "intermediate", "description": "Stand with feet shoulder-width apart, barbell on upper back. Lower hips until thighs are parallel to floor, then drive through heels to stand."},
    {"name": "Push-ups", "category": "upper_body", "equipment": "bodyweight", "difficulty": "beginner", "description": "Keep body straight from head to heels. Lower chest to floor by bending elbows, then push back up."},
    {"name": "Plank", "category": "core", "equipment": "bodyweight", "difficulty": "beginner", "description": "Hold body in straight line from head to heels, supported on forearms and toes. Engage core and glutes."},
    {"name": "Running", "category": "cardio", "equipment": "other", "difficulty": "beginner", "description": "Maintain upright posture, land mid-foot, and drive arms forward and back."},
    {"name": "Deadlift", "category": "full_body", "equipment": "barbell", "difficulty": "advanced", "description": "Hinge at hips, grip barbell, keep back straight. Drive through heels to stand, squeezing glutes at the top."},
]

for data in exercises_data:
    exercise = Exercise(**data)
    db.session.add(exercise)

db.session.commit()
print(f"Seeded {len(exercises_data)} exercises.")