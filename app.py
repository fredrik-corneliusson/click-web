from click_web import flask_app, register

import example_command

register(example_command, example_command.cli)
