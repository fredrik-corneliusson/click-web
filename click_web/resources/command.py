from typing import List, Tuple

import click
from flask import render_template, abort
import click_web
from click_web.exceptions import CommandNotFound
from click_web.utils import get_input_field, get_commands_by_path


def get_form_for(command_path: str):
    # skip the first path part as it's the roots name (cli)
    try:
        ctx_and_commands = get_commands_by_path(command_path)
    except CommandNotFound as err:
        return abort(404, str(err))

    levels = _generate_form_data(ctx_and_commands)
    return render_template('command_form.html.j2',
                           levels=levels,
                           command=levels[-1]['command'],
                           command_path=command_path)


def _generate_form_data(ctx_and_commands: List[Tuple[click.Context, click.Command]]):
    """
    Construct a list of contexts and commands generate a python data structure for rendering jinja form
    :return: a list of dicts
    """
    levels = []
    for ctx, command in ctx_and_commands:
        # force help option off, no need in web.
        command.add_help_option = False

        fields = [get_input_field(ctx, p) for p in command.get_params(ctx)]
        levels.append({'command':command, 'fields':fields})

    return levels
