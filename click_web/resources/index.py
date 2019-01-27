from collections import OrderedDict

import click

import click_web

from flask import render_template


def index():
    with click.Context(click_web.click_root_cmd, info_name=click_web.click_root_cmd.name, parent=None) as ctx:
        return render_template('show_tree.html.j2', ctx=ctx, tree=_click_to_tree(ctx, click_web.click_root_cmd))


def _click_to_tree(ctx: click.Context, node: click.BaseCommand, parents=[]):
    '''
    Convert a click root command to a tree of dicts and lists
    :return: a json like tree
    '''
    res_childs = []
    res = OrderedDict()
    res['is_group'] = isinstance(node, click.core.MultiCommand)
    if res['is_group']:
        # a group, recurse for every child
        for key in node.list_commands(ctx):
            child = node.get_command(ctx, key)
            res_childs.append(_click_to_tree(ctx, child, parents[:] + [node, ]))

    res['name'] = node.name
    res['short_help'] = node.get_short_help_str()
    res['help'] = node.help
    path_parts = parents + [node]
    res['path'] = '/' + '/'.join(p.name for p in path_parts)
    if res_childs:
        res['childs'] = res_childs
    return res
