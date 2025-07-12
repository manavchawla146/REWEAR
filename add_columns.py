#!/usr/bin/env python3
"""
Script to manually add the missing columns to the database.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PetPocket import create_app, db
import sqlite3

def add_missing_columns():
    """Add the missing columns to the database."""
    app = create_app()
    
    with app.app_context():
        try:
            # Get the database file path
            db_path = app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
            if not db_path:
                # Fallback to default path
                db_path = os.path.join(app.instance_path, 'petpocket.db')
            
            print(f"Database path: {db_path}")
            
            # Connect directly to SQLite
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if columns exist
            cursor.execute("PRAGMA table_info(products)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'points_required' not in columns:
                print("Adding points_required column to products table...")
                cursor.execute("ALTER TABLE products ADD COLUMN points_required INTEGER DEFAULT 10")
                print("✅ Added points_required column")
            else:
                print("points_required column already exists")
            
            cursor.execute("PRAGMA table_info(users)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'points_balance' not in columns:
                print("Adding points_balance column to users table...")
                cursor.execute("ALTER TABLE users ADD COLUMN points_balance INTEGER DEFAULT 0")
                print("✅ Added points_balance column")
            else:
                print("points_balance column already exists")
            
            conn.commit()
            conn.close()
            
            print("✅ Database columns added successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error adding columns: {e}")
            return False

if __name__ == "__main__":
    print("🔧 Adding missing database columns...")
    success = add_missing_columns()
    
    if success:
        print("\n🎉 Database update completed successfully!")
    else:
        print("\n💥 Database update failed!")
        sys.exit(1)
