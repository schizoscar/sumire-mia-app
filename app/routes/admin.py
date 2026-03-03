from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User
from app.routes import admin_bp
from app.services.email_service import send_invitation_email
import secrets
import string

@admin_bp.route('/users')
@login_required
def users():
    """User management view."""
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))
    
    users_list = User.query.all()
    return render_template('admin/users.html', title='Manage Users', users=users_list)

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    """Add new user."""
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        color_scheme = request.form.get('color_scheme', 'purple')
        is_admin = request.form.get('is_admin') == '1'
        send_invite = request.form.get('send_invite') == 'on'
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('admin.add_user'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('admin.add_user'))
        
        # Generate temporary password
        alphabet = string.ascii_letters + string.digits
        temp_password = ''.join(secrets.choice(alphabet) for i in range(12))
        
        # Create new user
        user = User(
            username=username,
            email=email,
            color_scheme=color_scheme,
            is_admin=is_admin,
            is_active=True
        )
        user.set_password(temp_password)
        
        db.session.add(user)
        db.session.commit()
        
        # Send invitation email
        if send_invite:
            try:
                send_invitation_email(email, username, temp_password)
                flash(f'User created and invitation sent to {email}!', 'success')
            except Exception as e:
                flash(f'User created but email could not be sent. Temporary password: {temp_password}', 'warning')
        else:
            flash(f'User created. Temporary password: {temp_password}', 'info')
        
        return redirect(url_for('admin.users'))
    
    return render_template('admin/add_user.html', title='Add User')

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """Edit user."""
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        # Get form data
        new_username = request.form.get('username')
        new_email = request.form.get('email')
        color_scheme = request.form.get('color_scheme')
        is_admin = request.form.get('is_admin') == '1'
        is_active = request.form.get('is_active') == '1'
        reset_password = request.form.get('reset_password') == 'on'
        
        # Check if username is taken (by someone else)
        if new_username != user.username:
            existing = User.query.filter_by(username=new_username).first()
            if existing:
                flash('Username already taken', 'error')
                return redirect(url_for('admin.edit_user', user_id=user.id))
        
        # Check if email is taken (by someone else)
        if new_email != user.email:
            existing = User.query.filter_by(email=new_email).first()
            if existing:
                flash('Email already registered', 'error')
                return redirect(url_for('admin.edit_user', user_id=user.id))
        
        # Update user
        user.username = new_username
        user.email = new_email
        user.color_scheme = color_scheme
        user.is_admin = is_admin
        user.is_active = is_active
        
        # Reset password if requested
        if reset_password:
            import secrets
            import string
            alphabet = string.ascii_letters + string.digits
            temp_password = ''.join(secrets.choice(alphabet) for i in range(12))
            user.set_password(temp_password)
            
            # Send password reset email
            try:
                from app.services.email_service import send_password_reset_email
                send_password_reset_email(user.email, user.username, temp_password)
                flash(f'Password reset. New password sent to {user.email}', 'success')
            except Exception as e:
                print(f"Email error: {e}")
                flash(f'Password reset. Temporary password: {temp_password}', 'warning')
        
        db.session.commit()
        flash(f'User {user.username} updated successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/edit_user.html', title='Edit User', user=user)

@admin_bp.route('/users/toggle/<int:user_id>')
@login_required
def toggle_user(user_id):
    """Activate/deactivate user."""
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    
    # Don't allow deactivating yourself
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'error')
        return redirect(url_for('admin.users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} {status}.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/delete/<int:user_id>')
@login_required
def delete_user(user_id):
    """Delete user."""
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    
    # Don't allow deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} deleted.', 'success')
    return redirect(url_for('admin.users'))