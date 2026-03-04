import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

# Create the Flask application
app = create_app('production')

# Vercel serverless handler expects a function named 'handler'
def handler(request, context):
    return app(request.environ, lambda *args: None)