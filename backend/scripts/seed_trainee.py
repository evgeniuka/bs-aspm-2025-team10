import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from models.user import db, User

app, _ = create_app()
app.app_context().push()

users_data = [

    {"email": "maya@fitcoach.com", "full_name": "Maya Levi", "role": "trainee", "password": "secure321"},
    {"email": "mark@fitcoach.com", "full_name": "Mark Tern", "role": "trainee", "password": "secure321"},
    {"email": "sara@fitcoach.com", "full_name": "Sara Gelstein", "role": "trainee", "password": "secure321"},
    {"email": "alex@fitcoach.com", "full_name": "Alex Johnson", "role": "trainee", "password": "secure321"}
]

for user_data in users_data:
    existing_user = User.query.filter_by(email=user_data["email"]).first()
    if not existing_user:
        user = User(
            email=user_data["email"],
            full_name=user_data["full_name"],
            role=user_data["role"]
        )
        user.set_password(user_data["password"])
        db.session.add(user)
        print(f"✅ Created {user_data['role']}: {user_data['full_name']} ({user_data['email']})")
    else:
        print(f"ℹ️  User already exists: {user_data['email']}")

db.session.commit()
print("\n✨ All seed users processed!")