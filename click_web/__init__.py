import tempfile
from pathlib import Path

import click
import jinja2
from flask import Blueprint, Flask

import click_web.resources.cmd_exec
import click_web.resources.cmd_form
import click_web.resources.index

jinja_env = jinja2.Environment(extensions=['jinja2.ext.do'])


def _get_output_folder():
    _output_folder = (Path(tempfile.gettempdir()) / 'click-web')
    if not _output_folder.exists():
        _output_folder.mkdir()
    return _output_folder


logger = None


def create_click_web_app(module, command: click.BaseCommand, root='/'):
    """
    Create a Flask app that wraps a click command. (Call once)

    :param module: the module that contains the click command, needed to get the path to the script.
    :param command: The actual click root command, needed to be able to read the command tree and arguments
                    in order to generate the index page and the html forms
    :param root: the root url path to server click-web under.
    usage:

        from click_web import create_click_web_app

        import a_click_script

        app = create_click_web_app(a_click_script, a_click_script.a_group_or_command)

    """
    global logger
    root = root.rstrip('/')
    app = Flask(__name__, static_url_path=root + '/static')
    app.config['APPLICATION_ROOT'] = root
    app.config['OUTPUT_FOLDER'] = str(_get_output_folder())

    _register(app, module, command)

    # add the "do" extension needed by our jinja templates
    app.jinja_env.add_extension('jinja2.ext.do')

    app.add_url_rule(root + '/', 'index', click_web.resources.index.index)
    app.add_url_rule(root + '/<path:command_path>', 'command', click_web.resources.cmd_form.get_form_for)

    executor = click_web.resources.cmd_exec.Executor(app)
    app.add_url_rule(root + '/<path:command_path>', 'command_execute', executor.exec,
                     methods=['POST'])

    app.logger.info(f"OUTPUT_FOLDER: {app.config['OUTPUT_FOLDER']}")
    results_blueprint = Blueprint('results',
                                  __name__,
                                  static_url_path=root + '/static/results',
                                  static_folder=app.config['OUTPUT_FOLDER']
                                  )
    app.register_blueprint(results_blueprint)

    logger = app.logger

    return app


def _register(app, module, command: click.BaseCommand):
    """

    :param module: the module that contains the command, needed to get the path to the script.
    :param command: The actual click root command, needed to be able to read the command tree and arguments
                    in order to generate the index page and the html forms
    """
    # The full path to the click script file to execute.
    app.config['CLICK_WEB_SCRIPT_FILE'] = str(Path(module.__file__).absolute())
    # The click root command to serve
    app.config['CLICK_WEB_ROOT_CMD'] = command
