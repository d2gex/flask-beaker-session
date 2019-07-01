from flask import Flask
from beaker.middleware import SessionMiddleware
from flask_beaker_session import config, errors, beaker_session


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
            'session.data_dir': app.config.get('SESSION_DATA_DIR', config.SESSION_DATA_DIR)
        }

        app.wsgi_app = SessionMiddleware(app.wsgi_app, session_opts)
        app.session_interface = beaker_session.BeakerSessionInterface()
