from flask import Blueprint

# Create blueprints
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
calendar_bp = Blueprint('calendar', __name__)
todos_bp = Blueprint('todos', __name__)
reminders_bp = Blueprint('reminders', __name__)
admin_bp = Blueprint('admin', __name__)

# Import routes to register them
from app.routes import auth, calendar, todos, reminders, admin, main