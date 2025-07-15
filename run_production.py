"""
Production WSGI entry point for Pet Pocket
"""
import os
import sys

# Add the application directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from PetPocket import create_app, db
from config_domain import ProductionConfig
from werkzeug.middleware.proxy_fix import ProxyFix

# Create the Flask application instance
app = create_app(ProductionConfig)

# Add proxy fix to handle headers from Nginx
# This will read the X-Script-Name header set by Nginx
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Initialize database tables
with app.app_context():
    try:
        # Create all database tables if they don't exist
        db.create_all()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")

if __name__ == "__main__":
    # This is for local testing only
    app.run(host="0.0.0.0", port=8000, debug=False)
