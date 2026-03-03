from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.task import Task
from app.routes import todos_bp
from datetime import datetime
from sqlalchemy import case

@todos_bp.route('/')
@login_required
def index():
    """To-do list view - show all tasks from all users."""
    # Show ALL tasks, ordered by completion status and date
    tasks = Task.query.order_by(
        Task.completed.asc(),  # Incomplete first
        case(
            (Task.completed == True, Task.completed_at),
            else_=Task.created_at
        ).desc()  # Then by completed date (for completed) or created date (for incomplete)
    ).all()
    return render_template('todos/index.html', title='To-Do List', tasks=tasks)

@todos_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add new task - owned by current user."""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date = request.form.get('due_date')
        priority = request.form.get('priority', 3)
        
        task = Task(
            title=title,
            description=description,
            priority=int(priority),
            user_id=current_user.id
        )
        
        if due_date:
            task.due_date = datetime.fromisoformat(due_date)
        
        db.session.add(task)
        db.session.commit()
        
        flash('Task added successfully!', 'success')
        return redirect(url_for('todos.index'))
    
    return render_template('todos/add.html', title='Add Task')

@todos_bp.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit(task_id):
    """Edit task - only owner can edit."""
    task = Task.query.get_or_404(task_id)
    
    if task.user_id != current_user.id:
        flash('You can only edit your own tasks.', 'error')
        return redirect(url_for('todos.index'))
    
    if request.method == 'POST':
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        task.priority = int(request.form.get('priority', 3))
        
        due_date = request.form.get('due_date')
        if due_date:
            task.due_date = datetime.fromisoformat(due_date)
        else:
            task.due_date = None
        
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('todos.index'))
    
    return render_template('todos/edit.html', title='Edit Task', task=task)

@todos_bp.route('/toggle/<int:task_id>')
@login_required
def toggle(task_id):
    """Toggle task completion - only owner can toggle."""
    task = Task.query.get_or_404(task_id)
    
    # Only allow toggling if user owns the task
    if task.user_id != current_user.id:
        flash('You can only modify your own tasks.', 'error')
        return redirect(url_for('todos.index'))
    
    task.completed = not task.completed
    if task.completed:
        task.completed_at = datetime.utcnow()
    else:
        task.completed_at = None
    
    db.session.commit()
    return redirect(url_for('todos.index'))

@todos_bp.route('/delete/<int:task_id>')
@login_required
def delete(task_id):
    """Delete task - only owner can delete."""
    task = Task.query.get_or_404(task_id)
    
    if task.user_id != current_user.id:
        flash('You can only delete your own tasks.', 'error')
        return redirect(url_for('todos.index'))
    
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('todos.index'))

@todos_bp.route('/api/tasks')
@login_required
def api_tasks():
    """API endpoint for tasks - show all users' tasks."""
    # Get ALL tasks
    tasks = Task.query.order_by(
        Task.completed.asc(),
        Task.created_at.desc()
    ).all()
    
    tasks_list = []
    for task in tasks:
        # Get the owner's info
        owner = task.task_owner
        owner_username = owner.username if owner else 'Unknown'
        color_scheme = owner.color_scheme if owner else 'purple'
        
        # Determine if current user is the owner
        is_owner = (task.user_id == current_user.id)
        
        task_dict = {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'completed': task.completed,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'priority': task.priority,
            'owner_id': task.user_id,
            'owner_username': owner_username,
            'color_scheme': color_scheme,
            'is_owner': is_owner,
            'className': 'other-user-task' if not is_owner else ''
        }
        
        tasks_list.append(task_dict)
    
    return jsonify(tasks_list)