import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Force production environment
os.environ['FLASK_ENV'] = 'production'

# Import and create app
from app import create_app
app = create_app('production')

# Vercel serverless handler
def handler(request):
    return app(request)