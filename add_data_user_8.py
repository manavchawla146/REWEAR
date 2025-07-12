#!/usr/bin/env python3
"""
Add swap history and point redemptions for user ID 8 (admin)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from PetPocket import create_app, db
from PetPocket.models import SwapHistory, PointRedemption, User, Product
from datetime import datetime, timedelta
import random

def add_data_for_user_8():
    app = create_app()
    with app.app_context():
        try:
            # Get user ID 8
            user_8 = User.query.get(8)
            if not user_8:
                print('User ID 8 not found')
                return
            
            print(f'Adding data for user: {user_8.username} (ID: {user_8.id})')
            
            # Get all users and products
            all_users = User.query.filter(User.id != 8).all()  # Exclude user 8
            all_products = Product.query.all()
            
            if not all_users or not all_products:
                print('Need other users and products to create swaps')
                return
            
            # Create 3 swaps for user 8
            swaps_created = []
            for i in range(3):
                other_user = random.choice(all_users)
                item1 = random.choice(all_products)
                item2 = random.choice([p for p in all_products if p.id != item1.id])
                
                # Randomly decide if user 8 is user1 or user2
                if random.choice([True, False]):
                    swap = SwapHistory(
                        user1_id=user_8.id,
                        user2_id=other_user.id,
                        item1_id=item1.id,
                        item2_id=item2.id,
                        completed_at=datetime.now() - timedelta(days=random.randint(1, 45))
                    )
                else:
                    swap = SwapHistory(
                        user1_id=other_user.id,
                        user2_id=user_8.id,
                        item1_id=item1.id,
                        item2_id=item2.id,
                        completed_at=datetime.now() - timedelta(days=random.randint(1, 45))
                    )
                
                swaps_created.append(swap)
                db.session.add(swap)
            
            # Create 4 point redemptions for user 8
            redemptions_created = []
            for i in range(4):
                product = random.choice(all_products)
                points_spent = random.choice([10, 15, 20, 25, 30, 35])
                
                redemption = PointRedemption(
                    user_id=user_8.id,
                    product_id=product.id,
                    points_spent=points_spent,
                    redeemed_at=datetime.now() - timedelta(days=random.randint(1, 60))
                )
                redemptions_created.append(redemption)
                db.session.add(redemption)
            
            db.session.commit()
            
            print(f'Successfully created:')
            print(f'- {len(swaps_created)} swaps for user {user_8.username}')
            print(f'- {len(redemptions_created)} point redemptions for user {user_8.username}')
            
            print('\nSwaps created:')
            for swap in swaps_created:
                if swap.user1_id == user_8.id:
                    other_user = User.query.get(swap.user2_id)
                    print(f'  {user_8.username} ({swap.item1.name}) <-> {other_user.username} ({swap.item2.name})')
                else:
                    other_user = User.query.get(swap.user1_id)
                    print(f'  {other_user.username} ({swap.item1.name}) <-> {user_8.username} ({swap.item2.name})')
            
            print('\nRedemptions created:')
            for redemption in redemptions_created:
                print(f'  {redemption.points_spent} points for {redemption.product.name}')
                
        except Exception as e:
            print(f'Error: {e}')
            db.session.rollback()

if __name__ == '__main__':
    add_data_for_user_8()
