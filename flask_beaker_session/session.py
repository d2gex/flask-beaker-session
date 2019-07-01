from flask import Flask
from beaker.middleware import SessionMiddleware
from flask_beaker_session import config, errors, session_interface


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
        # TO-DO: Integrate other backend session storage such redis, memcache and db-based

        app.wsgi_app = SessionMiddleware(app.wsgi_app, session_opts)
        app.session_interface = session_interface.BeakerSessionInterface()
