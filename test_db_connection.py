#!/usr/bin/env python3
"""
Simple database reset test
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from PetPocket import create_app, db
    print("✅ Successfully imported PetPocket")
    
    app = create_app()
    print("✅ Successfully created app")
    
    with app.app_context():
        print("✅ Successfully entered app context")
        
        # Test database connection
        result = db.session.execute(db.text('SELECT 1')).fetchone()
        print(f"✅ Database connection test: {result}")
        
        # Get table names
        tables_result = db.session.execute(db.text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
        tables = [row[0] for row in tables_result]
        print(f"✅ Found {len(tables)} tables: {tables}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
