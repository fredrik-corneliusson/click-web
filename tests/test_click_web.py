import pprint
from pathlib import Path

import click
import pytest

import click_web
import click_web.utils


def test_register(cli, loaded_script_module):
    click_web.register(loaded_script_module, cli)

    assert click_web.script_file == str(Path(loaded_script_module.__file__).absolute())
    assert click_web.click_root_cmd == cli


@pytest.mark.parametrize(
    'command_path, command_name, command_help',
    [
        ('some-command', 'some-command', 'Help text'),
        ('sub-group', 'sub-group', 'a sub group'),
        ('sub-group/a-sub-group-command', 'a-sub-group-command', 'Help for sub_group.sub_group_command '),
    ])
def test_command_path(cli,
                      loaded_script_module,
                      command_path,
                      command_name,
                      command_help):
    click_web.register(loaded_script_module, cli)
    ctx, command = click_web.utils.get_command_by_path(command_path)

    assert command.name == command_name
    assert command.help == command_help


@pytest.mark.parametrize(
    'param, expected',
    [
        (click.Argument(["an_argument", ]),
         {'checked': '',
          'human_readable_name': 'AN_ARGUMENT',
          'name': 'an_argument',
          'nargs': 1,
          'type': 'text',
          'value': ''}),
        (click.Argument(["an_argument", ], nargs=2),
         {'checked': '',
          'human_readable_name': 'AN_ARGUMENT',
          'name': 'an_argument',
          'nargs': 2,
          'type': 'text',
          'value': ''}),
        (click.Option(["--an_option", ]),
         {'checked': '',
          'desc': None,
          'human_readable_name': 'an_option',
          'name': '--an_option',
          'nargs': 1,
          'type': 'text',
          'value': ''}),
        (click.Option(["--an_option", ], nargs=2),
         {'checked': '',
          'desc': None,
          'human_readable_name': 'an_option',
          'name': '--an_option',
          'nargs': 2,
          'type': 'text',
          'value': ''}),
        (click.Option(["--flag/--no-flag", ], default=True, help='help'),
         {'checked': 'checked="checked"',
          'desc': 'help',
          'human_readable_name': 'flag',
          'name': '--flag',
          'nargs': 1,
          'type': 'checkbox',
          'value': True}),
    ])
def test_get_input_field(cli, param, expected):
    res = click_web.utils.get_input_field(param)
    pprint.pprint(res)
    assert res == expected

'''
@click.command()
@click.option('--pos', nargs=2, type=float)
def findme(pos):
    click.echo('%s / %s' % pos)
And on the command line:

$ findme --pos 2.0 3.0
2.0 / 3.0
'''