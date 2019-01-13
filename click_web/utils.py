from typing import Tuple

import click
import click_web
from click_web import exceptions

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

def get_input_field(ctx: click.Context, param: click.Parameter) -> dict:
    """
    Convert a click.Parameter into a dict structure describing a html form option
    """
    # TODO: File and directory uploads (folders can be uploaded zipped and then unzipped in safe temp dir).
    field = {}
    field['param'] = param.param_type_name
    if param.param_type_name == 'option':
        if param.is_bool_flag:
            field['type'] = 'checkbox'
        else:
            field['type'] = _param_type_to_input_type(param)
        field['value'] = param.default if param.default else ''
        field['checked'] = 'checked="checked"' if param.default else ''
        field['desc'] = param.help
        field['name'] = '--{}'.format(param.name)
        field['help'] = param.get_help_record(ctx)
    elif param.param_type_name == 'argument':
        field['type'] = _param_type_to_input_type(param)
        field['value'] = ''
        field['name'] = param.name
        field['checked'] = ''
        field['help'] = ''
    if param.nargs < 0:
        raise exceptions.ClickWebException("Parameters with unlimited nargs not supportet at the moment.")
    field['nargs'] = param.nargs
    field['human_readable_name'] = param.human_readable_name
    return field


def _param_type_to_input_type(param):
    return 'number' if param.type == click.INT else 'text'
