from . import db
from datetime import datetime

class Exercise(db.Model):
    __tablename__ = 'exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.Enum('upper_body', 'lower_body', 'core', 'cardio', 'full_body', name='exercise_category'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    equipment = db.Column(db.Enum('bodyweight', 'barbell', 'dumbbell', 'machine', 'cable', 'kettlebell', 'other', name='exercise_equipment'), nullable=False)
    difficulty = db.Column(db.Enum('beginner', 'intermediate', 'advanced', name='exercise_difficulty'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'equipment': self.equipment,
            'difficulty': self.difficulty
        }