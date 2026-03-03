from app.extensions import db
from datetime import datetime

class Reminder(db.Model):
    """Reminder model."""
    __tablename__ = 'reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text)
    
    # Reminder time
    reminder_time = db.Column(db.DateTime, nullable=False)
    
    # Repeat options
    repeat = db.Column(db.String(50), default='none')  # none, daily, weekly, monthly, yearly
    repeat_until = db.Column(db.DateTime)
    
    # Status
    is_sent = db.Column(db.Boolean, default=False)
    
    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # No relationship defined here - let User model handle it
    
    def should_send(self):
        """Check if reminder should be sent."""
        now = datetime.utcnow()
        return not self.is_sent and self.reminder_time <= now
    
    def __repr__(self):
        return f'<Reminder {self.title}>'