import click

from flask import Flask, abort
import click_web
from click_web.exceptions import CommandNotFound

from .utils import get_command_by_path
from .web_utils import render_command_form, click_to_tree

app = Flask(__name__)

from flask import render_template


def index():
    with click.Context(click_web.click_root_cmd, info_name=click_web.click_root_cmd.name, parent=None) as ctx:
        return render_template('show_tree.html.j2', ctx=ctx, tree=click_to_tree(click_web.click_root_cmd))


def get_form_for(command_path: str):
    # skip the first path part as it's the roots name (cli)
    try:
        ctx, command = get_command_by_path(command_path)
    except CommandNotFound as err:
        return abort(404, str(err))

    return render_command_form(ctx, command, command_path=command_path)
