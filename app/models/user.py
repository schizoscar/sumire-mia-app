from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    """User model with color preference."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    # Color scheme preference - now with 4 options
    color_scheme = db.Column(db.String(20), default='purple')  # purple, pink, blue, orange
    
    # User status
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    events = db.relationship('Event', foreign_keys='Event.user_id', backref='event_owner', lazy=True, cascade='all, delete-orphan')
    # Add this if you want to access events where user is the joined user
    joined_events = db.relationship('Event', foreign_keys='Event.joined_user_id', backref='joined_user', lazy=True)
    tasks = db.relationship('Task', backref='task_owner', lazy=True, cascade='all, delete-orphan')
    reminders = db.relationship('Reminder', backref='reminder_owner', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def get_color_style(self):
        """Return CSS style based on user's color scheme."""
        colors = {
            'purple': {'bg': '#e6e6fa', 'border': '#c084fc', 'dot': '💜'},
            'pink': {'bg': '#ffdab9', 'border': '#f9a8d4', 'dot': '🩷'},
            'blue': {'bg': '#b8e2f2', 'border': '#7aa5c7', 'dot': '💙'},
            'orange': {'bg': '#ffd7b5', 'border': '#f9a95d', 'dot': '🧡'}
        }
        return colors.get(self.color_scheme, colors['purple'])
    
    def __repr__(self):
        return f'<User {self.username}>'