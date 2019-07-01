import pytest

from os import path, listdir
from flask import Flask, session, jsonify
from flask.sessions import SecureCookieSessionInterface
from beaker.middleware import SessionMiddleware
from flask_beaker_session import config, session as beaker_session, errors, session_interface
from unittest.mock import Mock


def test_init_app():
    '''Ensure init_app work as follows:

    1) if the passed app is not a Flask instance => raise a ConfigurationError exception
    2) app.wsgi_app should be of beaker.middleware.SessionMiddleware type after initialisation
    3) SESSION_TYPE, SESSION_EXPIRES and SESSION_DATA_DIR should be provided as default value if not present in config
    '''

    # (1)
    with pytest.raises(errors.ConfigurationError) as ex:
        beaker_session.Session(app=Mock())
    assert 'Invalid Flask' in str(ex)

    # (2)
    app = Flask(__name__)
    assert not isinstance(app.wsgi_app, SessionMiddleware)
    assert isinstance(app.session_interface, SecureCookieSessionInterface)
    beaker_session.Session(app=app)
    assert isinstance(app.wsgi_app, SessionMiddleware)
    assert isinstance(app.session_interface, session_interface.BeakerSessionInterface)

    # (3)
    session_options = app.wsgi_app.options
    assert session_options['type'] == config.SESSION_TYPE
    assert session_options['cookie_expires'] == config.SESSION_EXPIRES
    assert session_options['data_dir'] == config.SESSION_DATA_DIR


def test_factory_class_config_patterns():
    '''Application factory pattern and Class-Inheritance configuration pattern should work as expected
    '''

    class Config:
        SESSION_TYPE = 'redis'
        SESSION_EXPIRES = False
        SESSION_DATA_DIR = 'another_folder'

    session_ext = beaker_session.Session()

    def create_app(config_class=Config):
        app = Flask(__name__)
        app.config.from_object(config_class)
        session_ext.init_app(app)
        return app

    _app = create_app()

    assert isinstance(_app.wsgi_app, SessionMiddleware)
    assert isinstance(_app.session_interface, session_interface.BeakerSessionInterface)

    session_options = _app.wsgi_app.options
    assert session_options['type'] == Config.SESSION_TYPE
    assert session_options['cookie_expires'] == Config.SESSION_EXPIRES
    assert session_options['data_dir'] == Config.SESSION_DATA_DIR


def test_filesystem_session(tmp_path):
    '''Test Filesystem-stored sessions as follows;

    1) When a session variable is persisted => a file is created and cookie is stuck in the headers
    2) Popping an individual variable from session dict will remove it from the session
    3) session.delete() will delete all session variables
    '''
    d = tmp_path / "tmp"
    assert not path.exists(d / ".sessions")

    class Config:
        SESSION_DATA_DIR = d / '.sessions'

    app = Flask(__name__)
    app.config.from_object(Config)
    beaker_session.Session(app=app)

    var_1 = 'var_1'
    var_2 = 'var_2'
    var_3 = 'var_3'

    @app.route('/create')
    def create_session():
        session[var_1] = var_1
        session[var_2] = var_2
        session[var_3] = var_3
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
        return f"session is {'NOT' if any([keyword in session for keyword in (var_1, var_2, var_3)]) else ''} deleted"

    test_app = app.test_client()

    # (1)
    response = test_app.get('/create')
    assert path.exists(d / ".sessions")
    assert response.status_code == 200
    try:
        session_id = response.headers['Set-cookie']
    except KeyError:
        raise AssertionError("'Set-cookie' header has not been set")
    assert 'beaker.session.id' in session_id
    response = test_app.get('/read')
    assert all([keyword in response.get_data(as_text=True)] for keyword in [var_1, var_2])

    # (2)
    response = test_app.get('/delete')
    assert response.get_json() is False

    # (3)
    response = test_app.get('/delete_all')
    assert 'NOT' not in response.get_data(as_text=True)
