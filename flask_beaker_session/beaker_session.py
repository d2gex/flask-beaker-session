from flask.sessions import SessionInterface


class BeakerSessionInterface(SessionInterface):
    '''Implements the abstract base class SessionInterface from Flask
    '''
    def open_session(self, app, request):
        '''
        '''
        session = request.environ['beaker.session']
        return session

    def save_session(self, app, session, response):
        session.save()
