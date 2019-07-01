===============================================================================
``Flask-Beaker-Session``: A server-side session management extension for Flask
===============================================================================

A simple Flask extension to handle server-side sessions. Flask's default session would use client-based cookies and
a sign them. However it is Base64url-encode meaning that no sensitive data can be stored in sessions.

For the stream of Flask-based microservices being created as part of the oAuth 2.0 protocol's conceptual model, a
different session management library is needed. Hence this `Flask extension`_ compliant tiny library that wraps up
Beaker_ session library.

This library is still underdevelopment ...

.. _Flask extension:
    http://flask.pocoo.org/docs/1.0/extensiondev/

.. _Beaker:
    https://beaker.readthedocs.io/en/latest/sessions.html