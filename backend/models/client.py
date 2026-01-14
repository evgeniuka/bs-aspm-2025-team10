from flask_sqlalchemy import SQLAlchemy
from . import db
from datetime import datetime

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    fitness_level = db.Column(db.Enum('Beginner', 'Intermediate', 'Advanced', name='fitness_level'), nullable=False)
    goals = db.Column(db.Text, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    last_workout_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'fitness_level': self.fitness_level,
            'goals': self.goals,
            'active': self.active,
            'last_workout_date': self.last_workout_date.isoformat() if self.last_workout_date else None,
            'created_at': self.created_at.isoformat(),
            'user_id': self.user_id
        }