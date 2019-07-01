import pytest

from flask import Flask
from flask.sessions import SecureCookieSessionInterface
from beaker.middleware import SessionMiddleware
from flask_beaker_session import config, session, errors, beaker_session
from unittest.mock import Mock


def test_init_app():
    '''Ensure init_app work as follows:

    1) if the passed app is not a Flask instance => raise a ConfigurationError exception
    2) app.wsgi_app should be of beaker.middleware.SessionMiddleware type after initialisation
    3) SESSION_TYPE, SESSION_EXPIRES and SESSION_DATA_DIR should be provided as default value if not present in config
    '''

    # (1)
    with pytest.raises(errors.ConfigurationError) as ex:
        session.Session(app=Mock())
    assert 'Invalid Flask' in str(ex)

    # (2)
    app = Flask(__name__)
    assert not isinstance(app.wsgi_app, SessionMiddleware)
    assert isinstance(app.session_interface, SecureCookieSessionInterface)
    session.Session(app=app)
    assert isinstance(app.wsgi_app, SessionMiddleware)
    assert isinstance(app.session_interface, beaker_session.BeakerSessionInterface)

    # (3)
    session_options = app.wsgi_app.options
    assert session_options['type'] == config.SESSION_TYPE
    assert session_options['cookie_expires'] == config.SESSION_EXPIRES
    assert session_options['data_dir'] == config.SESSION_DATA_DIR
