from . import db
from datetime import datetime

class Program(db.Model):
    __tablename__ = 'programs'
    
    id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    exercises = db.relationship('ProgramExercise', back_populates='program', cascade='all, delete-orphan')

class ProgramExercise(db.Model):
    __tablename__ = 'program_exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)
    rest_seconds = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    
    program = db.relationship('Program', back_populates='exercises')
    exercise = db.relationship('Exercise')  