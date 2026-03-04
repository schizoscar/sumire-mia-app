import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database - handle both Render and Vercel/Neon formats
    # Vercel/Neon might use POSTGRES_URL, Render uses DATABASE_URL
    database_url = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')
    
    if database_url:
        # Handle both postgres:// and postgresql://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
    else:
        # Fallback for local development
        database_url = 'postgresql://localhost/sumire_mia_db'
    
    SQLALCHEMY_DATABASE_URI = database_url
    
    # App settings
    APP_NAME = os.environ.get('APP_NAME', 'すみれ＆みあ')
    
    # SendGrid settings
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    SENDGRID_FROM_EMAIL = os.environ.get('SENDGRID_FROM_EMAIL', 'noreply@example.com')
    SENDGRID_FROM_NAME = os.environ.get('SENDGRID_FROM_NAME', 'すみれ＆みあ')
    
    # URL for the app (important for email links)
    APP_URL = os.environ.get('APP_URL', 'http://localhost:5000')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    
class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    
# Choose config based on environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}