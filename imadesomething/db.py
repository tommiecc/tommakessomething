import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

#g is a special object that is unique for each request. it is used to store data the might be access by multiple functions.
def get_db(): #define the get_db command
    if 'db' not in g: #if the database has not been opened yet.
        #add db to g.
        #connect db to sqlite3 database.
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row #tells rows to behave like python dictionaries . this allows accessing the columsn by name.

    return g.db


def close_db(e=None):
    #checks if a connect was created by checking if g.db is set. if a connection exists it will close it.
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db() #get the database

    with current_app.open_resource('schema.sql') as f: #open the schema.sql file as f. open_reasource opens a file relative to the imadesomething package, regardless of location.
        db.executescript(f.read().decode('utf8')) #decode the schema.sql file in utf8


@click.command('init-db') #if init-db is called in the terminal
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db() #call init_db
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

