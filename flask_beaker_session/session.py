from flask import Flask
from flask_beaker_session import errors


class Session:

    def __init__(self, app=None):
        self.app = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if not app or not isinstance(app, Flask):
            raise errors.ConfigurationError('Invalid Flask application instance')

        self.app = app
        if 'SESSION_TYPE' not in app.config:
            raise errors.ConfigurationError(f"'SESSION_TYPE' required option not found")

        if 'SESSION_EXPIRES' not in app.config:
            raise errors.ConfigurationError(f"'SESSION_EXPIRES' required option not found")
