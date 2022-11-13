import functools
#import functools to decorate functions. then we can use functions that act on or return other functions cleanly
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
) #import flask stuff to build the blueprints
from werkzeug.security import check_password_hash, generate_password_hash #import security to hash the password

from imadesomething.db import get_db #import the database to write and read from

bp = Blueprint('auth', __name__, url_prefix='/auth') #defines the blueprint with prefix of /auth for all routes.
@bp.route('/register', methods=('GET', 'POST')) #defines register route.
def register():
    if request.method == 'POST': #same as 'create' for index.py
        username = request.form['username'] #requests the information from the form, the input with the id 'username'
        password = request.form['password'] #requests the information from the form, the input with the id 'password'
        db = get_db() #initalise connect with the database
        error = None

        if not username: #make sure the username field has been inputed
            error = 'Username is required.' #otherwise error is thrown
        elif not password: #make sure the password field has been inputed
            error = 'Password is required.' #otherwise error is thrown

        if error is None: #make sure the there are no errore
            try: #attmept to execute a SQLite command
                db.execute(
                    "INSERT INTO user (username, upassword) VALUES (?, ?)",
                    (username, generate_password_hash(password)), #we will has the password to make it more secure.
                )
                db.commit() #finalise database

            except db.IntegrityError: #if there is a problem then sqlite will throw an IntergrityError, if we see that it has we will set error to username already exists.
                error = f"User {username} is already registered."

            else:
                return redirect(url_for("auth.login")) #if all good then go to login page

        flash(error) #incase any errors show then to display.

    return render_template('auth/register.html') #going to this page will display the register.html file.

@bp.route('/login', methods=('GET', 'POST')) #the login page, with get and post methods to send and recieve data
def login():
    if request.method == 'POST': #make sure that the request method is post
        username = request.form['username'] #requests the information from the form, the input with the id 'username'
        password = request.form['password'] #requests the information from the form, the input with the id 'password'
        db = get_db() #initalise connection with the database
        error = None #set errors to None so we don't accidently throw errors from previous goes.
        user = db.execute( #get the username from databse using the form input
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None: #if the username with the information on the form is not found
            error = 'Incorrect username.' #then throw an error
        elif not check_password_hash(user['upassword'], password): #check that the password inputed matches the de-hashed password stored on the database
            error = 'Incorrect password.' #otherwise thrown an error

        if error is None: #if there are no errors
            session.clear() #clear the current session cookies
            session['user_id'] = user['id'] #set the new session to the current user id
            return redirect(url_for('index.index')) #redirect user to main page

        flash(error) #otherwise flash errors to flash area on base.html file.

    return render_template('auth/login.html') #when this route is called then it will render the login.html file.

@bp.before_app_request #before_app_request registers a function that is called everytime that a page is loaded no matter the url.
def load_logged_in_user():
    user_id = session.get('user_id') #this function gets the current user's session cookie data

    if user_id is None: #checks if it is none
        g.user = None # if it is none then g.user (which is a variable that tells the program what user is currently logged in) is none
    else: #if g.user is not empty
        g.user = get_db().execute( #then the current g.user is equal to the user information from the user table where the id of the user equals the current user id
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear() #when user goes to /logout (via logout button) the session cookies are cleared (logging the user out)
    return redirect(url_for('index.index')) #redirect the user back to the main page.

def login_required(view): #define the 'log_required' function for pages such as blog/update or project/create
    @functools.wraps(view) #functools.wraps decorates the nested function. the decorator returns a new function that checks if the user is logged in or not.
    def wrapped_view(**kwargs):
        if g.user is None: #if the user is not logged in
            return redirect(url_for('auth.login')) #then redirect them to the login page

        return view(**kwargs)

    return wrapped_view
