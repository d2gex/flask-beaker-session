from flask.sessions import SessionInterface
from flask_beaker_session import errors


class BeakerSessionInterface(SessionInterface):
    '''Implements the abstract base class SessionInterface from Flask
    '''

    def __init__(self, is_testing=False):
        self.is_testing = is_testing

    def open_session(self, app, request):
        '''This method is invoked in two different ways as follows:

        1) Whenever the wsgi server dispatch a request to a wsgi_app and this start a response
        2) As explicitly pushing a request context and therefore a session for testing purposes

        :param app: wsgi application
        :param request: request context
        :return: session object as expected by Beaker Session
        '''
        try:
            session_data = request.environ['beaker.session']
        except KeyError as ex:
            if not self.is_testing:
                raise errors.ConfigurationError("To use the 'session_transaction() or test_request_method()' the "
                                                "'SESSION_TESTING=True' option is needed") from ex
            # Restore the session object if we are testing session variables
            session_data = app.wsgi_app.restore_session(request.environ)
        return session_data

    def save_session(self, app, session, response):
        session.save()
        if self.is_testing:
            session.persist()
            if session.__dict__['_headers']['cookie_out']:
                cookie, *rest = session.__dict__['_headers']['cookie_out'].split(';')
                response.set_cookie('beaker.session.id', cookie)
