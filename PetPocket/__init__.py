from flask import Flask, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_login import current_user
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect, CSRFError
import os
import razorpay
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from .config import Config

# Initialize SQLAlchemy
db = SQLAlchemy()

# Initialize Flask-Mail
mail = Mail()

# Initialize CSRF protection
csrf = CSRFProtect()

# Initialize Razorpay client as None first
razorpay_client = None

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Force template reloading - critical for demo credentials to show
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.jinja_env.auto_reload = True
    app.jinja_env.cache = {}
    
    # Initialize extensions
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.login_view = 'main.signin'
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Configure CSRF protection
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour
    app.config['WTF_CSRF_SSL_STRICT'] = False  # Set to True in production
    
    # Add Razorpay configuration
    app.config['RAZORPAY_KEY_ID'] = 'rzp_test_QTmdq1PBiByYN9'
    app.config['RAZORPAY_KEY_SECRET'] = 'TNgY0GTvtMjHsl5pSm9Stlsy'
    
    # Replace with valid credentials from Google Cloud Console
    app.config['GOOGLE_CLIENT_ID'] = '780308680733-150vt09u8286otguf6krlq5um3nsbrf7.apps.googleusercontent.com'
    app.config['GOOGLE_CLIENT_SECRET'] = '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'
    
    # Initialize Razorpay client
    global razorpay_client
    razorpay_client = razorpay.Client(
        auth=(app.config['RAZORPAY_KEY_ID'], app.config['RAZORPAY_KEY_SECRET'])
    )
    
    # Initialize Flask-Migrate
    migrate = Migrate(app, db)
    
    # Custom unauthorized handler for AJAX requests
    @login_manager.unauthorized_handler
    def unauthorized():
        if request.is_json:
            return jsonify({'success': False, 'message': 'Authentication required.'}), 401
        return redirect(url_for('main.signin'))
    
    from .models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints with explicit prefixes
    from .routes import main
    from .auth import auth
    from .admin.analytics import admin_analytics
    
    app.register_blueprint(main, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(admin_analytics, url_prefix='/admin')
    
    # Import admin after initializing extensions and registering blueprints
    from .admin import init_admin
    init_admin(app, db)
    
    @app.context_processor
    def inject_cart_count():
        from .models import CartItem
        from sqlalchemy import func
        if current_user.is_authenticated:
            cart_count = db.session.query(func.sum(CartItem.quantity)).filter_by(user_id=current_user.id).scalar() or 0
            cart_count = int(cart_count)
        else:
            cart_count = 0
        return dict(cart_count=cart_count)
    
    # Configure Flask-Mail
    app.config.update(
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USERNAME=os.environ.get('MAIL_USERNAME', 'manavdodani2005@gmail.com'),
        MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD', 'efpd snbt djxw wesj'),
        MAIL_DEFAULT_SENDER=('PetPocket Admin', 'manavdodani2005@gmail.com')
    )
    
    mail.init_app(app)
    
    # Add COOP header to allow Google OAuth popups
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Only add HTTPS headers in production
        if not app.debug:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://accounts.google.com https://apis.google.com https://cdnjs.cloudflare.com https://kit.fontawesome.com https://checkout.razorpay.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com https://cdn.jsdelivr.net; "
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "frame-src 'self' https://accounts.google.com https://api.razorpay.com; "
            "connect-src 'self' https://accounts.google.com https://apis.google.com https://lumberjack.razorpay.com;"
        )
        response.headers['Cross-Origin-Opener-Policy'] = 'same-origin-allow-popups'
        return response
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        if request.is_json:
            return jsonify({'success': False, 'message': str(error)}), 400
        return f'Bad Request: {error}', 400

    @app.errorhandler(401)
    def unauthorized(error):
        if request.is_json:
            return jsonify({'success': False, 'message': 'Please login to continue'}), 401
        return redirect(url_for('auth.signin'))

    @app.errorhandler(404)
    def not_found(error):
        if request.is_json:
            return jsonify({'success': False, 'message': 'Resource not found'}), 404
        return 'Page not found', 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'message': 'Internal server error'}), 500
        return 'Internal server error', 500

    # CSRF error handler
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        if request.is_json:
            return jsonify({'success': False, 'message': 'CSRF token validation failed'}), 400
        return 'CSRF token validation failed', 400
    
    return app