from typing import List, Tuple

import click
from flask import render_template, abort

from click_web import exceptions
from click_web.exceptions import CommandNotFound
from click_web.utils import get_commands_by_path

form_command_index_separator = '.'


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
    for command_index, (ctx, command) in enumerate(ctx_and_commands):
        # force help option off, no need in web.
        command.add_help_option = False

        input_fields = [_get_input_field(ctx, param, command_index)
                        for param in command.get_params(ctx)]
        levels.append({'command': command, 'fields': input_fields})

    return levels


def _get_input_field(ctx: click.Context, param: click.Parameter, command_index) -> dict:
    """
    Convert a click.Parameter into a dict structure describing a html form option
    """
    # TODO: File and directory uploads (folders can be uploaded zipped and then unzipped in safe temp dir).
    field = {}
    field['param'] = param.param_type_name
    field.update(_param_type_to_input_type(param))
    if param.param_type_name == 'option':
        name = '--{}'.format(param.name)
        field['value'] = param.default if param.default else ''
        field['checked'] = 'checked="checked"' if param.default else ''
        field['desc'] = param.help
        field['help'] = param.get_help_record(ctx)
    elif param.param_type_name == 'argument':
        name = param.name
        field['value'] = ''
        field['checked'] = ''
        field['help'] = ''

    # in order for form to be have arguments for sub commands we need to add the
    # index of the command the argument belongs to
    field['name'] = f'{command_index}.{name}'
    field['required'] = param.required

    if param.nargs < 0:
        raise exceptions.ClickWebException("Parameters with unlimited nargs not supportet at the moment.")
    field['nargs'] = param.nargs
    field['human_readable_name'] = param.human_readable_name
    return field


def _param_type_to_input_type(param):
    """
    take a param and return a dict with html form type attrs
    :param param:
    :return:
    """
    type_attrs = {}
    if param.param_type_name == 'option' and param.is_bool_flag:
        type_attrs['type'] = 'checkbox'
    elif param.type == click.INT:
        type_attrs['type'] = 'number'
        type_attrs['step'] = '1'
    elif param.type == click.FLOAT:
        type_attrs['type'] = 'number'
        type_attrs['step'] = 'any'
    else:
        type_attrs['type'] = 'text'
    return type_attrs