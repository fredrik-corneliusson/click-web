from typing import Tuple

import click
import click_web

from click_web.exceptions import CommandNotFound


def get_command_by_path(command_path: str) -> Tuple[click.Context, click.Command]:
    command_path_items = command_path.split('/')
    command = click_web.click_root_cmd
    with click.Context(command, info_name=command, parent=None) as ctx:
        # dig down the path parts to find the leaf command
        parent_command = command
        for command in command_path_items:
            command = parent_command.get_command(ctx, command)
            if command:
                # create sub context for command
                ctx = click.Context(command, info_name=command, parent=ctx)
                parent_command = command
            else:
                raise CommandNotFound('command not found. Must be one of {}'.format(parent_command.list_commands(ctx)))
        return ctx, command
