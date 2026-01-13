"""
Main application initialization file
Sets up Flask app, database, login manager, scheduler, JWT, CORS, and Mail
"""
from flask import Flask
from flask_login import LoginManager
try:
    from flask_apscheduler import APScheduler
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False
    APScheduler = None
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import config
from app.models import db, User
from app.utils.email_service import mail
import os


# Initialize login manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة'

# Initialize scheduler (only if available)
if SCHEDULER_AVAILABLE:
    scheduler = APScheduler()
else:
    scheduler = None

# Initialize JWT manager
jwt = JWTManager()


@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return User.query.get(int(user_id))


def create_app(config_name='development'):
    """Create and configure Flask application"""
    # CRITICAL: Disable instance folder to prevent creating instance/app.db
    app = Flask(__name__, instance_relative_config=False)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)  # Initialize Flask-Mail
    if SCHEDULER_AVAILABLE and scheduler:
        scheduler.init_app(app)
    jwt.init_app(app)
    
    # Enable CORS for API endpoints
    # Enable CORS for all routes including static files
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from app.routes import auth, main, admin, user_views, api, admin_api, fleet, driver_api
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(user_views.bp)
    app.register_blueprint(api.api_bp)  # Register API blueprint
    app.register_blueprint(admin_api.bp)  # Register Admin API blueprint
    app.register_blueprint(fleet.fleet)  # Register Fleet Management blueprint
    app.register_blueprint(driver_api.driver_api_bp)  # Register Driver API blueprint
    
    # Create database tables
    with app.app_context():
        # DEBUG: Print database path
        print(f">>> DATABASE PATH: {app.config['SQLALCHEMY_DATABASE_URI']}")
        db.create_all()
        create_admin_user(app)
    
    
    # Start scheduler for monthly payouts (only if available and enabled)
    if SCHEDULER_AVAILABLE and scheduler and app.config.get('SCHEDULER_ENABLED', False) and not scheduler.running:
        try:
            scheduler.start()
        except RuntimeError as e:
            # Scheduler not available in this environment
            app.logger.warning(f"Scheduler not started: {e}")
    
    return app


def create_admin_user(app):
    """Create default admin user if it doesn't exist"""
    from app.models import User
    
    # HARDCODED admin credentials to prevent environment variable override
    ADMIN_EMAIL = 'amsprog2022@gmail.com'
    ADMIN_PASSWORD = 'Zo2lot@123'
    
    admin = User.query.filter_by(email=ADMIN_EMAIL).first()
    if not admin:
        admin = User(
            name='Admin',
            email=ADMIN_EMAIL,
            is_admin=True,
            referral_number='IPI000001'
        )
        admin.set_password(ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user created: {ADMIN_EMAIL}")


def schedule_monthly_payouts():
    """
    Scheduled task to distribute monthly rent to all investors
    Runs on the 1st day of each month at 00:00
    """
    from app.models import Apartment
    from datetime import datetime
    
    apartments = Apartment.query.filter_by(is_closed=True).all()
    total_payouts = 0
    
    for apartment in apartments:
        payouts = apartment.distribute_monthly_rent()
        total_payouts += payouts
    
    db.session.commit()
    print(f"Monthly payouts completed: {total_payouts} payments processed at {datetime.utcnow()}")


# Register scheduled tasks (only if scheduler is available)
if SCHEDULER_AVAILABLE and scheduler:
    @scheduler.task('cron', id='automatic_monthly_payouts', hour=0, minute=5)
    def scheduled_automatic_payouts():
        """
        Automatic monthly payout distributor
        Runs daily at 00:05 AM
        Distributes rental income to all investors based on approval date
        """
        with scheduler.app.app_context():
            from app.utils.auto_payouts import process_automatic_payouts
            result = process_automatic_payouts()
            
            if result['success']:
                print(f"✅ Auto-payout: Processed {result['shares_processed']} shares, distributed {result['total_distributed']:.2f} EGP")
            else:
                print(f"❌ Auto-payout: Failed with errors: {result['errors']}")
