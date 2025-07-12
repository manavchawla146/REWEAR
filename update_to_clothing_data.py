#!/usr/bin/env python3
"""
Update swap history and redemptions to use clothing products
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from PetPocket import create_app, db
from PetPocket.models import SwapHistory, PointRedemption, User, Product
from datetime import datetime, timedelta
import random

def update_to_clothing_data():
    app = create_app()
    with app.app_context():
        try:
            # Get clothing products (the ones we just added)
            clothing_products = Product.query.filter(
                Product.name.in_([
                    'Vintage Denim Jacket', 'Black Leather Boots', 'Floral Summer Dress',
                    'Designer Blue Jeans', 'Cashmere Sweater', 'Silk Scarf',
                    'White Button-Up Shirt', 'Leather Handbag'
                ])
            ).all()
            
            if not clothing_products:
                print('No clothing products found! Run add_clothing_products.py first.')
                return
            
            print(f'Found {len(clothing_products)} clothing products')
            
            # Clear existing swaps and redemptions
            SwapHistory.query.delete()
            PointRedemption.query.delete()
            
            # Get users
            users = User.query.all()
            if len(users) < 2:
                print('Need at least 2 users for swaps')
                return
            
            # Create new clothing-focused swaps
            swaps_created = []
            for i in range(4):
                user1 = random.choice(users)
                user2 = random.choice([u for u in users if u.id != user1.id])
                item1 = random.choice(clothing_products)
                item2 = random.choice([p for p in clothing_products if p.id != item1.id])
                
                swap = SwapHistory(
                    user1_id=user1.id,
                    user2_id=user2.id,
                    item1_id=item1.id,
                    item2_id=item2.id,
                    completed_at=datetime.now() - timedelta(days=random.randint(1, 30))
                )
                swaps_created.append(swap)
                db.session.add(swap)
            
            # Create new clothing-focused redemptions
            redemptions_created = []
            for i in range(8):
                user = random.choice(users)
                product = random.choice(clothing_products)
                
                redemption = PointRedemption(
                    user_id=user.id,
                    product_id=product.id,
                    points_spent=product.points_required,
                    redeemed_at=datetime.now() - timedelta(days=random.randint(1, 45))
                )
                redemptions_created.append(redemption)
                db.session.add(redemption)
            
            # Ensure user ID 8 has some data
            user_8 = User.query.get(8)
            if user_8:
                # Add specific swaps for user 8
                other_users = [u for u in users if u.id != 8]
                for i in range(2):
                    other_user = random.choice(other_users)
                    item1 = random.choice(clothing_products)
                    item2 = random.choice([p for p in clothing_products if p.id != item1.id])
                    
                    swap = SwapHistory(
                        user1_id=user_8.id,
                        user2_id=other_user.id,
                        item1_id=item1.id,
                        item2_id=item2.id,
                        completed_at=datetime.now() - timedelta(days=random.randint(1, 20))
                    )
                    swaps_created.append(swap)
                    db.session.add(swap)
                
                # Add specific redemptions for user 8
                for i in range(3):
                    product = random.choice(clothing_products)
                    redemption = PointRedemption(
                        user_id=user_8.id,
                        product_id=product.id,
                        points_spent=product.points_required,
                        redeemed_at=datetime.now() - timedelta(days=random.randint(1, 30))
                    )
                    redemptions_created.append(redemption)
                    db.session.add(redemption)
            
            db.session.commit()
            
            print(f'Successfully created:')
            print(f'- {len(swaps_created)} clothing swaps')
            print(f'- {len(redemptions_created)} clothing redemptions')
            
            print('\nSample swaps created:')
            for swap in swaps_created[:5]:  # Show first 5
                user1 = User.query.get(swap.user1_id)
                user2 = User.query.get(swap.user2_id)
                item1 = Product.query.get(swap.item1_id)
                item2 = Product.query.get(swap.item2_id)
                print(f'  {user1.username} ({item1.name}) <-> {user2.username} ({item2.name})')
            
            print('\nSample redemptions created:')
            for redemption in redemptions_created[:5]:  # Show first 5
                user = User.query.get(redemption.user_id)
                product = Product.query.get(redemption.product_id)
                print(f'  {user.username}: {redemption.points_spent} points for {product.name}')
                
        except Exception as e:
            print(f'Error: {e}')
            db.session.rollback()

if __name__ == '__main__':
    update_to_clothing_data()
