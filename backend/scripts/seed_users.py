import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from models.user import db, User

app, _ = create_app()
app.app_context().push()

if not User.query.filter_by(email="daniel@fitcoach.com").first():
    trainer = User(
        email="daniel@fitcoach.com",
        full_name="Daniel Cohen",
        role="trainer"
    )
    trainer.set_password("secure123")  
    db.session.add(trainer)
    db.session.commit()
    print("Seed user 'Daniel' created.")
else:
    print("ℹSeed user 'Daniel' already exists.")