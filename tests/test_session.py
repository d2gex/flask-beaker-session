import pytest
import time

from os import path
from flask import Flask, session, jsonify
from flask.sessions import SecureCookieSessionInterface
from beaker.middleware import SessionMiddleware
from flask_beaker_session import config, session as beaker_session, errors, session_interface
from unittest.mock import Mock


@pytest.fixture()
def data_dir(tmp_path):
    return tmp_path / "tmp" / ".sessions"


def test_init_app():
    '''Ensure init_app work as follows:

    1) if the passed app is not a Flask instance => raise a ConfigurationError exception
    2) app.wsgi_app should be of beaker.middleware.SessionMiddleware type after initialisation
    3) SESSION_TYPE, SESSION_EXPIRES and SESSION_DATA_DIR should be provided as default value if not present in config
    '''

    # (1)
    with pytest.raises(errors.ConfigurationError) as ex:
        beaker_session.Session(app=Mock())
    assert 'Invalid Flask' in str(ex.value)

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
    assert session_options['timeout'] == config.SESSION_TIMEOUT


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


def test_filesystem_session(data_dir):
    '''Test Filesystem-stored sessions as follows:

    1) When a session variable is persisted => a file is created and cookie is stuck in the headers
    2) Popping an individual variable from session dict will remove it from the session
    3) session.delete() will delete all session variables
    '''

    assert not path.exists(data_dir)

    class Config:
        SESSION_DATA_DIR = data_dir

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
    assert path.exists(data_dir)
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


def test_test_filesystem_session_with_expired_time_in_seconds(data_dir):
    '''Test Filesystem-stored sessions with an expiry date set in seconds
    '''

    class Config:
        SESSION_DATA_DIR = data_dir
        SESSION_TIMEOUT = 3

    app = Flask(__name__)
    app.config.from_object(Config)
    beaker_session.Session(app=app)

    var_1 = 'var_1'

    @app.route('/create')
    def create_session():
        session[var_1] = var_1
        session['var_2'] = 'var_2'
        return session[var_1]

    @app.route('/read')
    def read_session():
        return jsonify(var_1 in session)

    # create session
    test_app = app.test_client()
    response = test_app.get('/create')
    assert response.status_code == 200
    assert var_1 in response.get_data(as_text=True)

    # Wait twice as much as the session longevity
    time.sleep(Config.SESSION_TIMEOUT * 2)
    response = test_app.get('/read')
    assert response.status_code == 200
    assert not response.get_json()


def test_flask_client_session_transaction_method(data_dir):
    '''Test that the new flask extension can work with the FlaskClient.session_transaction method as follows

    1) A session can be reopened with session_transaction() to check the value from a previous FlaskClient object
    2) A session can be open with session_transaction() to modify the value for view later on to use
    '''

    class Config:
        SESSION_DATA_DIR = data_dir
        SESSION_TESTING = True

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
        return jsonify(session['_creation_time'], session['_accessed_time'])

    @app.route('/read')
    def read_session():
        return jsonify({'data': session['var_4'],
                        'creation_time': session['_creation_time'],
                        'accessed_time': session['_accessed_time']})

    # 1)
    test_app = app.test_client()
    response = test_app.get('/create')
    with test_app.session_transaction() as b_session:
        assert var_1 in b_session
        data = response.get_json()
        assert data[0] == b_session['_creation_time']
        assert data[-1] <= b_session['_accessed_time']

    # 2)
    with test_app.session_transaction() as b_session:
        b_session['var_4'] = 'var_4'
        creation_time = b_session['_creation_time']
        accessed_time = b_session['_accessed_time']

    response = test_app.get('/read')
    data = response.get_json()
    assert data['data'] == 'var_4'
    assert data['creation_time'] == creation_time
    assert accessed_time <= data['accessed_time']
