from app import db  # type: ignore
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash  # type: ignore


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(30))
    gender = db.Column(db.String(20), default='Not Specified')
    skin_type = db.Column(db.String(50))
    detected_skin_type = db.Column(db.String(50))
    detected_hair_type = db.Column(db.String(50))
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    addresses = db.relationship('Address', backref='user', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='author', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    @property
    def full_name(self):
        # compatibility for templates expecting `full_name`
        return self.username

    def __repr__(self):
        return f'<User {self.email}>'


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    category = db.Column(db.String(80), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    skin_type = db.Column(db.String(80))
    hair_type = db.Column(db.String(80))
    image_url = db.Column(db.String(400))
    description = db.Column(db.Text)
    rating = db.Column(db.Float, default=4.5)
    stock_count = db.Column(db.Integer, default=50)
    target_condition = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reviews = db.relationship('Review', backref='product', lazy=True, cascade='all, delete-orphan')

    @property
    def image(self):
        # compatibility: return filename expected by templates/utility processor
        # store image_filename (not full path). If image_url contains folders, strip to filename.
        if not self.image_url:
            return 'default.jpg'
        # if stored as a full URL, return it directly
        if self.image_url.startswith('http'):
            return self.image_url
        return os.path.basename(self.image_url)

    def __repr__(self):
        return f'<Product {self.name}>'


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    line1 = db.Column(db.String(200), nullable=False)
    line2 = db.Column(db.String(200))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), default='India')
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Address {self.id} for user {self.user_id}>'


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(120), unique=True)
    method = db.Column(db.String(50))  # 'Online' or 'COD'
    status = db.Column(db.String(50), default='Pending')  # Pending/Success/Failed
    amount = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Payment {self.transaction_id} status={self.status}>'


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(80), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'), index=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'), index=True)
    total_price = db.Column(db.Float, nullable=False, default=0.0)
    shipping = db.Column(db.Float, default=0.0)
    payment_status = db.Column(db.String(50), default='Pending')
    status = db.Column(db.String(50), default='Pending')  # Order status: Pending/Shipped/Delivered
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    payment = db.relationship('Payment')
    address = db.relationship('Address')

    @property
    def total(self):
        return self.total_price

    def __repr__(self):
        return f'<Order {self.order_id} total={self.total_price}>'

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)

    product = db.relationship('Product')

    def __repr__(self):
        return f'<OrderItem {self.id} for order {self.order_id}>'


class Wishlist(db.Model):
    __tablename__ = 'wishlist'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('wishlist_items', lazy=True, cascade='all, delete-orphan'))
    product = db.relationship('Product')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'product_id', name='_user_product_uc'),
        {'extend_existing': True},
    )

    def __repr__(self):
        return f'<Wishlist user={self.user_id} product={self.product_id}>'

class Review(db.Model):
    __tablename__ = 'review'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False, default=5)
    comment_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Review user={self.user_id} product={self.product_id} rating={self.rating}>'
