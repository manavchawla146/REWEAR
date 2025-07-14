"""
Google App Engine entry point
"""
import os
from PetPocket import create_app, db
from PetPocket.config import ProductionConfig

# Create the Flask application instance for App Engine
app = create_app(ProductionConfig)

# Initialize database tables on first deployment
with app.app_context():
    try:
        # Create all database tables if they don't exist
        db.create_all()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")

if __name__ == "__main__":
    # This is used for local testing
    app.run(host="127.0.0.1", port=8080, debug=False)
