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
        start_datetime_str = request.form.get('start_datetime')
        end_datetime_str = request.form.get('end_datetime')
        
        print(f"ADD DEBUG - Start datetime: '{start_datetime_str}'")
        print(f"ADD DEBUG - End datetime: '{end_datetime_str}'")
        print(f"ADD DEBUG - Event type: {event_type}")
        print(f"ADD DEBUG - Joined user: {joined_user_id}")
        
        try:
            # Parse datetime in format: DD/MM/YY HH:MM AM/PM
            start_date = datetime.strptime(start_datetime_str, '%d/%m/%y %I:%M %p')
            end_date = datetime.strptime(end_datetime_str, '%d/%m/%y %I:%M %p')
            
            print(f"ADD DEBUG - Parsed start: {start_date}")
            print(f"ADD DEBUG - Parsed end: {end_date}")
            
            # For joined events, we create ONE event with both user IDs
            if event_type == 'joined' and joined_user_id:
                event = Event(
                    title=title,
                    description=description,
                    start_date=start_date,
                    end_date=end_date,
                    user_id=current_user.id,
                    event_type='joined',
                    joined_user_id=int(joined_user_id)
                )
                print(f"ADD DEBUG - Creating SHARED joined event for users: {current_user.id} and {joined_user_id}")
            else:
                event = Event(
                    title=title,
                    description=description,
                    start_date=start_date,
                    end_date=end_date,
                    user_id=current_user.id,
                    event_type='solo',
                    joined_user_id=None
                )
                print(f"ADD DEBUG - Creating solo event for user: {current_user.id}")
            
            db.session.add(event)
            db.session.commit()
            print(f"ADD DEBUG - Database committed successfully")
            
            flash('Event added successfully!', 'success')
            return redirect(url_for('calendar.index'))
            
        except ValueError as e:
            print(f"ADD DEBUG - Date parsing error: {e}")
            flash(f'Invalid date format. Please use DD/MM/YY format (e.g., 02/03/26 02:30 PM)', 'error')
            return render_template('calendar/add.html', title='Add Event', 
                                 form_data=request.form, users=User.query.all())
        except Exception as e:
            print(f"ADD DEBUG - Unexpected error: {e}")
            flash(f'Error creating event: {str(e)}', 'error')
            return render_template('calendar/add.html', title='Add Event', 
                                 form_data=request.form, users=User.query.all())
    
    # GET request
    users = User.query.all()
    return render_template('calendar/add.html', title='Add Event', users=users)

@calendar_bp.route('/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit(event_id):
    """Edit event - both users can edit joined events."""
    event = Event.query.get_or_404(event_id)
    
    # Check if user can edit this event
    if not event.can_edit(current_user.id):
        flash('You do not have permission to edit this event.', 'error')
        return redirect(url_for('calendar.index'))
    
    if request.method == 'POST':
        event.title = request.form.get('title')
        event.description = request.form.get('description')
        
        # Get the date and time strings - Note: form uses start_datetime and end_datetime
        start_datetime_str = request.form.get('start_datetime')
        end_datetime_str = request.form.get('end_datetime')
        
        print(f"EDIT DEBUG - Start datetime from form: '{start_datetime_str}'")
        print(f"EDIT DEBUG - End datetime from form: '{end_datetime_str}'")
        
        try:
            # Parse datetime in format: DD/MM/YY HH:MM AM/PM
            if start_datetime_str:
                event.start_date = datetime.strptime(start_datetime_str, '%d/%m/%y %I:%M %p')
                print(f"EDIT DEBUG - Parsed start: {event.start_date}")
            
            if end_datetime_str:
                event.end_date = datetime.strptime(end_datetime_str, '%d/%m/%y %I:%M %p')
                print(f"EDIT DEBUG - Parsed end: {event.end_date}")
            
            db.session.commit()
            print(f"EDIT DEBUG - After commit - Start: {event.start_date}, End: {event.end_date}")
            flash('Event updated successfully!', 'success')
            return redirect(url_for('calendar.index'))
            
        except ValueError as e:
            print(f"EDIT DEBUG - Date parsing error: {e}")
            flash('Invalid date/time format. Please use DD/MM/YY format (e.g., 02/03/26 02:30 PM)', 'error')
    
    # Format dates for display in the form
    formatted_start_date = event.start_date.strftime('%d/%m/%y') if event.start_date else ''
    formatted_start_time = event.start_date.strftime('%H:%M') if event.start_date else '12:00'
    formatted_end_date = event.end_date.strftime('%d/%m/%y') if event.end_date else ''
    formatted_end_time = event.end_date.strftime('%H:%M') if event.end_date else '13:00'
    
    print(f"EDIT DEBUG - Formatted for display - Start: {formatted_start_date} {formatted_start_time}, End: {formatted_end_date} {formatted_end_time}")
    
    # Get all users for display
    from app.models.user import User
    users = User.query.all()
    
    return render_template('calendar/edit.html', title='Edit Event', 
                         event=event, 
                         formatted_start_date=formatted_start_date,
                         formatted_start_time=formatted_start_time,
                         formatted_end_date=formatted_end_date,
                         formatted_end_time=formatted_end_time,
                         users=users)

@calendar_bp.route('/delete/<int:event_id>')
@login_required
def delete(event_id):
    """Delete event - both users can delete joined events."""
    event = Event.query.get_or_404(event_id)
    
    # Check if user can delete this event
    if not event.can_edit(current_user.id):  # Using same permission as edit
        flash('You do not have permission to delete this event.', 'error')
        return redirect(url_for('calendar.index'))
    
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('calendar.index'))

@calendar_bp.route('/api/events')
@login_required
def api_events():
    """API endpoint for calendar events - show all users' events."""
    # Get ALL events
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
        
        # For joined events, BOTH users can edit
        if event.event_type == 'joined':
            can_edit = (event.user_id == current_user.id or event.joined_user_id == current_user.id)
        else:
            can_edit = (event.user_id == current_user.id)
        
        # Format dates for display (12-hour format with AM/PM)
        # IMPORTANT: Make sure we're using the actual event dates
        formatted_start = event.start_date.strftime('%d/%m/%y %I:%M %p') if event.start_date else ''
        formatted_end = event.end_date.strftime('%d/%m/%y %I:%M %p') if event.end_date else ''
        
        print(f"API DEBUG - Event {event.id}: Start raw: {event.start_date}, Formatted: {formatted_start}")
        print(f"API DEBUG - Event {event.id}: End raw: {event.end_date}, Formatted: {formatted_end}")
        
        event_dict = {
            'id': event.id,
            'title': event.title,
            'start': event.start_date.isoformat(),
            'end': event.end_date.isoformat(),
            'formatted_start': formatted_start,
            'formatted_end': formatted_end,
            'description': event.description,
            'allDay': event.all_day,
            'event_type': event.event_type,
            'joined_user_id': event.joined_user_id,
            'joined_username': joined_username,
            'className': f"{event.event_type}-{color_scheme if event.event_type == 'solo' else 'joined'}",
            'color_scheme': color_scheme,
            'owner_id': event.user_id,
            'owner_username': owner_username,
            'can_edit': can_edit,
            'is_owner': (event.user_id == current_user.id)
        }
        
        # Set color based on event type
        if event.event_type == 'joined':
            event_dict['color'] = '#ffb6b6'
            event_dict['textColor'] = '#4a4a4a'
            event_dict['borderColor'] = '#f87171'
        else:
            if color_scheme == 'purple':
                event_dict['color'] = '#e6e6fa'
                event_dict['borderColor'] = '#c084fc'
            elif color_scheme == 'pink':
                event_dict['color'] = '#ffdab9'
                event_dict['borderColor'] = '#f9a8d4'
            elif color_scheme == 'blue':
                event_dict['color'] = '#b8e2f2'
                event_dict['borderColor'] = '#7aa5c7'
            elif color_scheme == 'orange':
                event_dict['color'] = '#ffd7b5'
                event_dict['borderColor'] = '#f9a95d'
            event_dict['textColor'] = '#4a4a4a'
        
        # If can't edit, slightly fade the event
        if not can_edit:
            event_dict['className'] += ' other-user-event'
        
        events_list.append(event_dict)
    
    return jsonify(events_list)