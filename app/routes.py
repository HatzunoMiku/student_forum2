from flask import render_template, url_for, flash, redirect, request
from app import app, db
from app.forms import RegistrationForm, LoginForm, ThreadForm, PostForm
from app.models import User, Thread, Post
from flask_login import login_user, current_user, logout_user, login_required

@app.route('/')
@app.route('/home')
def home():
    threads = Thread.query.order_by(Thread.created_at.desc()).all()
    return render_template('home.html', threads=threads)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Check email and password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/thread/new', methods=['GET', 'POST'])
@login_required
def new_thread():
    form = ThreadForm()
    if form.validate_on_submit():
        thread = Thread(title=form.title.data, author=current_user)
        db.session.add(thread)
        db.session.commit()
        flash('Thread created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_thread.html', form=form)

@app.route('/thread/<int:thread_id>', methods=['GET', 'POST'])
def thread(thread_id):
    thread = Thread.query.get_or_404(thread_id)
    form = PostForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('You need to login to post.', 'danger')
            return redirect(url_for('login'))
        post = Post(content=form.content.data, author=current_user, thread=thread)
        db.session.add(post)
        db.session.commit()
        flash('Post added!', 'success')
        return redirect(url_for('thread', thread_id=thread.id))
    posts = Post.query.filter_by(thread_id=thread.id).order_by(Post.created_at.asc()).all()
    return render_template('thread.html', thread=thread, posts=posts, form=form)
