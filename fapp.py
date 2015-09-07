from flask import session
from models import User, Post, UserPostAction

from utils import app_exceptions
from utils.error_handler import report_error
from configs import config
from functools import wraps
from flask import session, request, redirect, url_for, abort, flash, render_template, g
from app_objects import app
import scraper


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = None
        user_id = session.get('id')
        if user_id:
            user = User.get_user(user_id)
        g.loggedin_user = user
        if not user:
            flash('You need to login.', category='error')
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function


def add_user_to_session(user):
    session['id'] = user.id
    session['user_type'] = user.user_type


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    next_url = request.args.get('next', url_for('home'))

    if session.get('id'):
        return redirect(next_url)

    if request.method == 'POST':
        user = User.query.filter(User.username==request.form.get('username')).first()
        if user and user.check_password(password=request.form.get('password')):
            add_user_to_session(user)
            flash('You have been logged in.', category='success')
            return redirect(next_url)
        else:
            flash('Invalid credentials', category='warning')

    return render_template('login.html', next_url=next_url)



@app.route('/register', methods=['POST', 'GET'])
def register():
    error = None
    next_url = request.args.get('next', url_for('home'))

    if session.get('id'):
        return redirect(next_url)

    if request.method == 'POST':
        try:
            user = User.add_new(username=request.form.get('username'), password=request.form.get('password'))
            add_user_to_session(user)
            return redirect(url_for('home'))
        except app_exceptions.BadRequestException as e:
            flash(str(e))
            return render_template('login.html', next_url=next_url)

    
    return render_template('login.html', next_url=next_url)


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('id', None)
    flash('Logged out successfully', category='success')
    return redirect(url_for('login'))


@app.route('/home', methods=['GET'])
@login_required
def home():
    page_num = int(request.args.get('page_num', 1))
    limit = 30
    offset = limit * (page_num-1)
    posts = [Post.to_dict(post) for post in Post.get_posts(viewer_id=g.loggedin_user.id, offset=offset, limit=limit)]
    more_posts = True
    if len(posts)<limit:
        more_posts = False
    return render_template('post_list.html', post_list=posts, page_num=page_num, more_posts=more_posts)


@app.route('/action/<action_type>', methods=['GET'])
@login_required
def action(action_type):
    post_id = request.args.get('post_id')
    next_url = request.args.get('next', url_for('home'))
    if post_id:
        if action_type == 'delete':
            UserPostAction.add_action(user_id=g.loggedin_user.id, post_id=post_id, marked_deleted=True)
            flash("Post has been deleted.", category='success')
        elif action_type == 'read':
            UserPostAction.add_action(user_id=g.loggedin_user.id, post_id=post_id, marked_read=True)
            flash("Post has been marked_read.", category='success')
    return redirect(next_url)


@app.route('/fetchnew', methods=['GET'])
@login_required
def fetch_new():
    """
    TODO: Run this task in celery or async thread.
    """
    next_url = request.args.get('next', url_for('home'))

    if session.get('user_type') == 5:
        scraper.run_scraper()
        flash("New posts have been fetched.", category='success')
    else:
        flash("You are not allowed to perform that action.", category='warning')

    return redirect(next_url)
