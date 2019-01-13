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

    return _render_command_form(ctx_and_commands, command_path=command_path)


def _render_command_form(ctx_and_commands: List[Tuple[click.Context, click.Command]],
                         command_path: str):
    ctx, command = ctx_and_commands[-1]
    if command:
        # force help option off, no need in web.
        command.add_help_option = False

        fields = [get_input_field(ctx, p) for p in command.get_params(ctx)]
        return render_template('command_form.html.j2',
                               ctx=ctx,
                               command=command,
                               fields=fields,
                               command_path=command_path)
    else:
        return abort(404, 'command not found. Must be one of {}'
                     .format(click_web.click_root_cmd.list_commands(ctx)))
