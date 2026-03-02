from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.routes import main_bp

@main_bp.route('/')
@main_bp.route('/index')
@login_required
def index():
    """Dashboard/home page."""
    return render_template('index.html', title='Dashboard')

# Add a public route for the root that redirects to login if not authenticated
@main_bp.route('/home')
def home():
    """Public home page - redirects to login or dashboard."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return redirect(url_for('auth.login'))