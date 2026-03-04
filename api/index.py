import os
import sys
import logging

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logging.basicConfig(level=logging.INFO)

# Force production environment
os.environ['FLASK_ENV'] = 'production'

# Import and create app
from app import create_app
app = create_app('production')

# Vercel serverless handler
def handler(request):
    return app(request)

# For local development
if __name__ == '__main__':
    app.run()
