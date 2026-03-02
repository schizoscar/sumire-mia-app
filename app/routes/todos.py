from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.task import Task
from app.routes import todos_bp
from datetime import datetime

@todos_bp.route('/')
@login_required
def index():
    """To-do list view."""
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    return render_template('todos/index.html', title='To-Do List', tasks=tasks)

@todos_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add new task."""
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
    """Edit task."""
    task = Task.query.get_or_404(task_id)
    
    if task.user_id != current_user.id:
        flash('You cannot edit this task.', 'error')
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
    """Toggle task completion."""
    task = Task.query.get_or_404(task_id)
    
    if task.user_id != current_user.id:
        flash('You cannot modify this task.', 'error')
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
    """Delete task."""
    task = Task.query.get_or_404(task_id)
    
    if task.user_id != current_user.id:
        flash('You cannot delete this task.', 'error')
        return redirect(url_for('todos.index'))
    
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('todos.index'))