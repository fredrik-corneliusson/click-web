import click
from flask import render_template, abort
import click_web
from click_web.exceptions import CommandNotFound
from click_web.utils import get_input_field, get_command_by_path


def render_command_form(ctx, command: click.Command, command_path):
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


def get_form_for(command_path: str):
    # skip the first path part as it's the roots name (cli)
    try:
        ctx, command = get_command_by_path(command_path)
    except CommandNotFound as err:
        return abort(404, str(err))

    return render_command_form(ctx, command, command_path=command_path)
