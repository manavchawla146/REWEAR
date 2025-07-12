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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(datetime.timezone.utc))
    
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    profile_picture = db.Column(db.String(200), nullable=True)
    
    cart_items = db.relationship('CartItem', backref='user', lazy=True)
    wishlist_items = db.relationship('WishlistItem', backref='user', lazy=True)
    uploaded_products = db.relationship('Product', backref='uploader', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='reviewer', lazy=True)
    points_balance = db.Column(db.Integer, default=0)

    
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
    
def add_points(self, amount, reason=None):
    self.points_balance += amount
    log = AdminAuditLog(
        admin_id=self.id if self.is_admin else None,
        action='add_points',
        target_type='user',
        target_id=self.id,
        message=reason or f'Added {amount} points'
    )
    db.session.add(log)
    db.session.commit()

def deduct_points(self, amount, reason=None):
    if self.points_balance >= amount:
        self.points_balance -= amount
        log = AdminAuditLog(
            admin_id=self.id if self.is_admin else None,
            action='deduct_points',
            target_type='user',
            target_id=self.id,
            message=reason or f'Deducted {amount} points'
        )
        db.session.add(log)
        db.session.commit()
        return True
    return False


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
    points_required = db.Column(db.Integer, default=10)  # Default cost in points


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
            return False, f"Order value must be at least <img src='/static/images/coin.png' class='coin-icon'>{self.min_order_value} to use this promo code"
        return True, "Promo code is valid"
    
    def apply_discount(self, subtotal):
        if self.discount_type == 'percentage':
            discount = subtotal * (self.discount_value / 100)
        else:
            discount = self.discount_value
        return max(0, discount)
    
# Enhancement 1: Admin Audit Logs
class AdminAuditLog(db.Model):
    __tablename__ = 'admin_audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # e.g., 'approve_item', 'reject_item'
    target_type = db.Column(db.String(50), nullable=False)  # e.g., 'product', 'user', 'report'
    target_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    admin = db.relationship('User', backref='admin_logs')

    def __repr__(self):
        return f'<AdminAuditLog {self.action} on {self.target_type}:{self.target_id}>'


# Enhancement 2: Swap History
class SwapHistory(db.Model):
    __tablename__ = 'swap_history'
    id = db.Column(db.Integer, primary_key=True)
    item1_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    item2_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    item1 = db.relationship('Product', foreign_keys=[item1_id], backref='swaps_as_item1')
    item2 = db.relationship('Product', foreign_keys=[item2_id], backref='swaps_as_item2')
    user1 = db.relationship('User', foreign_keys=[user1_id], backref='swaps_as_user1')
    user2 = db.relationship('User', foreign_keys=[user2_id], backref='swaps_as_user2')

    def __repr__(self):
        return f'<SwapHistory {self.item1_id} <--> {self.item2_id}>'


# Enhancement 3: Item Reports
class ItemReport(db.Model):
    __tablename__ = 'item_reports'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    reported_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, reviewed, dismissed, action_taken
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    item = db.relationship('Product', backref='reports')
    reporter = db.relationship('User', foreign_keys=[reported_by], backref='submitted_reports')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by], backref='reviewed_reports')

    def __repr__(self):
        return f'<ItemReport item={self.item_id} by user={self.reported_by}>'
    
class PointRedemption(db.Model):
    __tablename__ = 'point_redemptions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    points_spent = db.Column(db.Integer, nullable=False)
    redeemed_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='point_redemptions')
    product = db.relationship('Product', backref='point_redemptions')

    def __repr__(self):
        return f'<PointRedemption user={self.user_id} item={self.product_id} points={self.points_spent}>'

