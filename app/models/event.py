from app.extensions import db
from datetime import datetime

class Event(db.Model):
    """Calendar event model."""
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Date and time
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    all_day = db.Column(db.Boolean, default=False)
    
    # Event type
    event_type = db.Column(db.String(20), default='solo')
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    joined_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # No back_populates - let the User model handle the relationship
    
    def to_dict(self):
        """Convert to dictionary for JSON responses."""
        # Get the user to access color scheme
        from app.models.user import User
        user = User.query.get(self.user_id)
        
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start': self.start_date.isoformat(),
            'end': self.end_date.isoformat(),
            'allDay': self.all_day,
            'user_id': self.user_id,
            'event_type': self.event_type,
            'joined_user_id': self.joined_user_id,
            'color': user.color_scheme if user else 'purple'
        }
    
    def __repr__(self):
        return f'<Event {self.title}>'