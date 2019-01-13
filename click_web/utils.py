from typing import Tuple

import click
import click_web

from click_web.exceptions import CommandNotFound


def get_commands_by_path(command_path: str) -> Tuple[click.Context, click.Command]:
    """
    Take a (slash separated) string and generate (context, command) for each level.
    :param command_path: "some_group/a_command"
    :return: Return a list from root to leaf comand. each element is (Click.Context, Click.Command)
    """
    command_path_items = command_path.split('/')
    command_name, *command_path_items = command_path_items
    command = click_web.click_root_cmd
    if command.name != command_name:
        raise CommandNotFound('Failed to find root command {}. There is a root commande named:{}'
                              .format(command_name, command.name))
    result = []
    with click.Context(command, info_name=command, parent=None) as ctx:
        result.append((ctx, command))
        # dig down the path parts to find the leaf command
        parent_command = command
        for command_name in command_path_items:
            command = parent_command.get_command(ctx, command_name)
            if command:
                # create sub context for command
                ctx = click.Context(command, info_name=command, parent=ctx)
                parent_command = command
            else:
                raise CommandNotFound('Failed to find command for path "{}". Command "{}" not found. Must be one of {}'
                                      .format(command_path, command_name, parent_command.list_commands(ctx)))
            result.append((ctx, command))
    return result
