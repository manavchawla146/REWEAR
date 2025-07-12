#!/usr/bin/env python3
"""
Add sample point redemptions for testing
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from PetPocket import create_app, db
from PetPocket.models import PointRedemption, User, Product
from datetime import datetime, timedelta
import random

def add_sample_redemptions():
    app = create_app()
    with app.app_context():
        try:
            users = User.query.all()
            products = Product.query.all()
            
            print(f'Found {len(users)} users and {len(products)} products')
            
            if not users or not products:
                print('No users or products found in database')
                return
            
            # Check if redemptions already exist
            existing_redemptions = PointRedemption.query.count()
            if existing_redemptions > 0:
                print(f'Found {existing_redemptions} existing redemptions, skipping creation')
                return
            
            # Create some sample point redemptions
            sample_redemptions = []
            
            # Create redemptions for the first few users
            for i in range(min(5, len(users))):
                user = users[i]
                
                # Create 1-2 redemptions per user
                num_redemptions = random.randint(1, 2)
                for j in range(num_redemptions):
                    product = random.choice(products)
                    points_spent = random.choice([10, 15, 20, 25, 30])
                    
                    redemption = PointRedemption(
                        user_id=user.id,
                        product_id=product.id,
                        points_spent=points_spent,
                        redeemed_at=datetime.now() - timedelta(days=random.randint(1, 30))
                    )
                    sample_redemptions.append(redemption)
                    db.session.add(redemption)
            
            db.session.commit()
            print(f'Created {len(sample_redemptions)} sample point redemptions')
            
            # Show the redemptions
            for redemption in sample_redemptions:
                print(f'User {redemption.user.username} redeemed {redemption.points_spent} points for {redemption.product.name}')
                
        except Exception as e:
            print(f'Error: {e}')
            db.session.rollback()

if __name__ == '__main__':
    add_sample_redemptions()
