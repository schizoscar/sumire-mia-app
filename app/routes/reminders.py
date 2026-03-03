from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.reminder import Reminder
from app.routes import reminders_bp
from datetime import datetime
from app.models.user import User

@reminders_bp.route('/')
@login_required
def index():
    """Reminders list view - show all reminders from all users."""
    # Show all reminders, ordered by reminder time (upcoming first)
    reminders = Reminder.query.order_by(
        Reminder.reminder_time.asc()
    ).all()
    return render_template('reminders/index.html', title='Reminders', reminders=reminders)

@reminders_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add new reminder - owned by current user."""
    if request.method == 'POST':
        title = request.form.get('title')
        message = request.form.get('message')
        reminder_time_str = request.form.get('reminder_time')
        repeat = request.form.get('repeat', 'none')
        repeat_until_str = request.form.get('repeat_until')
        
        print(f"DEBUG - reminder_time_str: '{reminder_time_str}'")
        print(f"DEBUG - repeat_until_str: '{repeat_until_str}'")
        
        try:
            # Parse reminder time from datetime-local format (YYYY-MM-DDTHH:MM)
            if reminder_time_str:
                # datetime-local format: "2024-03-02T14:30"
                reminder_time = datetime.fromisoformat(reminder_time_str.replace('T', ' '))
            else:
                flash('Please select a reminder time.', 'error')
                return render_template('reminders/add.html', title='Add Reminder', 
                                     form_data=request.form)
            
            # Create reminder
            reminder = Reminder(
                title=title,
                message=message,
                reminder_time=reminder_time,
                repeat=repeat,
                user_id=current_user.id
            )
            
            # Parse repeat until if provided
            if repeat_until_str and repeat != 'none':
                reminder.repeat_until = datetime.fromisoformat(repeat_until_str.replace('T', ' '))
            
            db.session.add(reminder)
            db.session.commit()
            
            flash('Reminder added successfully!', 'success')
            return redirect(url_for('reminders.index'))
            
        except ValueError as e:
            print(f"DEBUG - Date parsing error: {e}")
            flash('Invalid date format. Please use the date picker to select a valid date and time.', 'error')
            return render_template('reminders/add.html', title='Add Reminder', 
                                 form_data=request.form)
        except Exception as e:
            print(f"DEBUG - Unexpected error: {e}")
            flash(f'Error creating reminder: {str(e)}', 'error')
            return render_template('reminders/add.html', title='Add Reminder', 
                                 form_data=request.form)
    
    # GET request
    return render_template('reminders/add.html', title='Add Reminder')

@reminders_bp.route('/edit/<int:reminder_id>', methods=['GET', 'POST'])
@login_required
def edit(reminder_id):
    """Edit reminder - only owner can edit."""
    reminder = Reminder.query.get_or_404(reminder_id)
    
    # Check if user owns this reminder
    if reminder.user_id != current_user.id:
        flash('You can only edit your own reminders.', 'error')
        return redirect(url_for('reminders.index'))
    
    if request.method == 'POST':
        reminder.title = request.form.get('title')
        reminder.message = request.form.get('message')
        
        reminder_time_str = request.form.get('reminder_time')
        repeat = request.form.get('repeat', 'none')
        repeat_until_str = request.form.get('repeat_until')
        
        try:
            # Parse reminder time from datetime-local format
            if reminder_time_str:
                reminder.reminder_time = datetime.fromisoformat(reminder_time_str.replace('T', ' '))
            
            reminder.repeat = repeat
            
            # Parse repeat until if provided
            if repeat_until_str and repeat != 'none':
                reminder.repeat_until = datetime.fromisoformat(repeat_until_str.replace('T', ' '))
            else:
                reminder.repeat_until = None
            
            db.session.commit()
            flash('Reminder updated successfully!', 'success')
            return redirect(url_for('reminders.index'))
            
        except ValueError as e:
            print(f"DEBUG - Date parsing error: {e}")
            flash('Invalid date format. Please use the date picker to select a valid date and time.', 'error')
    
    # Format dates for display in the form (convert to datetime-local format)
    formatted_reminder_time = reminder.reminder_time.strftime('%Y-%m-%dT%H:%M') if reminder.reminder_time else ''
    formatted_repeat_until = reminder.repeat_until.strftime('%Y-%m-%dT%H:%M') if reminder.repeat_until else ''
    
    return render_template('reminders/edit.html', title='Edit Reminder', 
                         reminder=reminder,
                         formatted_reminder_time=formatted_reminder_time,
                         formatted_repeat_until=formatted_repeat_until)

@reminders_bp.route('/delete/<int:reminder_id>')
@login_required
def delete(reminder_id):
    """Delete reminder - only owner can delete."""
    reminder = Reminder.query.get_or_404(reminder_id)
    
    # Check if user owns this reminder
    if reminder.user_id != current_user.id:
        flash('You can only delete your own reminders.', 'error')
        return redirect(url_for('reminders.index'))
    
    db.session.delete(reminder)
    db.session.commit()
    flash('Reminder deleted successfully!', 'success')
    return redirect(url_for('reminders.index'))

@reminders_bp.route('/api/reminders')
@login_required
def api_reminders():
    """API endpoint for reminders - show all users' reminders."""
    # Get ALL reminders, not just current user's
    reminders = Reminder.query.all()
    reminders_list = []
    
    for reminder in reminders:
        # Get the owner's info
        owner = reminder.reminder_owner
        owner_username = owner.username if owner else 'Unknown'
        color_scheme = owner.color_scheme if owner else 'purple'
        
        # Determine if current user is the owner
        is_owner = (reminder.user_id == current_user.id)
        
        reminder_dict = {
            'id': reminder.id,
            'title': reminder.title,
            'message': reminder.message,
            'reminder_time': reminder.reminder_time.isoformat(),
            'repeat': reminder.repeat,
            'repeat_until': reminder.repeat_until.isoformat() if reminder.repeat_until else None,
            'is_sent': reminder.is_sent,
            'owner_id': reminder.user_id,
            'owner_username': owner_username,
            'color_scheme': color_scheme,
            'is_owner': is_owner,
            'className': 'other-user-reminder' if not is_owner else ''
        }
        
        reminders_list.append(reminder_dict)
    
    return jsonify(reminders_list)