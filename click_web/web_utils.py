from collections import OrderedDict

import click
from flask import render_template, abort
import click_web

def click_to_tree(node: click.BaseCommand, parents=[]):
    '''
    Convert a click root command to a tree of dicts and lists
    :return: a json like tree
    '''
    res_childs = []
    if isinstance(node, click.core.Group):
        # a group, recurse for every child
        for child in node.commands.values():
            res_childs.append(click_to_tree(child, parents[:] + [node, ]))

    res = OrderedDict()
    res['name'] = node.name
    res['help'] = node.get_short_help_str()
    path_parts = parents + [node]
    res['path'] = '/' + '/'.join(p.name for p in path_parts[1:])
    if res_childs:
        res['childs'] = res_childs
    return res


def render_command_form(ctx, command, command_path):
    fields = [_get_input_field(p) for p in command.get_params(ctx)]
    if command:
        return render_template('command_form.html.j2', ctx=ctx,
                               command=command, fields=fields, command_path=command_path)
    else:
        return abort(404, 'command not found. Must be one of {}'.format(click_web.click_root_cmd.list_commands(ctx)))


def _get_input_field(param):
    # TODO: support options and arguments that can be used more than once
    #       File and directory uploads (folders can be uploaded zipped and then unzipped in safe temp dir).
    field = {}
    if param.param_type_name == 'option':
        if param.is_bool_flag:
            field['type'] = 'checkbox'
        else:
            field['type'] = 'text'
        field['value'] = param.default if param.default else ''
        field['checked'] = 'checked="checked"' if param.default else ''

        field['desc'] = param.help
        field['name'] = '--{}'.format(param.name)
    elif param.param_type_name == 'argument':
        field['type'] = 'text'
        field['value'] = ''
        field['name'] = '{}'.format(param.name)
        field['checked'] = ''
    field['human_readable_name'] = param.human_readable_name
    return field
