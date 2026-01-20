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
   
    {"name": "Bench Press", "category": "upper_body", "equipment": "barbell", "difficulty": "intermediate", "description": "Lie on bench, lower barbell to chest, press upward."},
    {"name": "Pull-ups", "category": "upper_body", "equipment": "bodyweight", "difficulty": "intermediate", "description": "Hang from bar, pull body up until chin clears bar."},
    {"name": "Dumbbell Shoulder Press", "category": "upper_body", "equipment": "dumbbell", "difficulty": "intermediate", "description": "Press dumbbells overhead from shoulder height."},
 
    {"name": "Lunges", "category": "lower_body", "equipment": "bodyweight", "difficulty": "beginner", "description": "Step forward, lower back knee toward floor."},
    {"name": "Romanian Deadlift", "category": "lower_body", "equipment": "barbell", "difficulty": "intermediate", "description": "Hinge at hips, lower barbell along legs."},
    {"name": "Leg Press", "category": "lower_body", "equipment": "machine", "difficulty": "beginner", "description": "Press platform away with feet on machine."},
   
    {"name": "Russian Twists", "category": "core", "equipment": "bodyweight", "difficulty": "beginner", "description": "Twist torso side to side while seated."},
    {"name": "Leg Raises", "category": "core", "equipment": "bodyweight", "difficulty": "intermediate", "description": "Raise legs to 90 degrees while lying down."},
    {"name": "Bicycle Crunches", "category": "core", "equipment": "bodyweight", "difficulty": "beginner", "description": "Alternate elbow to opposite knee in cycling motion."},

    {"name": "Jumping Jacks", "category": "cardio", "equipment": "bodyweight", "difficulty": "beginner", "description": "Jump while spreading legs and raising arms."},
    {"name": "Burpees", "category": "cardio", "equipment": "bodyweight", "difficulty": "intermediate", "description": "Squat, kick back to plank, jump back up."},
    {"name": "High Knees", "category": "cardio", "equipment": "bodyweight", "difficulty": "beginner", "description": "Run in place with knees to chest."},

    {"name": "Clean and Jerk", "category": "full_body", "equipment": "barbell", "difficulty": "advanced", "description": "Lift barbell from floor to overhead in two phases."},
    {"name": "Snatch", "category": "full_body", "equipment": "barbell", "difficulty": "advanced", "description": "Lift barbell from floor to overhead in one motion."},
    {"name": "Thrusters", "category": "full_body", "equipment": "dumbbell", "difficulty": "intermediate", "description": "Squat then press weights overhead."},
   
]

for data in exercises_data:
    exercise = Exercise(**data)
    db.session.add(exercise)

db.session.commit()
print(f"Seeded {len(exercises_data)} exercises.")