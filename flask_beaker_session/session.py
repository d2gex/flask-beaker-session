from flask import Flask
from flask_beaker_session import config, errors
from flask_beaker_session.session_middleware import SessionMiddleware
from flask_beaker_session.session_interface import BeakerSessionInterface


class Session:

    def __init__(self, app=None):

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if not app or not isinstance(app, Flask):
            raise errors.ConfigurationError('Invalid Flask application instance')

        session_opts = {
            'session.type': app.config.get('SESSION_TYPE', config.SESSION_TYPE),
            'session.cookie_expires': app.config.get('SESSION_EXPIRES', config.SESSION_EXPIRES),
            'session.data_dir': app.config.get('SESSION_DATA_DIR', config.SESSION_DATA_DIR),
            'session.timeout': app.config.get('SESSION_TIMEOUT', config.SESSION_TIMEOUT)
        }
        # TODO: Integrate other backend session storage such redis, memcache and db-based

        is_testing = app.config.get('SESSION_TESTING', False)
        app.wsgi_app = SessionMiddleware(app.wsgi_app, session_opts)
        app.session_interface = BeakerSessionInterface(is_testing=is_testing)
