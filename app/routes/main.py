from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.routes import main_bp
from app.models.event import Event
from app.models.task import Task
from app.models.reminder import Reminder
from datetime import datetime, date
from sqlalchemy import func

@main_bp.route('/')
@main_bp.route('/index')
@login_required
def index():
    """Dashboard/home page with real data."""
    
    # Get today's date range
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())
    
    # Count today's events for current user
    today_events = Event.query.filter(
        Event.user_id == current_user.id,
        Event.start_date >= today_start,
        Event.start_date <= today_end
    ).count()
    
    # Count pending tasks (not completed) for current user
    pending_tasks = Task.query.filter_by(
        user_id=current_user.id,
        completed=False
    ).count()
    
    # Count upcoming reminders (future) for current user
    upcoming_reminders = Reminder.query.filter(
        Reminder.user_id == current_user.id,
        Reminder.reminder_time >= datetime.utcnow()
    ).count()
    
    # Get recent tasks (latest 3, ordered by creation date)
    recent_tasks = Task.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Task.created_at.desc()
    ).limit(3).all()
    
    # Get upcoming reminders (next 3, ordered by reminder time)
    recent_reminders = Reminder.query.filter(
        Reminder.user_id == current_user.id,
        Reminder.reminder_time >= datetime.utcnow()
    ).order_by(
        Reminder.reminder_time.asc()
    ).limit(3).all()
    
    return render_template(
        'index.html',
        title='Dashboard',
        today_events=today_events,
        pending_tasks=pending_tasks,
        upcoming_reminders=upcoming_reminders,
        recent_tasks=recent_tasks,
        recent_reminders=recent_reminders
    )

# Add a public route for the root that redirects to login if not authenticated
@main_bp.route('/home')
def home():
    """Public home page - redirects to login or dashboard."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return redirect(url_for('auth.login'))