#!/usr/bin/env python3
"""
Add clothing products for ReWear platform
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from PetPocket import create_app, db
from PetPocket.models import Product, Category, PetType
from datetime import datetime

def add_clothing_products():
    app = create_app()
    with app.app_context():
        try:
            # Get or create clothing categories
            categories = Category.query.all()
            if not categories:
                print('No categories found, creating clothing categories...')
                clothing_categories = [
                    {'name': 'Tops', 'slug': 'tops', 'description': 'T-shirts, shirts, blouses, sweaters'},
                    {'name': 'Bottoms', 'slug': 'bottoms', 'description': 'Jeans, pants, shorts, skirts'},
                    {'name': 'Dresses', 'slug': 'dresses', 'description': 'Casual and formal dresses'},
                    {'name': 'Outerwear', 'slug': 'outerwear', 'description': 'Jackets, coats, hoodies'},
                    {'name': 'Accessories', 'slug': 'accessories', 'description': 'Bags, scarves, jewelry'},
                ]
                
                for cat_data in clothing_categories:
                    category = Category(**cat_data)
                    db.session.add(category)
                
                db.session.commit()
                categories = Category.query.all()
            
            # Get or create general pet type (we'll repurpose this for clothing sizes)
            pet_type = PetType.query.first()
            if not pet_type:
                pet_type = PetType(name="General", image_url="")
                db.session.add(pet_type)
                db.session.commit()
            
            # Create clothing products
            clothing_products = [
                {
                    'name': 'Vintage Denim Jacket',
                    'description': 'Classic blue denim jacket, size M, excellent condition. Timeless style perfect for any casual outfit.',
                    'price': 0,
                    'stock': 1,
                    'points_required': 25,
                    'image_url': 'https://images.unsplash.com/photo-1551163943-3f6a855d1153?w=400',
                    'category': 'outerwear'
                },
                {
                    'name': 'Black Leather Boots',
                    'description': 'Genuine leather ankle boots, size 8, minimal wear. Perfect for both casual and semi-formal occasions.',
                    'price': 0,
                    'stock': 1,
                    'points_required': 30,
                    'image_url': 'https://images.unsplash.com/photo-1544966503-7cc5ac882d5a?w=400',
                    'category': 'accessories'
                },
                {
                    'name': 'Floral Summer Dress',
                    'description': 'Light and airy floral dress, size S, perfect for summer days. Barely worn, like new condition.',
                    'price': 0,
                    'stock': 1,
                    'points_required': 20,
                    'image_url': 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400',
                    'category': 'dresses'
                },
                {
                    'name': 'Designer Blue Jeans',
                    'description': 'Premium designer jeans, size 32, dark wash. Excellent quality denim in great condition.',
                    'price': 0,
                    'stock': 1,
                    'points_required': 35,
                    'image_url': 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=400',
                    'category': 'bottoms'
                },
                {
                    'name': 'Cashmere Sweater',
                    'description': 'Soft cashmere sweater in cream, size L. Luxurious feel and perfect for cooler weather.',
                    'price': 0,
                    'stock': 1,
                    'points_required': 40,
                    'image_url': 'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=400',
                    'category': 'tops'
                },
                {
                    'name': 'Silk Scarf',
                    'description': 'Beautiful silk scarf with abstract pattern. Perfect accessory to elevate any outfit.',
                    'price': 0,
                    'stock': 1,
                    'points_required': 15,
                    'image_url': 'https://images.unsplash.com/photo-1581338834647-b0fb40704e21?w=400',
                    'category': 'accessories'
                },
                {
                    'name': 'White Button-Up Shirt',
                    'description': 'Classic white cotton shirt, size M. Crisp and clean, perfect for professional or casual wear.',
                    'price': 0,
                    'stock': 1,
                    'points_required': 18,
                    'image_url': 'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=400',
                    'category': 'tops'
                },
                {
                    'name': 'Leather Handbag',
                    'description': 'Genuine leather handbag in brown, excellent condition. Spacious and stylish with multiple compartments.',
                    'price': 0,
                    'stock': 1,
                    'points_required': 45,
                    'image_url': 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400',
                    'category': 'accessories'
                }
            ]
            
            # Check if clothing products already exist
            existing_products = Product.query.filter(Product.name.in_([p['name'] for p in clothing_products])).all()
            if existing_products:
                print(f'Found {len(existing_products)} existing clothing products, skipping creation')
                return
            
            products_created = []
            for product_data in clothing_products:
                # Find category
                category = Category.query.filter_by(slug=product_data['category']).first()
                if not category:
                    category = categories[0]  # Use first available category
                
                product = Product(
                    name=product_data['name'],
                    description=product_data['description'],
                    price=product_data['price'],
                    stock=product_data['stock'],
                    points_required=product_data['points_required'],
                    image_url=product_data['image_url'],
                    pet_type_id=pet_type.id,
                    category_id=category.id,
                    uploader_id=1  # Admin user
                )
                products_created.append(product)
                db.session.add(product)
            
            db.session.commit()
            print(f'Successfully created {len(products_created)} clothing products for ReWear:')
            for product in products_created:
                print(f'  - {product.name} ({product.points_required} points)')
                
        except Exception as e:
            print(f'Error: {e}')
            db.session.rollback()

if __name__ == '__main__':
    add_clothing_products()
