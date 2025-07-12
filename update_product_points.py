#!/usr/bin/env python3
"""
Script to update existing products with points_required values.
This script sets point values based on product prices using a formula.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PetPocket import create_app, db
from PetPocket.models import Product

def update_product_points():
    """Update existing products with points_required values."""
    app = create_app()
    
    with app.app_context():
        try:
            # Get all products that don't have points_required set (or are None/0)
            products = Product.query.filter(
                (Product.points_required == None) | (Product.points_required == 0)
            ).all()
            
            print(f"Found {len(products)} products to update")
            
            updated_count = 0
            for product in products:
                # Calculate points based on price
                # Formula: 1 point per ₹10, minimum 5 points, maximum 100 points
                if product.price > 0:
                    points = max(5, min(100, int(product.price / 10)))
                else:
                    points = 10  # Default for products with no price
                
                product.points_required = points
                updated_count += 1
                
                print(f"Updated '{product.name}' (₹{product.price}) -> {points} points")
            
            # Commit all changes
            db.session.commit()
            print(f"\n✅ Successfully updated {updated_count} products with point values!")
            
            # Show summary of point distribution
            print("\n📊 Point Distribution Summary:")
            point_ranges = [
                (1, 10, "Budget items"),
                (11, 25, "Mid-range items"), 
                (26, 50, "Premium items"),
                (51, 100, "Luxury items")
            ]
            
            for min_points, max_points, category in point_ranges:
                count = Product.query.filter(
                    Product.points_required >= min_points,
                    Product.points_required <= max_points
                ).count()
                print(f"  {category} ({min_points}-{max_points} points): {count} products")
                
        except Exception as e:
            print(f"❌ Error updating products: {e}")
            db.session.rollback()
            return False
            
    return True

if __name__ == "__main__":
    print("🚀 Starting product points update...")
    success = update_product_points()
    
    if success:
        print("\n🎉 Product points update completed successfully!")
    else:
        print("\n💥 Product points update failed!")
        sys.exit(1)
