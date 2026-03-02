from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    """User model with color preference (purple/pink)."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    # Color scheme preference
    color_scheme = db.Column(db.String(20), default='purple')
    
    # User status
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Simplified relationships - only one relationship to events
    events = db.relationship(
        'Event',
        foreign_keys='Event.user_id',
        back_populates='owner',
        lazy=True,
        cascade='all, delete-orphan'
    )
    
    # Separate relationship for joined events (if needed)
    events_joined = db.relationship(
        'Event',
        foreign_keys='Event.joined_user_id',
        back_populates='joined_participant',
        lazy=True
    )
    
    tasks = db.relationship('Task', backref='user', lazy=True, cascade='all, delete-orphan')
    reminders = db.relationship('Reminder', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_color_class(self):
        return f"{self.color_scheme}-theme"
    
    def __repr__(self):
        return f'<User {self.username}>'