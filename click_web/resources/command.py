from typing import List, Tuple

import click
from flask import render_template, abort

import click_web
from click_web import exceptions
from click_web.exceptions import CommandNotFound

separator = '.'


def get_form_for(command_path: str):
    try:
        ctx_and_commands = _get_commands_by_path(command_path)
    except CommandNotFound as err:
        return abort(404, str(err))

    levels = _generate_form_data(ctx_and_commands)
    return render_template('command_form.html.j2',
                           levels=levels,
                           command=levels[-1]['command'],
                           command_path=command_path)


def _get_commands_by_path(command_path: str) -> Tuple[click.Context, click.Command]:
    """
    Take a (slash separated) string and generate (context, command) for each level.
    :param command_path: "some_group/a_command"
    :return: Return a list from root to leaf commands. each element is (Click.Context, Click.Command)
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


def _generate_form_data(ctx_and_commands: List[Tuple[click.Context, click.Command]]):
    """
    Construct a list of contexts and commands generate a python data structure for rendering jinja form
    :return: a list of dicts
    """
    levels = []
    for command_index, (ctx, command) in enumerate(ctx_and_commands):
        # force help option off, no need in web.
        command.add_help_option = False

        input_fields = [_get_input_field(ctx, param, command_index, param_index)
                        for param_index, param in enumerate(command.get_params(ctx))]
        levels.append({'command': command, 'fields': input_fields})

    return levels


def _get_input_field(ctx: click.Context, param: click.Parameter, command_index, param_index) -> dict:
    """
    Convert a click.Parameter into a dict structure describing a html form option
    """
    # TODO: File and directory uploads (folders can be uploaded zipped and then unzipped in safe temp dir).
    # TODO: if file is only output (no 'w' in mode) generate a hidden input field

    field = {}
    field['param'] = param.param_type_name
    field.update(_param_type_to_input_type(param))
    if param.param_type_name == 'option':
        name = '--{}'.format(_to_cmd_line_name(param.name))
        field['value'] = param.default if param.default else ''
        field['checked'] = 'checked="checked"' if param.default else ''
        field['desc'] = param.help
        field['help'] = param.get_help_record(ctx)
    elif param.param_type_name == 'argument':
        name = _to_cmd_line_name(param.name)
        field['value'] = param.default
        field['checked'] = ''
        field['help'] = ''

    field['name'] = _build_name(command_index, param_index, param, name)
    field['required'] = param.required

    if param.nargs < 0:
        raise exceptions.ClickWebException("Parameters with unlimited nargs not supportet at the moment.")
    field['nargs'] = param.nargs
    field['human_readable_name'] = param.human_readable_name.replace('_', ' ')
    return field


def _to_cmd_line_name(name: str) -> str:
    return name.replace('_', '-')


def _build_name(command_index: int, param_index:int, param: click.Parameter, name: str):
    """
    Construct a name to use for field in form that have information about
    what sub-command it belongs order index (for later sorting) and type of parameter.
    """
    # get the type of param to encode the in the name
    if param.param_type_name == 'option':
        param_type = 'flag' if param.is_bool_flag else 'option'
    else:
        param_type = param.param_type_name

    click_type = _param_type_to_input_type(param)['click_type']

    # in order for form to be have arguments for sub commands we need to add the
    # index of the command the argument belongs to
    return separator.join(str(p) for p in (command_index, param_index, param_type, click_type, name))


def _param_type_to_input_type(param: click.Parameter):
    """
    take a param and return a dict with html form type attrs
    :param param:
    :return:
    """
    type_attrs = {}
    if isinstance(param.type, click.Choice):
        type_attrs['type'] = 'option'
        type_attrs['options'] = param.type.choices
        type_attrs['click_type'] = 'choice'
    elif param.param_type_name == 'option' and param.is_bool_flag:
        type_attrs['type'] = 'checkbox'
        type_attrs['click_type'] = 'bool_flag'
    elif isinstance(param.type, click.types.IntParamType):
        type_attrs['type'] = 'number'
        type_attrs['step'] = '1'
        type_attrs['click_type'] = 'int'
    elif isinstance(param.type, click.types.FloatParamType):
        type_attrs['type'] = 'number'
        type_attrs['step'] = 'any'
        type_attrs['click_type'] = 'float'
    elif isinstance(param.type, click.File):
        type_attrs['type'] = 'file'
        type_attrs['click_type'] = f'file[{param.type.mode}]'
    else:
        type_attrs['type'] = 'text'
        type_attrs['click_type'] = 'text'
    return type_attrs
