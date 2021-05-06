"""
An Example click-web flask app that forces user login before access to click-web command using digest auth.
Please note this is just rudimentary security, unless you serve flask under HTTPS this will not protect data sent and
and is susceptible to Man in the middle attacks.
"""

from flask_httpauth import HTTPDigestAuth

from click_web import create_click_web_app
from example import example_command

# just a dict with username as key and password as value
users = {
    'user': 'password',
    'another_user': 'password'
}


def _get_password_callback(username):
    """For a username return cleartext password"""
    app.logger.info(f'Verifying user: {username}')

    if username in users:
        return users[username]

    return None


def setup_authentication(app, get_pw_callback):
    """
    This sets up HTTPDigestAuth login to a flask app before each request.
    :param app: The flask app to add HTTPDigestAuth to.
    :param get_pw_callback: A function that takes a username and returns cleartext password.
    :return: Nothing
    """
    auth = HTTPDigestAuth()

    @auth.login_required
    def _assert_auth_before_request():
        """
        Run before each request, relies on the fact that the decorator function @auth.login_required
        will not run this code if it fails, and if it did not stop just pass thru call by returning None
        """
        app.logger.info(f'User: {auth.username()}')
        return None

    app.logger.info(f'Setting up {app} to require login...')
    auth.get_password(get_pw_callback)
    app.before_request(_assert_auth_before_request)


# create app
app = create_click_web_app(example_command, example_command.cli)

# Set this to a random key and keep it secret, example from what you get from os.urandom(12)
app.secret_key = b'sbnh&%r%&h/nTHFdgsdfdwekfjkwsfjkhw345rnmklb4564'

# This adds authentication for all requests to flask app.
setup_authentication(app, get_pw_callback=_get_password_callback)
