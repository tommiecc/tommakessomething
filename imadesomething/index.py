from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
) #import flask and a bunch of it's functions and classes to initilise blueprints and complete specialised functions
from werkzeug.exceptions import abort
#import werkzeug to use abort in case of error
from imadesomething.auth import login_required #import functions from other python files in directory
from imadesomething.db import get_db

#create blueprint which will be used for home, projects, and blog
bp = Blueprint('index', __name__)
@bp.route('/blog') #create a 'route' which is the path on the search engine to get to destination. In this case when it is https://example.com/blog it will call this function
def blog(): #define what this function is
    db = get_db() #access the database
    posts = db.execute( #execute a SQL command to pull data from blog
        'SELECT blog.id, blog.title, blog.body, blog.created, blog.url, blog.author_id, username'
        ' FROM blog blog JOIN user u ON blog.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    #display blog.html to window and set posts to posts so they can be iterated through in html fikle
    return render_template('blog/blog.html', posts=posts)

@bp.route('/') #create another route
def index():
    db = get_db() #complete sample process as above however with the 'projects' table
    projects = db.execute(
        'SELECT projects.id, projects.title, projects.body, projects.created, projects.url, projects.author_id, username'
        ' FROM projects projects JOIN user u ON projects.author_id = u.id'
        ' ORDER BY created DESC'
    )
    #return index.ht,l to window and set projects to projecred so they can be interated through in html file
    return render_template('index/index.html', projects=projects)

#pages for blog
@bp.route('/blog/create', methods=('GET', 'POST'))
@login_required #this time a login is required to access this page, if the user is not logged in it will taken them back to the home page
def create():
    if request.method == 'POST': #checks that the request method from the 'create' form is in post mode
        title = request.form['title'] #sets title to the input named 'title'
        body = request.form['body']
        url = request.form['url']
        error = None

        if not title: #if there is no title
            error = 'Title is required.' #then it will set an error

        if error is not None: #if there are errors
            flash(error) #display error to front-end
        else:
            db = get_db() #otherwise, get the infomation for the database
            db.execute( #and with the database execute a SQLite command.
                'INSERT INTO blog (title, body, url, author_id)' #into the 'blog' table we will insert values into title, body, url, and author id.
                ' VALUES (?, ?, ?, ?)',
                (title, body, url, g.user['id']) #VALUES is equal to the title, body, url, and g.user[id] (g.user defined in database) variables
            )
            db.commit()
            return redirect(url_for('index.blog')) #once done take user back to blog page.

    return render_template('blog/create.html') #render the html file create.html

def get_post(id, check_author=True): 
    post = get_db().execute( #gets all information from a blog post with certain id.
        'SELECT b.id, b.title, b.body, b.created, b.author_id, username'
        ' FROM blog b JOIN user u ON b.author_id = u.id'
        ' WHERE b.id = ?',
        (id,)
    ).fetchone()

    if post is None: #if the post doesn't exist then abort with a 404 error.
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:#if someone who isn't the author is trying to delete it
        abort(403) #abort with a 403 'forbidden' error

    return post 

@bp.route('/blog/<int:id>/update', methods=('GET', 'POST'))
@login_required #for updates login is required.
def update(id):
    post = get_post(id) #get the post with the id used in the url

    if request.method == 'POST':
        title = request.form['title'] #same as create
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE blog SET title = ?, body = ?' #however instead of insert we are using UPDATE to update a certain row with a certain id.
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('index.blog')) #when finished redirect user to blog.

    return render_template('blog/update.html', post=post) #render and display update.html file, with the post equal to the post that we collected at get_post(id)

@bp.route('/blog/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id) #get the post
    db = get_db() #access the database
    db.execute('DELETE FROM blog WHERE id = ?', (id,)) #use the SQLite DELETE command to remove row with id of <int:id> from blog table.
    db.commit() #finalise and close the database
    return redirect(url_for('index.blog')) #after redirect user to the blog page.

"""
projects are idenitical to blog however the blog, post and b keywords have been replaced with projects, project, and p
"""
@bp.route('/projects/create', methods=('GET', 'POST'))
@login_required
def createProject():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        url = request.form['url']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO projects (title, body, url, author_id)'
                ' VALUES (?, ?, ?, ?)',
                (title, body, url, g.user['id'])
            )
            db.commit()
            return redirect(url_for('index.index'))

    return render_template('projects/createproject.html')

def get_project(id, check_author=True):
    project = get_db().execute(
        'SELECT projects.id, projects.title, projects.body, projects.created, projects.url, projects.author_id, username'
        ' FROM projects projects JOIN user u ON projects.author_id = u.id'
        ' WHERE projects.id = ?',
        (id,)
    ).fetchone()

    if project is None:
        abort(404, f"Project id {id} doesn't exist.")

    if check_author and project['author_id'] != g.user['id']:
        abort(403)

    return project

@bp.route('/projects/<int:id>/update', methods=('GET', 'POST'))
@login_required
def updateProject(id):
    project = get_project(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE projects SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('index.index'))

    return render_template('projects/updateproject.html', project=project)

@bp.route('/projects/<int:id>/delete', methods=('POST',))
@login_required
def deleteProject(id):
    get_project(id)
    db = get_db()
    db.execute('DELETE FROM projects WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('index.index'))


