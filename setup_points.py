#!/usr/bin/env python3
"""
Script to give initial points to users and show current status.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PetPocket import create_app, db
from PetPocket.models import User, Product

def setup_initial_points():
    """Give initial points to users and show status."""
    app = create_app()
    
    with app.app_context():
        try:
            # Show current users
            users = User.query.all()
            print(f"Found {len(users)} users in the system")
            
            # Give initial points to users who have 0 points
            updated_users = 0
            for user in users:
                if user.points_balance == 0:
                    user.points_balance = 50  # Give 50 initial points
                    updated_users += 1
                    print(f"Gave 50 points to user: {user.username}")
            
            db.session.commit()
            print(f"\n✅ Updated {updated_users} users with initial points")
            
            # Show user point balances
            print("\n👥 User Point Balances:")
            for user in User.query.all():
                print(f"  {user.username}: {user.points_balance} points")
            
            # Show product point costs
            products = Product.query.limit(10).all()
            print(f"\n🛍️ Sample Product Point Costs (first 10):")
            for product in products:
                print(f"  {product.name[:30]:<30} | <img src='/static/images/coin.png' class='coin-icon'>{product.price:<6} | {product.points_required} points")
            
            # Show total stats
            total_products = Product.query.count()
            avg_points = db.session.query(db.func.avg(Product.points_required)).scalar()
            print(f"\n📊 ReWear Platform Stats:")
            print(f"  Total Products: {total_products}")
            print(f"  Average Point Cost: {avg_points:.1f} points")
            print(f"  Total Users: {len(users)}")
            print(f"  Total User Points: {sum(u.points_balance for u in users)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting up points: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("🎯 Setting up initial points for ReWear platform...")
    success = setup_initial_points()
    
    if success:
        print("\n🎉 Points setup completed successfully!")
        print("\n💡 Users can now:")
        print("  • Earn points by uploading clothing items")
        print("  • Spend points to redeem clothing from others")
        print("  • Participate in clothing swaps")
    else:
        print("\n💥 Points setup failed!")
        sys.exit(1)
