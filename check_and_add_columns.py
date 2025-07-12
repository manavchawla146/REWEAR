#!/usr/bin/env python3
"""
Script to check database path and add missing columns.
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
            # Check different possible database paths
            possible_paths = [
                os.path.join(os.getcwd(), 'instance', 'petpocket.db'),
                os.path.join(app.instance_path, 'petpocket.db'),
                'instance/petpocket.db',
                'petpocket.db'
            ]
            
            db_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    db_path = path
                    break
            
            if not db_path:
                print("❌ Could not find database file")
                return False
                
            print(f"Found database at: {db_path}")
            
            # Connect directly to SQLite
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # List all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"Tables in database: {[t[0] for t in tables]}")
            
            # Check if columns exist
            cursor.execute("PRAGMA table_info(products)")
            columns = [row[1] for row in cursor.fetchall()]
            print(f"Products table columns: {columns}")
            
            if 'points_required' not in columns:
                print("Adding points_required column to products table...")
                cursor.execute("ALTER TABLE products ADD COLUMN points_required INTEGER DEFAULT 10")
                print("✅ Added points_required column")
            else:
                print("points_required column already exists")
            
            cursor.execute("PRAGMA table_info(users)")
            columns = [row[1] for row in cursor.fetchall()]
            print(f"Users table columns: {columns}")
            
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
