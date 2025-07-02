from . import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=True, default=None)
    password_hash = db.Column(db.String(128), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    profile_picture = db.Column(db.String(200), nullable=True)
    
    cart_items = db.relationship('CartItem', backref='user', lazy=True)
    wishlist_items = db.relationship('WishlistItem', backref='user', lazy=True)
    uploaded_products = db.relationship('Product', backref='uploader', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='reviewer', lazy=True)
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
        
    @password.setter
    def password(self, password):
        if password:
            self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class PetType(db.Model):
    __tablename__ = 'pet_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    image_url = db.Column(db.String(200)) 
    products = db.relationship('Product', backref='pet_type', lazy=True)

    def __str__(self):
        return self.name

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    image_url = db.Column(db.String(200))
    description = db.Column(db.Text)
    products = db.relationship('Product', backref='category', lazy=True)
    
    def __str__(self):
        return self.name

    def __repr__(self):
        return f'<Category {self.name}>'

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    weight = db.Column(db.Float, nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('products.id', name='fk_product_parent'), nullable=True)
    parent = db.relationship('Product', remote_side=[id], backref='variants')

    pet_type_id = db.Column(db.Integer, db.ForeignKey('pet_types.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    additional_images = db.relationship('ProductImage', backref='product', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='product', lazy=True, cascade='all, delete-orphan')
    attributes = db.relationship('ProductAttribute', backref='product', lazy=True, cascade='all, delete-orphan')
    analytics = db.relationship('ProductAnalytics', backref='product', lazy=True, cascade='all, delete-orphan')
    views = db.relationship('ProductView', backref='product', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Product {self.name}>'

class ProductImage(db.Model):
    __tablename__ = 'product_images'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)

class ProductAttribute(db.Model):
    __tablename__ = 'product_attributes'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(200), nullable=False)
    display_order = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<ProductAttribute {self.key}: {self.value}>'

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Review {self.id} by User {self.user_id} for Product {self.product_id}>'

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product = db.relationship('Product')

class WishlistItem(db.Model):
    __tablename__ = 'wishlist_items'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product = db.relationship('Product')

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    total_price = db.Column(db.Float, nullable=False)
    payment_id = db.Column(db.String(100))
    order_id = db.Column(db.String(100))
    payment_status = db.Column(db.String(20), default='pending')
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False)
    product = db.relationship('Product')

class Address(db.Model):
    __tablename__ = 'addresses'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    address_type = db.Column(db.String(20), nullable=False)
    company_name = db.Column(db.String(128))
    street_address = db.Column(db.String(256), nullable=False)
    apartment = db.Column(db.String(128))
    city = db.Column(db.String(64), nullable=False)
    state = db.Column(db.String(64), nullable=False)
    country = db.Column(db.String(64), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    user = db.relationship('User', backref='addresses')

class PageView(db.Model):
    __tablename__ = 'page_views'
    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(128), nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user_agent = db.Column(db.String(256), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='page_views')
    
    def __repr__(self):
        return f'<PageView {self.page}>'

class ProductView(db.Model):
    __tablename__ = 'product_views'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', name='fk_product_view_product_id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='product_views')

class SalesAnalytics(db.Model):
    __tablename__ = 'sales_analytics'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    total_sales = db.Column(db.Float, default=0)
    order_count = db.Column(db.Integer, default=0)
    avg_order_value = db.Column(db.Float, default=0)
    
    @classmethod
    def update_daily_stats(cls, date):
        from .models import Order
        orders = Order.query.filter(
            db.func.date(Order.timestamp) == date,
            Order.payment_status == 'completed'
        ).all()
        order_count = len(orders)
        total_sales = sum(order.total_price for order in orders)
        avg_order_value = total_sales / order_count if order_count > 0 else 0
        record = cls.query.filter_by(date=date).first()
        if record:
            record.total_sales = total_sales
            record.order_count = order_count
            record.avg_order_value = avg_order_value
        else:
            record = cls(
                date=date,
                total_sales=total_sales,
                order_count=order_count,
                avg_order_value=avg_order_value
            )
            db.session.add(record)
        db.session.commit()
        return record

class ProductAnalytics(db.Model):
    __tablename__ = 'product_analytics'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', name='fk_product_analytics_product_id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    view_count = db.Column(db.Integer, default=0)
    cart_add_count = db.Column(db.Integer, default=0)
    purchase_count = db.Column(db.Integer, default=0)

    @classmethod
    def increment_view(cls, product_id, date=None):
        if date is None:
            date = datetime.utcnow().date()
        record = cls.query.filter_by(product_id=product_id, date=date).first()
        if not record:
            record = cls(product_id=product_id, date=date, view_count=1)
            db.session.add(record)
        else:
            record.view_count += 1
        db.session.commit()
        return record
    
    @classmethod
    def increment_cart_add(cls, product_id, date=None):
        if date is None:
            date = datetime.utcnow().date()
        record = cls.query.filter_by(product_id=product_id, date=date).first()
        if not record:
            record = cls(product_id=product_id, date=date, cart_add_count=1)
            db.session.add(record)
        else:
            record.cart_add_count += 1
        db.session.commit()
        return record
    
    @classmethod
    def increment_purchase(cls, product_id, quantity=1, date=None):
        if date is None:
            date = datetime.utcnow().date()
        record = cls.query.filter_by(product_id=product_id, date=date).first()
        if not record:
            record = cls(product_id=product_id, date=date, purchase_count=quantity)
            db.session.add(record)
        else:
            record.purchase_count += quantity
        db.session.commit()
        return record

class PromoCode(db.Model):
    __tablename__ = 'promo_codes'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    discount_type = db.Column(db.String(20), nullable=False)
    discount_value = db.Column(db.Float, nullable=False)
    valid_from = db.Column(db.DateTime, nullable=False)
    valid_until = db.Column(db.DateTime, nullable=False)
    max_uses = db.Column(db.Integer, nullable=True)
    uses = db.Column(db.Integer, default=0)
    min_order_value = db.Column(db.Float, nullable=True)
    active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<PromoCode {self.code}>'
    
    def is_valid(self, order_value):
        now = datetime.now()
        if not self.active:
            return False, "Promo code is not active"
        if now < self.valid_from or now > self.valid_until:
            return False, "Promo code has expired"
        if self.max_uses is not None and self.uses >= self.max_uses:
            return False, "Promo code usage limit reached"
        if self.min_order_value is not None and order_value < self.min_order_value:
            return False, f"Order value must be at least ₹{self.min_order_value} to use this promo code"
        return True, "Promo code is valid"
    
    def apply_discount(self, subtotal):
        if self.discount_type == 'percentage':
            discount = subtotal * (self.discount_value / 100)
        else:
            discount = self.discount_value
        return max(0, discount)