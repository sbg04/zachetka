from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Order, Expert, Message, BlogPost
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'zachetka-secret-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///zachetka.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Войдите в аккаунт, чтобы продолжить'

@login_manager.user_loader
def load_user(uid): return User.query.get(int(uid))

WORK_TYPES = [
    'Дипломная работа (ВКР)', 'Курсовая работа', 'Реферат', 'Контрольная работа',
    'Лабораторная работа', 'Эссе', 'Доклад', 'Решение задач',
    'Тест / Онлайн-экзамен', 'Отчёт по практике', 'Бизнес-план',
    'Презентация', 'Статья / Научная работа', 'Редактура / Оформление по ГОСТ',
    'Консультация по диплому', 'Чертёж / Проект',
]

PRICE_BASE = {
    'Дипломная работа (ВКР)': 150, 'Курсовая работа': 80, 'Реферат': 40,
    'Контрольная работа': 40, 'Лабораторная работа': 60, 'Эссе': 40,
    'Доклад': 35, 'Решение задач': 50, 'Тест / Онлайн-экзамен': 45,
    'Отчёт по практике': 70, 'Бизнес-план': 90, 'Презентация': 55,
    'Статья / Научная работа': 100, 'Редактура / Оформление по ГОСТ': 30,
    'Консультация по диплому': 200, 'Чертёж / Проект': 80,
}

FAQ = [
    ('Как долго выполняется работа?', 'Срок зависит от объёма и сложности. Реферат — от 6 часов, курсовая — от 3 дней, диплом — от 7 дней. Точные сроки согласовываются при оформлении заявки.'),
    ('Какой процент антиплагиата гарантируете?', 'По умолчанию — от 70% уникальности. Если нужно больше (80–90%), укажите в форме заявки — выполним.'),
    ('Как происходит оплата?', 'Оплата поэтапная: 50% при старте работы, 50% после сдачи. Средства резервируются — выплачиваются автору только после вашего подтверждения.'),
    ('Что если работа не понравится?', 'Включены бесплатные правки до полного принятия. Если работа не соответствует заданию — возврат средств.'),
    ('Это законно?', 'Да. Мы оказываем образовательные услуги. Работа передаётся как пример и обучающий материал — как её использовать, решаете вы.'),
    ('Могу ли я общаться с автором напрямую?', 'Да! После оформления заявки открывается чат с исполнителем прямо в личном кабинете.'),
    ('Работаете ли с техническими специальностями?', 'Да — математика, физика, программирование, инженерные дисциплины, чертежи. У нас более 300 авторов разных специализаций.'),
    ('Соблюдается ли конфиденциальность?', 'Полностью. Ваши данные не передаются третьим лицам. Авторы подписывают NDA.'),
]

def seed_data():
    if Expert.query.count() == 0:
        experts = [
            Expert(name='Алексей Морозов', avatar='👨‍💼', specialization='Экономика, Финансы, Менеджмент', experience=7, rating=4.97, orders_done=834, bio='Кандидат экономических наук, доцент. Специализируюсь на финансовом анализе и стратегическом менеджменте.'),
            Expert(name='Мария Соколова', avatar='👩‍🔬', specialization='Математика, Физика, Программирование', experience=5, rating=4.95, orders_done=612, bio='Выпускница МФТИ. Решаю задачи любой сложности по высшей математике, теормеху и Python/Java.'),
            Expert(name='Дмитрий Волков', avatar='👨‍⚖️', specialization='Право, Юриспруденция, Государственное управление', experience=9, rating=4.98, orders_done=1102, bio='Практикующий юрист. Дипломные и курсовые по всем отраслям права — гражданское, уголовное, международное.'),
            Expert(name='Анна Петрова', avatar='👩‍🏫', specialization='Педагогика, Психология, Социология', experience=6, rating=4.92, orders_done=487, bio='Магистр педагогики. Помогаю со всеми видами работ по гуманитарным и социальным дисциплинам.'),
            Expert(name='Игорь Кузнецов', avatar='👨‍🔧', specialization='Строительство, Архитектура, Черчение', experience=8, rating=4.94, orders_done=723, bio='Главный инженер-проектировщик. Чертежи, курсовые и дипломные по строительным и техническим специальностям.'),
            Expert(name='Екатерина Лебедева', avatar='👩‍⚕️', specialization='Медицина, Биология, Химия', experience=4, rating=4.89, orders_done=318, bio='Врач-терапевт, аспирант медицинского университета. Работы по медицинским и биологическим дисциплинам.'),
        ]
        for e in experts: db.session.add(e)

    if BlogPost.query.count() == 0:
        posts = [
            BlogPost(title='Как правильно составить техническое задание на курсовую', slug='kak-sostavit-tz', excerpt='Подробное ТЗ — залог качественной работы. Рассказываем, что обязательно нужно указать.', emoji='📋', content='Подробное ТЗ — залог успеха...'),
            BlogPost(title='Как пройти антиплагиат: 7 легальных способов', slug='antiplagiat-sposoby', excerpt='Разбираем официальные методы повышения уникальности текста без потери смысла.', emoji='🔍', content='Уникальность текста важна...'),
            BlogPost(title='Структура дипломной работы по ГОСТу 2026', slug='struktura-diplom-2026', excerpt='Актуальные требования к оформлению ВКР: титульный лист, содержание, список литературы.', emoji='🎓', content='ГОСТ 2026 требует...'),
            BlogPost(title='Как выбрать тему курсовой: пошаговый гид', slug='vybor-temy-kursovoy', excerpt='Советы по выбору темы, которая понравится научному руководителю и будет интересна вам.', emoji='💡', content='Выбор темы — важный шаг...'),
        ]
        for p in posts: db.session.add(p)

    db.session.commit()

# ── ROUTES ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    experts = Expert.query.filter_by(is_active=True).limit(4).all()
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).limit(4).all()
    return render_template('index.html', experts=experts, posts=posts, work_types=WORK_TYPES)

@app.route('/services')
def services():
    return render_template('services.html', work_types=WORK_TYPES, price_base=PRICE_BASE)

@app.route('/experts')
def experts():
    all_experts = Expert.query.filter_by(is_active=True).all()
    return render_template('experts.html', experts=all_experts)

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
    return render_template('faq.html', faq=FAQ)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        email = request.form.get('email','').strip().lower()
        phone = request.form.get('phone','').strip()
        password = request.form.get('password','')
        confirm = request.form.get('confirm','')
        if not name or not email or not password:
            flash('Заполните все обязательные поля','error'); return render_template('register.html')
        if password != confirm:
            flash('Пароли не совпадают','error'); return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('Email уже зарегистрирован','error'); return render_template('register.html')
        user = User(name=name, email=email, phone=phone, password=generate_password_hash(password))
        db.session.add(user); db.session.commit()
        login_user(user)
        flash(f'Добро пожаловать, {name}! 🎓','success')
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            return redirect(request.args.get('next') or url_for('dashboard'))
        flash('Неверный email или пароль','error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user(); return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    stats = {
        'total': len(orders),
        'active': sum(1 for o in orders if o.status in ('Новая','В работе','На проверке')),
        'done': sum(1 for o in orders if o.status == 'Выполнена'),
    }
    return render_template('dashboard.html', orders=orders, stats=stats)

@app.route('/order/new', methods=['GET', 'POST'])
@login_required
def new_order():
    if request.method == 'POST':
        work_type = request.form.get('work_type','')
        subject = request.form.get('subject','').strip()
        specialty = request.form.get('specialty','').strip()
        topic = request.form.get('topic','').strip()
        pages = request.form.get('pages', 1)
        deadline = request.form.get('deadline','')
        antiplagiat = request.form.get('antiplagiat', 70)
        requirements = request.form.get('requirements','').strip()
        if not all([work_type, subject, topic, pages, deadline]):
            flash('Заполните все обязательные поля','error')
            return render_template('order.html', work_types=WORK_TYPES)
        price = PRICE_BASE.get(work_type, 45) * int(pages)
        order = Order(user_id=current_user.id, work_type=work_type, subject=subject,
                      specialty=specialty, topic=topic, pages=int(pages), deadline=deadline,
                      antiplagiat=int(antiplagiat), requirements=requirements, price=price)
        db.session.add(order); db.session.commit()
        flash('Заявка подана! Менеджер свяжется с вами в течение 15 минут 📬','success')
        return redirect(url_for('dashboard'))
    wt = request.args.get('wt','')
    return render_template('order.html', work_types=WORK_TYPES, preselect=wt)

@app.route('/order/<int:oid>')
@login_required
def order_detail(oid):
    order = Order.query.filter_by(id=oid, user_id=current_user.id).first_or_404()
    return render_template('order_detail.html', order=order)

@app.route('/order/<int:oid>/message', methods=['POST'])
@login_required
def send_message(oid):
    order = Order.query.filter_by(id=oid, user_id=current_user.id).first_or_404()
    text = request.form.get('text','').strip()
    if text:
        msg = Message(order_id=oid, sender='user', text=text)
        db.session.add(msg); db.session.commit()
    return redirect(url_for('order_detail', oid=oid))

@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name', current_user.name).strip()
        current_user.phone = request.form.get('phone', current_user.phone or '').strip()
        db.session.commit()
        flash('Профиль обновлён','success')
        return redirect(url_for('profile'))
    return render_template('profile.html')

# ── ADMIN ─────────────────────────────────────────────────────────────────────

ADMIN_LOGIN = 'admin'
ADMIN_PASSWORD = 'zachetka2026'

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_panel'))
    if request.method == 'POST':
        if request.form.get('login') == ADMIN_LOGIN and request.form.get('password') == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_panel'))
        flash('Неверный логин или пароль', 'error')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/panel')
@admin_required
def admin_panel():
    status_filter = request.args.get('status')
    if status_filter:
        orders = Order.query.filter_by(status=status_filter).order_by(Order.created_at.desc()).all()
    else:
        orders = Order.query.order_by(Order.created_at.desc()).all()
    users = User.query.order_by(User.created_at.desc()).all()
    all_orders = Order.query.all()
    stats = {
        'total': len(all_orders),
        'new': sum(1 for o in all_orders if o.status == 'Новая'),
        'active': sum(1 for o in all_orders if o.status == 'В работе'),
        'done': sum(1 for o in all_orders if o.status == 'Выполнена'),
        'users': User.query.count(),
        'revenue': sum(o.price or 0 for o in all_orders if o.status == 'Выполнена'),
    }
    return render_template('admin.html', orders=orders, users=users, stats=stats, status_filter=status_filter)

@app.route('/admin/order/<int:oid>')
@admin_required
def admin_order_detail(oid):
    order = Order.query.get_or_404(oid)
    return render_template('admin_order.html', order=order)

@app.route('/admin/order/<int:oid>/update', methods=['POST'])
@admin_required
def admin_update_order(oid):
    order = Order.query.get_or_404(oid)
    order.status = request.form.get('status', order.status)
    price = request.form.get('price', '')
    if price: order.price = float(price)
    db.session.commit()
    flash(f'Заявка #{oid} обновлена', 'success')
    return redirect(request.referrer or url_for('admin_panel'))

@app.route('/admin/order/<int:oid>/message', methods=['POST'])
@admin_required
def admin_message(oid):
    order = Order.query.get_or_404(oid)
    text = request.form.get('text', '').strip()
    if text:
        msg = Message(order_id=oid, sender='expert', text=text)
        db.session.add(msg); db.session.commit()
    return redirect(url_for('admin_order_detail', oid=oid))

with app.app_context():
    db.create_all()
    seed_data()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
