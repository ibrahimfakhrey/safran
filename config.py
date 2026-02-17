"""
Flask application configuration
"""
import os
from datetime import timedelta

# Get absolute path to project directory
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration class with common settings"""
    
    # Secret key for session management and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # JWT configuration for mobile API
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Database configuration - Use Flask instance folder
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///app.db'  # Relative path creates instance/app.db automatically
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload folder for apartment images
    UPLOAD_FOLDER = os.path.join(basedir, 'app/static/images/apartments')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size for faster uploads
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Scheduler configuration for monthly rent payouts
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = "Africa/Cairo"  # Adjust to your timezone
    
    # Application settings
    ITEMS_PER_PAGE = 12  # For pagination
    
    # Color palette (Black & Gold Theme)
    PRIMARY_GOLD = "#FFD700"  # Bright Gold
    ACCENT_GOLD = "#FDB931"  # Lighter Gold
    BACKGROUND_BLACK = "#000000"  # Pure Black
    SECONDARY_BLACK = "#1A1A1A"  # Dark Gray
    TEXT_LIGHT = "#FFFFFF"  # White text
    
    # Admin credentials (in production, use environment variables)
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'amsprog2022@gmail.com'
    
    # Email configuration for OTP verification
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'ibrahimfakhreyams@gmail.com'
    MAIL_PASSWORD = 'miwz eeam nkrx oxvv'
    MAIL_DEFAULT_SENDER = ('i pillars i', os.environ.get('MAIL_USERNAME') or 'ibrahimfakhreyams@gmail.com')
    
    # OTP configuration
    OTP_EXPIRY_MINUTES = 10  # OTP expires after 10 minutes
    OTP_LENGTH = 6  # 6-digit OTP
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'Zo2lot@123'
    
    # Social Authentication Configuration
    # Google Sign-In
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID') or '7685982458-280u9fp7fk62230mikv3hl1asacieon0.apps.googleusercontent.com'
    GOOGLE_CLIENT_ID_IOS = '7685982458-280u9fp7fk62230mikv3hl1asacieon0.apps.googleusercontent.com'
    GOOGLE_CLIENT_ID_ANDROID = '7685982458-7hdh31pb18cgcaiedkd9dg9onidefvid.apps.googleusercontent.com'
    
    # Apple Sign-In (Bundle ID must match for iOS native apps)
    APPLE_CLIENT_ID = 'international.ipi.investment'
    APPLE_TEAM_ID = '52D8TDFTXN'
    APPLE_KEY_ID = '37XJXQAPKL'
    APPLE_PRIVATE_KEY_PATH = '/home/amsfiles/ipi/AuthKey_37XJXQAPKL.p8'
    
    # Firebase Admin SDK (NEW - Legacy Server Key is deprecated)
    # This should be the path to your service account JSON file
    # Or the JSON content as a string (for PythonAnywhere/Heroku)
    FIREBASE_SERVICE_ACCOUNT = os.environ.get('FIREBASE_SERVICE_ACCOUNT') or \
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'firebase-service-account.json')

class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Log SQL queries
    SCHEDULER_ENABLED = True  # Enable scheduler in development


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    SCHEDULER_ENABLED = False  # Disable scheduler in production (PythonAnywhere doesn't support it)
    # In production, ensure SECRET_KEY is set via environment variable
    FIREBASE_SERVICE_ACCOUNT = '/home/amsfiles/ipi/ipi-real-estate-c0afd-firebase-adminsdk-fbsvc-151d8cb4f2.json'
    

class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
