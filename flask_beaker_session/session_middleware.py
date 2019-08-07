from beaker import middleware
from beaker.session import Session, SessionObject


class SessionMiddleware(middleware.SessionMiddleware):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def restore_session(self, environ):
        '''Given a wsgi environment it reconstruct a session object
        :param environ: wsgi environment
        :return: session object
        '''
        session = SessionObject(environ, **self.options)
        environ[self.environ_key] = session
        environ['beaker.get_session'] = self._get_session
        return Session({}, use_cookies=True, **self.options)
