from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='user', lazy=True)

class Expert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    avatar = db.Column(db.String(10), default='👨‍🎓')
    specialization = db.Column(db.String(300))
    experience = db.Column(db.Integer, default=3)
    rating = db.Column(db.Float, default=4.9)
    orders_done = db.Column(db.Integer, default=120)
    bio = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    expert_id = db.Column(db.Integer, db.ForeignKey('expert.id'), nullable=True)
    work_type = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    specialty = db.Column(db.String(200))
    topic = db.Column(db.String(500), nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    deadline = db.Column(db.String(50), nullable=False)
    antiplagiat = db.Column(db.Integer, default=70)
    requirements = db.Column(db.Text)
    status = db.Column(db.String(50), default='Новая')
    price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('Message', backref='order', lazy=True)
    expert = db.relationship('Expert', backref='orders', foreign_keys=[expert_id])

    STATUS_COLORS = {
        'Новая': '#3B82F6',
        'В работе': '#F59E0B',
        'На проверке': '#8B5CF6',
        'Выполнена': '#10B981',
        'Отменена': '#EF4444',
    }

    @property
    def status_color(self):
        return self.STATUS_COLORS.get(self.status, '#6B7280')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    sender = db.Column(db.String(50), nullable=False)  # 'user' or 'expert'
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(300), unique=True, nullable=False)
    excerpt = db.Column(db.String(500))
    content = db.Column(db.Text)
    emoji = db.Column(db.String(10), default='📝')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
