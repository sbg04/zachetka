from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Order, Message, BlogPost, ExecutorProfile
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'zachetka-super-secret-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///zachetka.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Войдите в аккаунт, чтобы продолжить'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

WORK_TYPES = [
    'Дипломная работа (ВКР)', 'Курсовая работа', 'Реферат', 'Эссе',
    'Контрольная работа', 'Лабораторная работа', 'Решение задач',
    'Тест / Онлайн-экзамен', 'Отчёт по практике', 'Бизнес-план',
    'Презентация', 'Статья / Научная работа', 'Чертёж / Проект',
    'Консультация по диплому', 'Редактура и оформление по ГОСТу',
]

PRICE_BASE = {
    'Дипломная работа (ВКР)': 150, 'Курсовая работа': 80,
    'Реферат': 40, 'Эссе': 40, 'Контрольная работа': 40,
    'Лабораторная работа': 60, 'Решение задач': 50,
    'Тест / Онлайн-экзамен': 45, 'Отчёт по практике': 70,
    'Бизнес-план': 90, 'Презентация': 55,
    'Статья / Научная работа': 100, 'Чертёж / Проект': 80,
    'Консультация по диплому': 200, 'Редактура и оформление по ГОСТу': 30,
}

def seed_data():
    if User.query.count() == 0:
        # Demo executors
        executors_data = [
            ('Анна Соколова', 'anna@zachetka.ru', '👩‍🏫', 'Экономика, Менеджмент, Маркетинг', 8, 342, 4.9),
            ('Дмитрий Орлов', 'dmitry@zachetka.ru', '👨‍💻', 'Программирование, Математика, Физика', 6, 218, 4.8),
            ('Елена Петрова', 'elena@zachetka.ru', '👩‍⚖️', 'Право, Юриспруденция, Политология', 10, 487, 5.0),
            ('Михаил Власов', 'mikhail@zachetka.ru', '👨‍🔬', 'Химия, Биология, Медицина', 5, 156, 4.7),
        ]
        for name, email, emoji, specs, exp, completed, rating in executors_data:
            u = User(name=name, email=email, role='executor',
                     password=generate_password_hash('demo123'), avatar=emoji)
            db.session.add(u)
            db.session.flush()
            ep = ExecutorProfile(user_id=u.id, bio=f'Опытный специалист в области {specs}.',
                                 specializations=specs, experience_years=exp,
                                 completed_orders=completed, rating=rating, avatar_emoji=emoji)
            db.session.add(ep)

        # Blog posts
        posts = [
            ('Как правильно составить задание на курсовую', 'kak-sostavit-zadanie',
             'Подробная инструкция: что указать, чтобы получить именно то, что нужно вашему научруку.',
             'zadanie', '📋'),
            ('Антиплагиат 2026: как пройти проверку', 'antiplagiat-2026',
             'Разбираем актуальные системы проверки и способы повысить оригинальность текста легально.',
             'antiplagiat', '🔍'),
            ('Как структурировать дипломную работу', 'struktura-diploma',
             'Пошаговый план: от введения до заключения. Что должно быть в каждой главе.',
             'diplom', '🎓'),
            ('Оформление по ГОСТу 2026: главные правила', 'gost-2026',
             'Актуальные требования к шрифту, полям, сноскам и списку литературы.',
             'gost', '📐'),
        ]
        for title, slug, excerpt, content, emoji in posts:
            bp = BlogPost(title=title, slug=slug, excerpt=excerpt, content=content, emoji=emoji)
            db.session.add(bp)

        db.session.commit()

# ── PAGES ──────────────────────────────────────────────────────────────

@app.route('/')
def index():
    executors = ExecutorProfile.query.order_by(ExecutorProfile.rating.desc()).limit(4).all()
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).limit(3).all()
    return render_template('index.html', executors=executors, posts=posts)

@app.route('/services')
def services():
    return render_template('services.html', work_types=WORK_TYPES)

@app.route('/executors')
def executors():
    execs = ExecutorProfile.query.order_by(ExecutorProfile.rating.desc()).all()
    return render_template('executors.html', executors=execs)

@app.route('/blog')
def blog():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('blog.html', posts=posts)

@app.route('/blog/<slug>')
def blog_post(slug):
    post = BlogPost.query.filter_by(slug=slug).first_or_404()
    return render_template('blog_post.html', post=post)

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')
        if not name or not email or not password:
            flash('Заполните все обязательные поля', 'error')
            return render_template('register.html')
        if password != confirm:
            flash('Пароли не совпадают', 'error')
            return render_template('register.html')
        if len(password) < 6:
            flash('Пароль должен быть не менее 6 символов', 'error')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('Этот email уже зарегистрирован', 'error')
            return render_template('register.html')
        user = User(name=name, email=email, phone=phone,
                    password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f'Добро пожаловать, {name}! 🎓', 'success')
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            return redirect(request.args.get('next') or url_for('dashboard'))
        flash('Неверный email или пароль', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    orders = Order.query.filter_by(user_id=current_user.id)\
                        .order_by(Order.created_at.desc()).all()
    stats = {
        'total': len(orders),
        'active': sum(1 for o in orders if o.status in ('Новая', 'В работе', 'На проверке', 'Правки')),
        'done': sum(1 for o in orders if o.status == 'Выполнена'),
    }
    return render_template('dashboard.html', orders=orders, stats=stats)

@app.route('/order/new', methods=['GET', 'POST'])
@login_required
def new_order():
    if request.method == 'POST':
        work_type = request.form.get('work_type', '')
        subject = request.form.get('subject', '').strip()
        specialty = request.form.get('specialty', '').strip()
        topic = request.form.get('topic', '').strip()
        pages = request.form.get('pages', 0)
        deadline = request.form.get('deadline', '')
        uniqueness = request.form.get('uniqueness', '')
        requirements = request.form.get('requirements', '').strip()
        if not all([work_type, subject, topic, pages, deadline]):
            flash('Заполните все обязательные поля', 'error')
            return render_template('order.html', work_types=WORK_TYPES)
        base = PRICE_BASE.get(work_type, 45)
        price = base * int(pages)
        order = Order(user_id=current_user.id, work_type=work_type,
                      subject=subject, specialty=specialty, topic=topic,
                      pages=int(pages), deadline=deadline,
                      uniqueness=uniqueness, requirements=requirements, price=price)
        db.session.add(order)
        db.session.commit()
        flash('Заявка принята! Менеджер свяжется с вами в течение 15 минут 📬', 'success')
        return redirect(url_for('order_detail', order_id=order.id))
    return render_template('order.html', work_types=WORK_TYPES)

@app.route('/order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def order_detail(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        if text:
            msg = Message(order_id=order.id, user_id=current_user.id, text=text)
            db.session.add(msg)
            db.session.commit()
            flash('Сообщение отправлено', 'success')
        return redirect(url_for('order_detail', order_id=order_id))
    messages = Message.query.filter_by(order_id=order.id).order_by(Message.created_at).all()
    return render_template('order_detail.html', order=order, messages=messages)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name', current_user.name).strip()
        current_user.phone = request.form.get('phone', current_user.phone or '').strip()
        db.session.commit()
        flash('Профиль обновлён', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html')

@app.route('/api/price')
def api_price():
    wt = request.args.get('wt', '')
    pages = int(request.args.get('pages', 0) or 0)
    base = PRICE_BASE.get(wt, 45)
    return jsonify({'price': base * pages if pages > 0 else 0})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True, port=5000)
