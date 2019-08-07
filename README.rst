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
follows::

    $ pip install git+https://github.com/d2gex/flask-beaker-session.git@0.1.0#egg=flask_beaker_session



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

Configuration Options
=====================
You can change some options for how this extension works via::

    app.config[OPTION_NAME] = new_options

The following options are available:

1.  SESSION_TYPE: At present only ``file`` option is supported as session are stored in the the filesystem
2.  SESSION_EXPIRES: ``True`` or ``False`` option for the session to expire or not, respectively. By default they expire
3.  SESSION_TIMEOUT: ``<integer>`` if SESSION_EXPIRES is set, this option says when the session expired if not accessed
    again. By default after 30 minutes expires - ``1800``
4.  SESSION_DATA_DIR : ``path_to_folder`` where the extension will store the session files created. By default they are
    stored in ``./.sessions``
5.  SESSION_TESTING: ``True`` or ``False`` option for the extension to be able to work with the session_transaction()
    method of the FlaskClient object.

Advance Testing
===============
FlaskClient object resulting from `app.test_client()` can be called with `session_transaction()` method to either check
previous session values modified by your views or vice versa, to modify the session object by adding, deleting or
updating any stored value previous to your view running. All that you need to do is::

    SESSION_TESTING = True

And then you can call `session_transaction()` as you would do with Flask's sessions by default as shown below:

.. code-block:: python

    @app.route('/read')
    def read_session():
        return session['var_4']

    test_app = app.test_client()
    with test_app.session_transaction() as b_session:
        b_session['var_4'] = 'var_4'

    response = test_app.get('/read')
    data = response.get_json()
    assert data['data'] == 'var_4'

.. _PyPI: http://pypi.python.org/

.. _Flask extension:
    https://flask.palletsprojects.com/en/1.1.x/extensiondev/

.. _Beaker:
    https://beaker.readthedocs.io/en/latest/sessions.html