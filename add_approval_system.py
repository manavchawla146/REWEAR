#!/usr/bin/env python3
"""
Script to add approval system to the database
"""
import sqlite3
import os

# Database path
db_path = os.path.join('instance', 'petpocket.db')

def add_approval_columns():
    """Add approval system columns to the products table"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add approval columns to products table
        cursor.execute('ALTER TABLE products ADD COLUMN is_approved BOOLEAN DEFAULT FALSE')
        cursor.execute('ALTER TABLE products ADD COLUMN approval_status VARCHAR(20) DEFAULT "pending"')
        cursor.execute('ALTER TABLE products ADD COLUMN approved_by INTEGER')
        cursor.execute('ALTER TABLE products ADD COLUMN approved_at DATETIME')
        cursor.execute('ALTER TABLE products ADD COLUMN rejection_reason TEXT')
        
        print("Added approval columns to products table")
        
        # Create swap_requests table
        cursor.execute('''
            CREATE TABLE swap_requests (
                id INTEGER PRIMARY KEY,
                requester_id INTEGER NOT NULL,
                requested_item_id INTEGER NOT NULL,
                offered_item_id INTEGER NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                requester_approved BOOLEAN DEFAULT TRUE,
                owner_approved BOOLEAN DEFAULT FALSE,
                responded_at DATETIME,
                completed_at DATETIME,
                rejection_reason TEXT,
                FOREIGN KEY (requester_id) REFERENCES users (id),
                FOREIGN KEY (requested_item_id) REFERENCES products (id),
                FOREIGN KEY (offered_item_id) REFERENCES products (id)
            )
        ''')
        
        print("Created swap_requests table")
        
        # Update existing products to be approved by default (for testing)
        cursor.execute('UPDATE products SET is_approved = TRUE, approval_status = "approved" WHERE is_approved IS NULL OR is_approved = FALSE')
        
        print("Updated existing products to approved status")
        
        conn.commit()
        print("Database updated successfully!")
        
    except sqlite3.Error as e:
        if "duplicate column name" in str(e):
            print("Approval columns already exist")
        elif "table swap_requests already exists" in str(e):
            print("Swap requests table already exists")
        else:
            print(f"Error: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == '__main__':
    if os.path.exists(db_path):
        add_approval_columns()
    else:
        print(f"Database not found at {db_path}")
