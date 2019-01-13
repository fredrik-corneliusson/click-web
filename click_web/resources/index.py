from collections import OrderedDict

import click

from flask import Flask
import click_web

app = Flask(__name__)

from flask import render_template


def index():
    with click.Context(click_web.click_root_cmd, info_name=click_web.click_root_cmd.name, parent=None) as ctx:
        return render_template('show_tree.html.j2', ctx=ctx, tree=_click_to_tree(click_web.click_root_cmd))


def _click_to_tree(node: click.BaseCommand, parents=[]):
    '''
    Convert a click root command to a tree of dicts and lists
    :return: a json like tree
    '''
    res_childs = []
    if isinstance(node, click.core.Group):
        # a group, recurse for every child
        for child in node.commands.values():
            res_childs.append(_click_to_tree(child, parents[:] + [node, ]))

    res = OrderedDict()
    res['name'] = node.name
    res['help'] = node.get_short_help_str()
    path_parts = parents + [node]
    res['path'] = '/' + '/'.join(p.name for p in path_parts)
    if res_childs:
        res['childs'] = res_childs
    return res