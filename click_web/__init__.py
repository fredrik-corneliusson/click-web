from pathlib import Path

import click
import click_web.resources.index
import click_web.resources.exec_command
from flask import Flask

import click_web.resources.command

'The full path to the click script file to execute.'
script_file = None
'The click root command to serve'
click_root_cmd = None

def register(module, command: click.BaseCommand):
    '''

    :param module: the module that contains the command, needed to get the path to the script.
    :param command: The actual click root command, needed to be able to read the command tree and arguments
                    in order to generate the index page and the html forms
    usage:

        from click_web import flask_app, register

        import a_click_script

        click_web.register(a_click_script,
                           a_click_script.a_group_or_command)

    '''
    global click_root_cmd, script_file
    script_file = str(Path(module.__file__).absolute())
    click_root_cmd = command


flask_app = Flask(__name__)
flask_app.add_url_rule('/', 'index', click_web.resources.index.index)
flask_app.add_url_rule('/<path:command_path>', 'command', click_web.resources.command.get_form_for)
flask_app.add_url_rule('/exec/<path:command_path>', 'command_execute', click_web.resources.exec_command.exec, methods=['POST'])
