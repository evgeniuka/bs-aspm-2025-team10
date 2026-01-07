import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from models.user import db, User

app, _ = create_app()
app.app_context().push()

if not User.query.filter_by(email="maya@fitcoach.com").first():
    trainee = User(
        email="maya@fitcoach.com",
        full_name="Maya Levi",
        role="trainee"
    )
    trainee.set_password("secure321")  
    db.session.add(trainee)
    db.session.commit()
    print("Seed user 'Maya' (trainee) created.")
else:
    print("ℹSeed user 'Maya' (trainee) already exists.")