import pytest

from flask import Flask
from unittest.mock import Mock
from flask_beaker_session import config, session, errors


def test_init_app():
    '''Ensure init_app work as follows:

    1) if the passed app is not a Flask instance => raise a ConfigurationError exception
    2) if SESSION_TYPE conf option not provided => raise a ConfigurationError exception
    '''

    # (1)
    with pytest.raises(errors.ConfigurationError) as ex:
        session.Session(app=Mock())
    assert 'Invalid Flask' in str(ex)

    # (2)
    app = Flask(__name__)
    with pytest.raises(errors.ConfigurationError) as ex:
        session.Session(app=app)
    assert "'SESSION_TYPE'" in str(ex)

    # (3)
    app.config.from_mapping(SESSION_TYPE=config.SESSION_TYPE)
    with pytest.raises(errors.ConfigurationError) as ex:
        session.Session(app=app)
    assert "'SESSION_EXPIRES'" in str(ex)
