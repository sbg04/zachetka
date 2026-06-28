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
    role = db.Column(db.String(20), default='student')  # student / executor / admin
    avatar = db.Column(db.String(10), default='🎓')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='user', lazy=True, foreign_keys='Order.user_id')
    messages = db.relationship('Message', backref='author', lazy=True)

class ExecutorProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='executor_profile')
    bio = db.Column(db.Text)
    specializations = db.Column(db.String(500))
    experience_years = db.Column(db.Integer, default=1)
    completed_orders = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=5.0)
    avatar_emoji = db.Column(db.String(10), default='👨‍🏫')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    work_type = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    specialty = db.Column(db.String(200))
    topic = db.Column(db.String(500), nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    deadline = db.Column(db.String(50), nullable=False)
    uniqueness = db.Column(db.String(50))
    requirements = db.Column(db.Text)
    status = db.Column(db.String(50), default='Новая')
    price = db.Column(db.Float)
    paid = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('Message', backref='order', lazy=True)

    STATUS_MAP = {
        'Новая':       ('#3B82F6', '🆕'),
        'В работе':    ('#F59E0B', '⚙️'),
        'На проверке': ('#8B5CF6', '🔍'),
        'Правки':      ('#EF4444', '✏️'),
        'Выполнена':   ('#10B981', '✅'),
        'Отменена':    ('#6B7280', '❌'),
    }

    @property
    def status_color(self):
        return self.STATUS_MAP.get(self.status, ('#6B7280', ''))[0]

    @property
    def status_icon(self):
        return self.STATUS_MAP.get(self.status, ('#6B7280', ''))[1]

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
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
