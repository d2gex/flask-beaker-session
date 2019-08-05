import setuptools
import flask_beaker_session


def get_long_desc():
    with open("README.rst", "r") as fh:
        return fh.read()


setuptools.setup(
    name="Flask-Beaker_Session",
    version=flask_beaker_session.__version__,
    author="Dan G",
    author_email="daniel.garcia@d2garcia.com",
    description="A simple Flask extension that wraps up Beaker to conform Flask Extension Development guidelines",
    long_description=get_long_desc(),
    long_description_content_type="text/x-rst",
    url="https://github.com/d2gex/flask-beaker-session",
    packages=['flask_beaker_session'],
    python_requires='>=3.6',
    install_requires=['Beaker>=1.10.1', 'Flask>=1.0.3'],
    tests_require=['pytest>=5.0.0'],
    platforms='any',
    zip_safe=True,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
