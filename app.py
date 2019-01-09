from click_web import flask_app, register

import test_command

register(test_command, test_command.cli)
