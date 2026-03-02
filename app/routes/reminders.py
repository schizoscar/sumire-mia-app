from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.reminder import Reminder
from app.routes import reminders_bp
from datetime import datetime

@reminders_bp.route('/')
@login_required
def index():
    """Reminders view."""
    reminders = Reminder.query.filter_by(user_id=current_user.id).order_by(Reminder.reminder_time).all()
    return render_template('reminders/index.html', title='Reminders', reminders=reminders)

@reminders_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add new reminder."""
    if request.method == 'POST':
        title = request.form.get('title')
        message = request.form.get('message')
        reminder_time = datetime.fromisoformat(request.form.get('reminder_time'))
        repeat = request.form.get('repeat', 'none')
        
        reminder = Reminder(
            title=title,
            message=message,
            reminder_time=reminder_time,
            repeat=repeat,
            user_id=current_user.id
        )
        
        db.session.add(reminder)
        db.session.commit()
        
        flash('Reminder added successfully!', 'success')
        return redirect(url_for('reminders.index'))
    
    return render_template('reminders/add.html', title='Add Reminder')

@reminders_bp.route('/edit/<int:reminder_id>', methods=['GET', 'POST'])
@login_required
def edit(reminder_id):
    """Edit reminder."""
    reminder = Reminder.query.get_or_404(reminder_id)
    
    if reminder.user_id != current_user.id:
        flash('You cannot edit this reminder.', 'error')
        return redirect(url_for('reminders.index'))
    
    if request.method == 'POST':
        reminder.title = request.form.get('title')
        reminder.message = request.form.get('message')
        reminder.reminder_time = datetime.fromisoformat(request.form.get('reminder_time'))
        reminder.repeat = request.form.get('repeat', 'none')
        
        db.session.commit()
        flash('Reminder updated successfully!', 'success')
        return redirect(url_for('reminders.index'))
    
    return render_template('reminders/edit.html', title='Edit Reminder', reminder=reminder)

@reminders_bp.route('/delete/<int:reminder_id>')
@login_required
def delete(reminder_id):
    """Delete reminder."""
    reminder = Reminder.query.get_or_404(reminder_id)
    
    if reminder.user_id != current_user.id:
        flash('You cannot delete this reminder.', 'error')
        return redirect(url_for('reminders.index'))
    
    db.session.delete(reminder)
    db.session.commit()
    flash('Reminder deleted successfully!', 'success')
    return redirect(url_for('reminders.index'))