#!/usr/bin/env python3
"""
Add sample swap history for testing
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from PetPocket import create_app, db
from PetPocket.models import SwapHistory, User, Product
from datetime import datetime, timedelta
import random

def add_sample_swaps():
    app = create_app()
    with app.app_context():
        try:
            users = User.query.all()
            products = Product.query.all()
            
            print(f'Found {len(users)} users and {len(products)} products')
            
            if len(users) < 2 or not products:
                print('Need at least 2 users and some products for swaps')
                return
            
            # Check if swaps already exist
            existing_swaps = SwapHistory.query.count()
            if existing_swaps > 0:
                print(f'Found {existing_swaps} existing swaps, skipping creation')
                return
            
            # Create some sample swaps
            sample_swaps = []
            
            for i in range(3):  # Create 3 swaps
                # Select two different users
                user1 = random.choice(users)
                user2 = random.choice([u for u in users if u.id != user1.id])
                
                # Select two different products
                item1 = random.choice(products)
                item2 = random.choice([p for p in products if p.id != item1.id])
                
                swap = SwapHistory(
                    user1_id=user1.id,
                    user2_id=user2.id,
                    item1_id=item1.id,
                    item2_id=item2.id,
                    completed_at=datetime.now() - timedelta(days=random.randint(1, 60))
                )
                sample_swaps.append(swap)
                db.session.add(swap)
            
            db.session.commit()
            print(f'Created {len(sample_swaps)} sample swaps')
            
            # Show the swaps
            for swap in sample_swaps:
                print(f'Swap: {swap.user1.username} ({swap.item1.name}) <-> {swap.user2.username} ({swap.item2.name})')
                
        except Exception as e:
            print(f'Error: {e}')
            db.session.rollback()

if __name__ == '__main__':
    add_sample_swaps()
