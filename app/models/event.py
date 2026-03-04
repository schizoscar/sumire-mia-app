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
    event_type = db.Column(db.String(20), default='solo')  # 'solo' or 'joined'
    
    # For joined events, both users are stored here
    # Primary owner is the creator, secondary is the joined user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Primary owner
    joined_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Secondary user
    
    # Both users can edit/delete if it's a joined event
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - use the existing backref from User model
    # The User model already has 'events' relationship with backref='event_owner'
    
    def to_dict(self):
        """Convert to dictionary for JSON responses."""
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
            'joined_user_id': self.joined_user_id,
            'event_type': self.event_type,
            'color': user.color_scheme if user else 'purple'
        }
    
    def can_edit(self, user_id):
        """Check if a user can edit this event."""
        if self.event_type == 'solo':
            return self.user_id == user_id
        else:  # joined event
            return self.user_id == user_id or self.joined_user_id == user_id
    
    def __repr__(self):
        return f'<Event {self.title}>'