from . import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum('active', 'completed', 'cancelled', name='session_status'), nullable=False, default='active')
    
    clients = db.relationship('SessionClient', back_populates='session', cascade='all, delete-orphan')

class SessionClient(db.Model):
    __tablename__ = 'session_clients'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)
    current_exercise_index = db.Column(db.Integer, nullable=False, default=0)
    current_set = db.Column(db.Integer, nullable=False, default=1)
    completed_exercises = db.Column(db.JSON, default=list, nullable=False)  
    status = db.Column(db.Enum('ready', 'in_progress', 'resting', 'completed', name='client_session_status'), nullable=False, default='ready')
    
    session = db.relationship('Session', back_populates='clients')
    client = db.relationship('Client')
    program = db.relationship('Program')