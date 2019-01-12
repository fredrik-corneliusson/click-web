from pathlib import Path

import click
import click_web.web
import click_web.web_exec
from flask import Flask

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

        import click_web
        from click_web import app
        import a_command

        click_web.register(a_command, a_command.cli)

    '''
    global click_root_cmd, script_file
    script_file = str(Path(module.__file__).absolute())
    click_root_cmd = command


flask_app = Flask(__name__)
flask_app.add_url_rule('/', 'index', click_web.web.index)
flask_app.add_url_rule('/<path:command_path>', 'command', click_web.web.get_form_for)
flask_app.add_url_rule('/exec/<path:command_path>', 'command_execute', click_web.web_exec.exec, methods=['POST'])
