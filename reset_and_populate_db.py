#!/usr/bin/env python3
"""
Complete database reset and population script for ReWear platform
Truncates all tables and adds fresh data with admin, products, users, swaps, and redemptions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PetPocket import create_app, db
from PetPocket.models import (
    User, PetType, Category, Product, ProductImage, ProductAttribute, 
    Review, CartItem, WishlistItem, Order, OrderItem, Address, 
    PageView, ProductView, SalesAnalytics, ProductAnalytics, 
    PromoCode, AdminAuditLog, SwapHistory, ItemReport, PointRedemption
)
from datetime import datetime, timedelta
import random

def truncate_all_tables():
    """Truncate all database tables"""
    print("🗑️ Truncating all database tables...")
    
    # Get all table names
    tables = [
        'point_redemptions',
        'item_reports', 
        'swap_history',
        'admin_audit_logs',
        'product_analytics',
        'sales_analytics',
        'product_views',
        'page_views',
        'addresses',
        'order_items',
        'orders',
        'wishlist_items',
        'cart_items',
        'reviews',
        'product_attributes',
        'product_images',
        'products',
        'categories',
        'pet_types',
        'promo_codes',
        'users'
    ]
    
    # Disable foreign key checks
    db.session.execute(db.text('PRAGMA foreign_keys=OFF'))
    
    # Truncate each table
    for table in tables:
        try:
            db.session.execute(db.text(f'DELETE FROM {table}'))
            db.session.execute(db.text(f'DELETE FROM sqlite_sequence WHERE name="{table}"'))
            print(f"✅ Truncated {table}")
        except Exception as e:
            print(f"⚠️ Could not truncate {table}: {e}")
    
    # Re-enable foreign key checks
    db.session.execute(db.text('PRAGMA foreign_keys=ON'))
    db.session.commit()
    print("✅ All tables truncated successfully!")

def create_admin_user():
    """Create admin user"""
    print("👑 Creating admin user...")
    
    admin = User(
        username='admin',
        email='admin@rewear.com',
        phone='+1234567890',
        is_admin=True,
        points_balance=1000,
        created_at=datetime.utcnow() - timedelta(days=30)
    )
    admin.password = 'admin123'
    
    db.session.add(admin)
    db.session.commit()
    print("✅ Admin user created: admin/admin123")
    return admin

def create_categories():
    """Create clothing categories"""
    print("👕 Creating clothing categories...")
    
    categories = [
        {
            'name': 'Tops & Shirts',
            'slug': 'tops-shirts',
            'description': 'T-shirts, shirts, blouses, and tank tops',
            'image_url': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400'
        },
        {
            'name': 'Dresses',
            'slug': 'dresses',
            'description': 'Casual, formal, and party dresses',
            'image_url': 'https://images.unsplash.com/photo-1566479179817-c6a4f5b8d0e6?w=400'
        },
        {
            'name': 'Pants & Jeans',
            'slug': 'pants-jeans',
            'description': 'Jeans, trousers, and casual pants',
            'image_url': 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=400'
        },
        {
            'name': 'Jackets & Coats',
            'slug': 'jackets-coats',
            'description': 'Outerwear, blazers, and coats',
            'image_url': 'https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=400'
        },
        {
            'name': 'Shoes',
            'slug': 'shoes',
            'description': 'Sneakers, boots, heels, and sandals',
            'image_url': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400'
        },
        {
            'name': 'Accessories',
            'slug': 'accessories',
            'description': 'Bags, jewelry, scarves, and belts',
            'image_url': 'https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=400'
        }
    ]
    
    created_categories = []
    for cat_data in categories:
        category = Category(**cat_data)
        db.session.add(category)
        created_categories.append(category)
    
    db.session.commit()
    print(f"✅ Created {len(categories)} clothing categories")
    return created_categories

def create_pet_types():
    """Create pet types (keeping for compatibility)"""
    print("🐾 Creating pet types (for compatibility)...")
    
    pet_types = [
        {'name': 'Fashion', 'image_url': 'https://images.unsplash.com/photo-1445205170230-053b83016050?w=400'},
        {'name': 'Casual', 'image_url': 'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=400'},
        {'name': 'Formal', 'image_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400'},
        {'name': 'Sports', 'image_url': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400'}
    ]
    
    created_pet_types = []
    for pet_data in pet_types:
        pet_type = PetType(**pet_data)
        db.session.add(pet_type)
        created_pet_types.append(pet_type)
    
    db.session.commit()
    print(f"✅ Created {len(pet_types)} style types")
    return created_pet_types

def create_products(categories, pet_types, admin):
    """Create 35-40 clothing products"""
    print("👗 Creating 35-40 clothing products...")
    
    products_data = [
        # Tops & Shirts
        {'name': 'Vintage Denim Jacket', 'price': 45.00, 'points': 25, 'category': 'Jackets & Coats', 'style': 'Casual', 'image': 'https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=400', 'description': 'Classic vintage denim jacket in excellent condition'},
        {'name': 'White Cotton T-Shirt', 'price': 12.00, 'points': 8, 'category': 'Tops & Shirts', 'style': 'Casual', 'image': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400', 'description': 'Basic white cotton t-shirt, soft and comfortable'},
        {'name': 'Silk Blouse', 'price': 35.00, 'points': 20, 'category': 'Tops & Shirts', 'style': 'Formal', 'image': 'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400', 'description': 'Elegant silk blouse perfect for office wear'},
        {'name': 'Striped Long Sleeve', 'price': 18.00, 'points': 12, 'category': 'Tops & Shirts', 'style': 'Casual', 'image': 'https://images.unsplash.com/photo-1571945153237-4929e783af4a?w=400', 'description': 'Classic striped long sleeve shirt'},
        {'name': 'Crop Top', 'price': 15.00, 'points': 10, 'category': 'Tops & Shirts', 'style': 'Fashion', 'image': 'https://images.unsplash.com/photo-1574180566232-aaad1b5b8450?w=400', 'description': 'Trendy crop top for casual outings'},
        
        # Dresses
        {'name': 'Floral Summer Dress', 'price': 28.00, 'points': 18, 'category': 'Dresses', 'style': 'Casual', 'image': 'https://images.unsplash.com/photo-1566479179817-c6a4f5b8d0e6?w=400', 'description': 'Beautiful floral summer dress, perfect for warm weather'},
        {'name': 'Little Black Dress', 'price': 50.00, 'points': 30, 'category': 'Dresses', 'style': 'Formal', 'image': 'https://images.unsplash.com/photo-1539008835657-9e8e9680c956?w=400', 'description': 'Timeless little black dress for any occasion'},
        {'name': 'Maxi Dress', 'price': 38.00, 'points': 22, 'category': 'Dresses', 'style': 'Fashion', 'image': 'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=400', 'description': 'Flowing maxi dress with beautiful print'},
        {'name': 'Cocktail Dress', 'price': 65.00, 'points': 35, 'category': 'Dresses', 'style': 'Formal', 'image': 'https://images.unsplash.com/photo-1583519923775-66d2e4ac7580?w=400', 'description': 'Elegant cocktail dress for special events'},
        {'name': 'Casual Sundress', 'price': 22.00, 'points': 15, 'category': 'Dresses', 'style': 'Casual', 'image': 'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=400', 'description': 'Light and breezy sundress'},
        
        # Pants & Jeans
        {'name': 'High-Waist Jeans', 'price': 32.00, 'points': 20, 'category': 'Pants & Jeans', 'style': 'Casual', 'image': 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=400', 'description': 'Trendy high-waist jeans in classic blue'},
        {'name': 'Black Skinny Jeans', 'price': 28.00, 'points': 18, 'category': 'Pants & Jeans', 'style': 'Fashion', 'image': 'https://images.unsplash.com/photo-1582418702059-97ebafb35d09?w=400', 'description': 'Sleek black skinny jeans'},
        {'name': 'Wide Leg Trousers', 'price': 40.00, 'points': 25, 'category': 'Pants & Jeans', 'style': 'Formal', 'image': 'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400', 'description': 'Professional wide leg trousers'},
        {'name': 'Yoga Leggings', 'price': 20.00, 'points': 12, 'category': 'Pants & Jeans', 'style': 'Sports', 'image': 'https://images.unsplash.com/photo-1506629905877-c52222d84b9f?w=400', 'description': 'Comfortable yoga leggings'},
        {'name': 'Cargo Pants', 'price': 35.00, 'points': 22, 'category': 'Pants & Jeans', 'style': 'Casual', 'image': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400', 'description': 'Utility cargo pants with multiple pockets'},
        
        # Jackets & Coats
        {'name': 'Leather Jacket', 'price': 85.00, 'points': 45, 'category': 'Jackets & Coats', 'style': 'Fashion', 'image': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400', 'description': 'Classic black leather jacket'},
        {'name': 'Wool Coat', 'price': 95.00, 'points': 50, 'category': 'Jackets & Coats', 'style': 'Formal', 'image': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400', 'description': 'Elegant wool coat for winter'},
        {'name': 'Bomber Jacket', 'price': 42.00, 'points': 25, 'category': 'Jackets & Coats', 'style': 'Casual', 'image': 'https://images.unsplash.com/photo-1562137369-1a1a0bc66744?w=400', 'description': 'Trendy bomber jacket'},
        {'name': 'Blazer', 'price': 55.00, 'points': 32, 'category': 'Jackets & Coats', 'style': 'Formal', 'image': 'https://images.unsplash.com/photo-1584464491033-06628f3a6b7b?w=400', 'description': 'Professional blazer for work'},
        {'name': 'Hoodie', 'price': 25.00, 'points': 15, 'category': 'Jackets & Coats', 'style': 'Casual', 'image': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400', 'description': 'Comfortable cotton hoodie'},
        
        # Shoes
        {'name': 'White Sneakers', 'price': 60.00, 'points': 35, 'category': 'Shoes', 'style': 'Casual', 'image': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400', 'description': 'Classic white leather sneakers'},
        {'name': 'Black Heels', 'price': 45.00, 'points': 28, 'category': 'Shoes', 'style': 'Formal', 'image': 'https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=400', 'description': 'Elegant black high heels'},
        {'name': 'Ankle Boots', 'price': 70.00, 'points': 40, 'category': 'Shoes', 'style': 'Fashion', 'image': 'https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=400', 'description': 'Stylish ankle boots'},
        {'name': 'Running Shoes', 'price': 80.00, 'points': 45, 'category': 'Shoes', 'style': 'Sports', 'image': 'https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=400', 'description': 'Performance running shoes'},
        {'name': 'Sandals', 'price': 25.00, 'points': 15, 'category': 'Shoes', 'style': 'Casual', 'image': 'https://images.unsplash.com/photo-1603487742131-4160ec999306?w=400', 'description': 'Comfortable summer sandals'},
        
        # Accessories
        {'name': 'Leather Handbag', 'price': 75.00, 'points': 42, 'category': 'Accessories', 'style': 'Fashion', 'image': 'https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=400', 'description': 'Premium leather handbag'},
        {'name': 'Silk Scarf', 'price': 20.00, 'points': 12, 'category': 'Accessories', 'style': 'Fashion', 'image': 'https://images.unsplash.com/photo-1601924994987-69e26d50dc26?w=400', 'description': 'Elegant silk scarf with pattern'},
        {'name': 'Gold Necklace', 'price': 150.00, 'points': 80, 'category': 'Accessories', 'style': 'Formal', 'image': 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=400', 'description': 'Delicate gold chain necklace'},
        {'name': 'Baseball Cap', 'price': 15.00, 'points': 8, 'category': 'Accessories', 'style': 'Casual', 'image': 'https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=400', 'description': 'Classic baseball cap'},
        {'name': 'Watch', 'price': 120.00, 'points': 65, 'category': 'Accessories', 'style': 'Formal', 'image': 'https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=400', 'description': 'Stylish wrist watch'},
        
        # Additional items to reach 35-40
        {'name': 'Cardigan', 'price': 32.00, 'points': 20, 'category': 'Tops & Shirts', 'style': 'Casual', 'image': 'https://images.unsplash.com/photo-1571945153237-4929e783af4a?w=400', 'description': 'Cozy knit cardigan'},
        {'name': 'Sports Bra', 'price': 18.00, 'points': 10, 'category': 'Tops & Shirts', 'style': 'Sports', 'image': 'https://images.unsplash.com/photo-1506629905877-c52222d84b9f?w=400', 'description': 'Supportive sports bra'},
        {'name': 'Denim Skirt', 'price': 25.00, 'points': 15, 'category': 'Dresses', 'style': 'Casual', 'image': 'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400', 'description': 'Classic denim mini skirt'},
        {'name': 'Palazzo Pants', 'price': 30.00, 'points': 18, 'category': 'Pants & Jeans', 'style': 'Fashion', 'image': 'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400', 'description': 'Flowy palazzo pants'},
        {'name': 'Puffer Jacket', 'price': 65.00, 'points': 38, 'category': 'Jackets & Coats', 'style': 'Casual', 'image': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400', 'description': 'Warm puffer jacket for winter'},
        {'name': 'Ballet Flats', 'price': 35.00, 'points': 20, 'category': 'Shoes', 'style': 'Casual', 'image': 'https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=400', 'description': 'Comfortable ballet flats'},
        {'name': 'Belt', 'price': 12.00, 'points': 8, 'category': 'Accessories', 'style': 'Fashion', 'image': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400', 'description': 'Stylish leather belt'},
        {'name': 'Sunglasses', 'price': 40.00, 'points': 25, 'category': 'Accessories', 'style': 'Fashion', 'image': 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=400', 'description': 'Designer sunglasses'},
        {'name': 'Crossbody Bag', 'price': 45.00, 'points': 28, 'category': 'Accessories', 'style': 'Casual', 'image': 'https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=400', 'description': 'Convenient crossbody bag'},
        {'name': 'Evening Gown', 'price': 120.00, 'points': 70, 'category': 'Dresses', 'style': 'Formal', 'image': 'https://images.unsplash.com/photo-1583519923775-66d2e4ac7580?w=400', 'description': 'Stunning evening gown for special occasions'}
    ]
    
    created_products = []
    
    # Create category and pet_type lookup dictionaries
    cat_dict = {cat.name: cat for cat in categories}
    pet_dict = {pt.name: pt for pt in pet_types}
    
    for product_data in products_data:
        category = cat_dict.get(product_data['category'])
        pet_type = pet_dict.get(product_data['style'])
        
        if category and pet_type:
            product = Product(
                name=product_data['name'],
                description=product_data['description'],
                price=product_data['price'],
                points_required=product_data['points'],
                stock=random.randint(1, 10),
                image_url=product_data['image'],
                category_id=category.id,
                pet_type_id=pet_type.id,
                uploader_id=admin.id,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            db.session.add(product)
            created_products.append(product)
    
    db.session.commit()
    print(f"✅ Created {len(created_products)} clothing products")
    return created_products

def create_users():
    """Create 3-4 regular users"""
    print("👥 Creating regular users...")
    
    users_data = [
        {
            'username': 'fashion_lover',
            'email': 'fashion@example.com',
            'phone': '+1234567891',
            'points': 150
        },
        {
            'username': 'style_guru',
            'email': 'style@example.com', 
            'phone': '+1234567892',
            'points': 200
        },
        {
            'username': 'trendy_user',
            'email': 'trendy@example.com',
            'phone': '+1234567893',
            'points': 120
        },
        {
            'username': 'casual_shopper',
            'email': 'casual@example.com',
            'phone': '+1234567894',
            'points': 80
        }
    ]
    
    created_users = []
    for user_data in users_data:
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            phone=user_data['phone'],
            points_balance=user_data['points'],
            created_at=datetime.utcnow() - timedelta(days=random.randint(5, 25))
        )
        user.password = 'password123'
        db.session.add(user)
        created_users.append(user)
    
    db.session.commit()
    print(f"✅ Created {len(created_users)} regular users")
    return created_users

def create_swaps(users, products):
    """Create swap history between users"""
    print("🔄 Creating swap history...")
    
    swap_count = 0
    
    # Create swaps between different users
    for i in range(6):  # Create 6 swaps
        user1 = random.choice(users)
        user2 = random.choice([u for u in users if u != user1])
        item1 = random.choice(products)
        item2 = random.choice([p for p in products if p != item1])
        
        swap = SwapHistory(
            user1_id=user1.id,
            user2_id=user2.id,
            item1_id=item1.id,
            item2_id=item2.id,
            completed_at=datetime.utcnow() - timedelta(days=random.randint(1, 20))
        )
        
        db.session.add(swap)
        swap_count += 1
    
    db.session.commit()
    print(f"✅ Created {swap_count} swap transactions")
    return swap_count

def create_redemptions(users, products):
    """Create point redemptions for users"""
    print("⭐ Creating point redemptions...")
    
    redemption_count = 0
    
    # Create redemptions for each user
    for user in users:
        num_redemptions = random.randint(2, 4)
        
        for _ in range(num_redemptions):
            product = random.choice(products)
            
            # Only create redemption if user has enough points
            if user.points_balance >= product.points_required:
                redemption = PointRedemption(
                    user_id=user.id,
                    product_id=product.id,
                    points_spent=product.points_required,
                    redeemed_at=datetime.utcnow() - timedelta(days=random.randint(1, 15))
                )
                
                # Deduct points from user
                user.points_balance -= product.points_required
                
                db.session.add(redemption)
                redemption_count += 1
    
    db.session.commit()
    print(f"✅ Created {redemption_count} point redemptions")
    return redemption_count

def create_orders_and_reviews(users, products):
    """Create some orders and reviews"""
    print("🛒 Creating orders and reviews...")
    
    order_count = 0
    review_count = 0
    
    for user in users:
        num_orders = random.randint(1, 3)
        
        for _ in range(num_orders):
            # Create order
            order = Order(
                user_id=user.id,
                total_price=random.uniform(20, 150),
                payment_status='completed',
                timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            db.session.add(order)
            db.session.flush()  # Get the order ID
            
            # Add order items
            num_items = random.randint(1, 3)
            for _ in range(num_items):
                product = random.choice(products)
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=random.randint(1, 2),
                    price_at_purchase=product.price
                )
                db.session.add(order_item)
                
                # Sometimes add a review
                if random.random() < 0.6:  # 60% chance of review
                    review = Review(
                        product_id=product.id,
                        user_id=user.id,
                        rating=random.randint(3, 5),
                        content=random.choice([
                            "Great quality clothing item!",
                            "Exactly as described, very happy with purchase.",
                            "Good condition and fast delivery.",
                            "Love this piece, perfect fit!",
                            "Excellent value for money."
                        ]),
                        created_at=datetime.utcnow() - timedelta(days=random.randint(1, 25))
                    )
                    db.session.add(review)
                    review_count += 1
            
            order_count += 1
    
    db.session.commit()
    print(f"✅ Created {order_count} orders and {review_count} reviews")
    return order_count, review_count

def main():
    """Main function to reset and populate database"""
    print("🚀 Starting ReWear database reset and population...")
    
    app = create_app()
    
    with app.app_context():
        # Step 1: Truncate all tables
        truncate_all_tables()
        
        # Step 2: Create admin user
        admin = create_admin_user()
        
        # Step 3: Create categories and pet types
        categories = create_categories()
        pet_types = create_pet_types()
        
        # Step 4: Create products
        products = create_products(categories, pet_types, admin)
        
        # Step 5: Create regular users
        users = create_users()
        
        # Step 6: Create swaps
        create_swaps(users, products)
        
        # Step 7: Create redemptions
        create_redemptions(users, products)
        
        # Step 8: Create orders and reviews
        create_orders_and_reviews(users, products)
        
        print("\n🎉 Database reset and population completed successfully!")
        print("\n📊 Summary:")
        print(f"   👑 Admin user: admin (password: admin123)")
        print(f"   👥 Regular users: {len(users)}")
        print(f"   📦 Categories: {len(categories)}")
        print(f"   👕 Products: {len(products)}")
        print(f"   🔄 Swaps: Available in profile")
        print(f"   ⭐ Point redemptions: Available in profile")
        print(f"   📝 Orders and reviews: Created")
        print("\n🌐 You can now test the ReWear platform with realistic data!")
        print("   Login with any user (password: password123) or admin (password: admin123)")

if __name__ == '__main__':
    main()
