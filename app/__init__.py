from flask import Flask, redirect, url_for
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from config import config
import os

# Initialize extensions (without app)
from app.extensions import db, login_manager

migrate = Migrate()

def create_app(config_name=None):
    """Application factory function."""
    app = Flask(__name__)
    
    # Determine configuration based on environment
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Import models for user_loader
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login."""
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.routes import auth_bp, calendar_bp, todos_bp, reminders_bp, admin_bp, main_bp
    
    app.register_blueprint(main_bp)  # No prefix for main
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(calendar_bp, url_prefix='/calendar')
    app.register_blueprint(todos_bp, url_prefix='/todos')
    app.register_blueprint(reminders_bp, url_prefix='/reminders')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Add a root route directly in the app
    @app.route('/')
    def root():
        """Root URL - redirect to main index or login."""
        if current_user.is_authenticated:
            return redirect(url_for('main.index'))
        return redirect(url_for('auth.login'))
    
    # Create tables only if they don't exist (optional, consider using migrations instead)
    with app.app_context():
        # This is safe to run - it won't overwrite existing tables
        db.create_all()
        print("✅ Database tables verified/created")
    
    return app