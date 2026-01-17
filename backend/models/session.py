
from datetime import datetime
from . import db 

class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='active')  
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    
    trainer = db.relationship('User', backref='sessions')
    clients = db.relationship('SessionClient', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Session {self.id} - {self.status}>'


class SessionClient(db.Model):
    __tablename__ = 'session_clients'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)
    
    current_exercise_index = db.Column(db.Integer, default=0)
    current_set = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='ready')  
    

    completed_exercises = db.Column(db.JSON, default=list)  
    rest_time_remaining = db.Column(db.Integer, default=0)  
    
    client = db.relationship('Client', backref='session_clients')
    program = db.relationship('Program', backref='session_clients')
    
    def __repr__(self):
        return f'<SessionClient session={self.session_id} client={self.client_id}>'
