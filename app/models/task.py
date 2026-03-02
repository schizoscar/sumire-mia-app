from app.extensions import db
from datetime import datetime

class Task(db.Model):
    """To-do task model."""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Task status
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    
    # Due date
    due_date = db.Column(db.DateTime)
    
    # Priority (1-5, with 5 being highest)
    priority = db.Column(db.Integer, default=3)
    
    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def mark_completed(self):
        """Mark task as completed."""
        self.completed = True
        self.completed_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<Task {self.title}>'
