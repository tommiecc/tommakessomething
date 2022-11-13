import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='b28f939dde81ec2ded2166dfb5a0fbaf92631e548c4abadc0f31a29588af7d63',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db #import information from the db.py file.
    db.init_app(app) #use the init_app function that we defined with the app information

    from . import auth #import information from auth.py file.
    app.register_blueprint(auth.bp) #use the register_blueprint function to register a 'blueprint' with the app (see more at auth.py)

    from . import index #same as auth.py but with index.py
    app.register_blueprint(index.bp)

    return app #run the app