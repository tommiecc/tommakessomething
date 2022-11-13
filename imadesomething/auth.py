import functools
#import functools to ...
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
) #import flask stuff to build the blueprints
from werkzeug.security import check_password_hash, generate_password_hash #import security to hash the password 

from imadesomething.db import get_db #import the database to write and read from

bp = Blueprint('auth', __name__, url_prefix='/auth') #defines the blueprint with prefix of /auth for all routes.
@bp.route('/register', methods=('GET', 'POST')) #defines register route.
def register():
    if request.method == 'POST': #same as 'create' for index.py
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, upassword) VALUES (?, ?)",
                    (username, generate_password_hash(password)), #we will has the password to make it more secure.
                )
                db.commit()

            except db.IntegrityError: #if there is a problem then sqlite will throw an IntergrityError, if we see that it has we will set error to username already exists.
                error = f"User {username} is already registered."

            else:
                return redirect(url_for("auth.login")) #otherwise go to login page

        flash(error) #incase any errors show then to display.

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['upassword'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index.index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index.index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view