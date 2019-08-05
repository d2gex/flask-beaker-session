===============================================================================
``Flask-Beaker-Session``: A server-side session management extension for Flask
===============================================================================

A simple Flask extension to handle server-side sessions. Flask's default session would use client-based cookies and
a sign them. However it is Base64url-encode meaning that no sensitive data can be stored in sessions.

For the stream of Flask-based microservices being created as part of the oAuth 2.0 protocol's conceptual model, a
different session management library is needed, hence this `Flask extension`_ compliant tiny library that wraps up
Beaker_ session library.

The extension is at present only handling Filesystem-based server-side session although it can be extended to cover
in-memory, database and other types of session storage.

Install and Run
===============
Flask-Beaker-Session is not available on PyPI yet, so you need to install it with pip providing a GitHub path as
follows:

$ pip install git+https://github.com:d2gex/flask-beaker-session.git@0.1.0#egg=flask-beaker-session



.. code-block:: python

    ''' Initialising Flask Beaker Session extension '''

    from flask_beaker_session import session

    class Config:
        SESSION_EXPIRES = False
        SESSION_TIMEOUT = 3600  # 1 hour
        SESSION_DATA_DIR = '<<path to where to store sessions here>>'


    def create_app(config_class=Config):
        app = Flask(__name__)
        app.config.from_object(config_class)
        session.init_app(app)
        return app

    _app = create_app()


.. code-block:: python

    ''' Using Flask Beaker Session extension '''

    from flask import session

    @app.route('/create')
    def create_session():
        session[var_1] = 'session 1'
        session[var_2] = 5
        session[var_3] = YourObject()
        return ''

    @app.route('/read')
    def read_session():
        return f"{session[var_1]} - {session[var_2]} - {session[var_3]}"

    @app.route('/delete')
    def delete():
        session.pop(var_1)
        return jsonify(var_1 in session)

    @app.route('/delete_all')
    def delete_all_session():
        session.delete()


.. _PyPI: http://pypi.python.org/

.. _Flask extension:
    https://flask.palletsprojects.com/en/1.1.x/extensiondev/

.. _Beaker:
    https://beaker.readthedocs.io/en/latest/sessions.html