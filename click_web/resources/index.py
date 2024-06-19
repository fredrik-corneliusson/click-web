from collections import OrderedDict
from typing import Union

import click
from flask import render_template

import click_web


def index():
    with click.Context(click_web.click_root_cmd, info_name=click_web.click_root_cmd.name, parent=None) as ctx:
        template_name = click_web._flask_app.config.get("CLICK_WEB_MAIN_TEMPLATE", "show_tree.html.j2")
        return render_template(template_name, ctx=ctx, tree=_click_to_tree(ctx, click_web.click_root_cmd))


def _click_to_tree(ctx: click.Context, node: Union[click.Command, click.MultiCommand], ancestors: list = None):
    """
    Convert a click root command to a tree of dicts and lists
    :return: a json like tree
    """
    if ancestors is None:
        ancestors = []
    res_childs = []
    res = OrderedDict()
    res['is_group'] = isinstance(node, click.core.MultiCommand)
    if res['is_group']:
        # a group, recurse for every child
        children = [node.get_command(ctx, key) for key in node.list_commands(ctx)]
        # Sort so commands comes before groups
        children = sorted(children, key=lambda c: isinstance(c, click.core.MultiCommand))
        for child in children:
            res_childs.append(_click_to_tree(ctx, child, ancestors[:] + [node, ]))

    res['name'] = node.name

    # Do not include any preformatted block (\b) for the short help.
    res['short_help'] = node.get_short_help_str().split('\b')[0]
    res['help'] = node.help
    path_parts = ancestors + [node]
    root = click_web._flask_app.config['APPLICATION_ROOT'].rstrip('/')
    res['path'] = root + '/' + '/'.join(p.name for p in path_parts)
    if res_childs:
        res['childs'] = res_childs
    return res
