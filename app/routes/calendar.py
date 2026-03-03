from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.event import Event
from app.routes import calendar_bp
from datetime import datetime
from app.models.user import User
import re

@calendar_bp.route('/')
@login_required
def index():
    """Calendar view."""
    return render_template('calendar/index.html', title='Calendar')

@calendar_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add new event."""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        event_type = request.form.get('event_type', 'solo')
        joined_user_id = request.form.get('joined_user_id')
        
        # Get the combined datetime strings
        start_datetime_str = request.form.get('start_date')  # This comes from hidden field
        end_datetime_str = request.form.get('end_date')      # This comes from hidden field
        
        print(f"DEBUG - Start datetime: '{start_datetime_str}'")
        print(f"DEBUG - End datetime: '{end_datetime_str}'")
        print(f"DEBUG - Event type: {event_type}")
        print(f"DEBUG - Joined user: {joined_user_id}")
        
        try:
            # Parse datetime in format: DD/MM/YY HH:MM AM/PM
            # Example: "02/03/26 02:30 PM"
            start_date = datetime.strptime(start_datetime_str, '%d/%m/%y %I:%M %p')
            end_date = datetime.strptime(end_datetime_str, '%d/%m/%y %I:%M %p')
            
            print(f"DEBUG - Parsed start: {start_date}")
            print(f"DEBUG - Parsed end: {end_date}")
            
            # Create event
            event = Event(
                title=title,
                description=description,
                start_date=start_date,
                end_date=end_date,
                user_id=current_user.id,
                event_type=event_type,
                joined_user_id=joined_user_id if event_type == 'joined' and joined_user_id else None
            )
            
            db.session.add(event)
            print(f"DEBUG - Event added to session: {event}")
            
            # If joined event, create a mirror event for the other user
            if event_type == 'joined' and joined_user_id:
                joined_user = User.query.get(int(joined_user_id))
                if joined_user:
                    joined_event = Event(
                        title=f"{title} (with {current_user.username})",
                        description=description,
                        start_date=start_date,
                        end_date=end_date,
                        user_id=int(joined_user_id),
                        event_type='joined',
                        joined_user_id=current_user.id
                    )
                    db.session.add(joined_event)
                    print(f"DEBUG - Joined event created for user: {joined_user.username}")
            
            db.session.commit()
            print(f"DEBUG - Database committed successfully")
            
            flash('Event added successfully!', 'success')
            return redirect(url_for('calendar.index'))
            
        except ValueError as e:
            print(f"DEBUG - Date parsing error: {e}")
            flash(f'Invalid date format. Please use DD/MM/YY format (e.g., 02/03/26 02:30 PM)', 'error')
            return render_template('calendar/add.html', title='Add Event', 
                                 form_data=request.form, users=User.query.all())
        except Exception as e:
            print(f"DEBUG - Unexpected error: {e}")
            flash(f'Error creating event: {str(e)}', 'error')
            return render_template('calendar/add.html', title='Add Event', 
                                 form_data=request.form, users=User.query.all())
    
    # GET request
    users = User.query.all()
    return render_template('calendar/add.html', title='Add Event', users=users)

@calendar_bp.route('/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit(event_id):
    """Edit event - only owner can edit."""
    event = Event.query.get_or_404(event_id)
    
    # Check if user owns this event
    if event.user_id != current_user.id:
        flash('You can only edit your own events.', 'error')
        return redirect(url_for('calendar.index'))
    
    if request.method == 'POST':
        event.title = request.form.get('title')
        event.description = request.form.get('description')
        
        # Get the date strings
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        
        try:
            # Parse date in DD/MM/YY HH:MM AM/PM format
            event.start_date = datetime.strptime(start_date_str, '%d/%m/%y %I:%M %p')
            event.end_date = datetime.strptime(end_date_str, '%d/%m/%y %I:%M %p')
            
            db.session.commit()
            flash('Event updated successfully!', 'success')
            return redirect(url_for('calendar.index'))
            
        except ValueError as e:
            print(f"Date parsing error: {e}")  # Debug print
            flash('Invalid date format. Please use DD/MM/YY format.', 'error')
    
    # Format dates for display in the form
    formatted_start = event.start_date.strftime('%d/%m/%y %I:%M %p') if event.start_date else ''
    formatted_end = event.end_date.strftime('%d/%m/%y %I:%M %p') if event.end_date else ''
    
    return render_template('calendar/edit.html', title='Edit Event', 
                         event=event, 
                         formatted_start=formatted_start,
                         formatted_end=formatted_end)

@calendar_bp.route('/delete/<int:event_id>')
@login_required
def delete(event_id):
    """Delete event - only owner can delete."""
    event = Event.query.get_or_404(event_id)
    
    # Check if user owns this event
    if event.user_id != current_user.id:
        flash('You can only delete your own events.', 'error')
        return redirect(url_for('calendar.index'))
    
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('calendar.index'))

@calendar_bp.route('/api/events')
@login_required
def api_events():
    """API endpoint for calendar events - show all users' events."""
    # Get ALL events, not just current user's
    events = Event.query.all()
    events_list = []
    
    for event in events:
        # Get the joined user's info if it's a joined event
        joined_username = None
        if event.joined_user_id:
            joined_user = User.query.get(event.joined_user_id)
            joined_username = joined_user.username if joined_user else None
        
        # Get the event owner's color scheme and username
        owner = event.event_owner
        color_scheme = owner.color_scheme if owner else 'purple'
        owner_username = owner.username if owner else 'Unknown'
        
        # Determine if current user is the owner
        is_owner = (event.user_id == current_user.id)
            
        event_dict = {
            'id': event.id,
            'title': event.title,
            'start': event.start_date.isoformat(),
            'end': event.end_date.isoformat(),
            'description': event.description,
            'allDay': event.all_day,
            'event_type': event.event_type,
            'joined_user_id': event.joined_user_id,
            'joined_username': joined_username,
            'className': f"{event.event_type}-{color_scheme if event.event_type == 'solo' else 'joined'}",
            'color_scheme': color_scheme,
            'owner_id': event.user_id,
            'owner_username': owner_username,
            'is_owner': is_owner  # Add this for frontend to know if user can edit/delete
        }
        
        # Set color based on event type
        if event.event_type == 'joined':
            event_dict['color'] = '#ffb6b6'  # red for joined
            event_dict['textColor'] = '#4a4a4a'
            event_dict['borderColor'] = '#f87171'
        else:
            if color_scheme == 'purple':
                event_dict['color'] = '#e6e6fa'  # lavender
                event_dict['borderColor'] = '#c084fc'
            elif color_scheme == 'pink':
                event_dict['color'] = '#ffdab9'  # peach
                event_dict['borderColor'] = '#f9a8d4'
            elif color_scheme == 'blue':
                event_dict['color'] = '#b8e2f2'  # sky blue
                event_dict['borderColor'] = '#7aa5c7'
            elif color_scheme == 'orange':
                event_dict['color'] = '#ffd7b5'  # coral
                event_dict['borderColor'] = '#f9a95d'
            event_dict['textColor'] = '#4a4a4a'
        
        # If not owner, slightly fade the event
        if not is_owner:
            event_dict['className'] += ' other-user-event'
        
        events_list.append(event_dict)
    
    return jsonify(events_list)