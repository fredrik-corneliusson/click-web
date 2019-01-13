import pprint
from pathlib import Path

import click
import pytest

import click_web
import click_web.utils
from click_web.resources.command import _generate_form_data


def test_register(cli, loaded_script_module):
    click_web.register(loaded_script_module, cli)

    assert click_web.script_file == str(Path(loaded_script_module.__file__).absolute())
    assert click_web.click_root_cmd == cli


def test_render_command_form(cli, loaded_script_module):
    cmd_path = 'cli/some-command'
    click_web.register(loaded_script_module, cli)
    ctx_and_commands = click_web.utils.get_commands_by_path(cmd_path)
    res = _generate_form_data(ctx_and_commands)
    assert len(res) == 2
    assert len(res[0]['fields']) == 1
    assert len(res[1]['fields']) == 2
    pprint.pprint(res)


@pytest.mark.parametrize(
    'command_path, command_name, command_help',
    [
        ('cli/some-command', 'some-command', 'Help text'),
        ('cli/sub-group', 'sub-group', 'a sub group'),
        ('cli/sub-group/a-sub-group-command', 'a-sub-group-command', 'Help for sub_group.sub_group_command '),
    ])
def test_command_path(cli,
                      loaded_script_module,
                      command_path,
                      command_name,
                      command_help):
    click_web.register(loaded_script_module, cli)
    ctx, command = click_web.utils.get_commands_by_path(command_path)[-1]

    assert command.name == command_name
    assert command.help == command_help


@pytest.mark.parametrize(
    'param, expected',
    [
        (click.Argument(["an_argument", ]),
         {'checked': '',
          'help': '',
          'human_readable_name': 'AN_ARGUMENT',
          'name': 'an_argument',
          'nargs': 1,
          'param': 'argument',
          'type': 'text',
          'value': ''}),
        (click.Argument(["an_argument", ], nargs=2),
         {'checked': '',
          'help': '',
          'human_readable_name': 'AN_ARGUMENT',
          'name': 'an_argument',
          'nargs': 2,
          'param': 'argument',
          'type': 'text',
          'value': ''}),
        (click.Option(["--an_option", ]),
         {'checked': '',
          'desc': None,
          'help': ('--an_option TEXT', ''),
          'human_readable_name': 'an_option',
          'name': '--an_option',
          'nargs': 1,
          'param': 'option',
          'type': 'text',
          'value': ''}),
        (click.Option(["--an_option", ], nargs=2),
         {'checked': '',
          'desc': None,
          'help': ('--an_option TEXT...', ''),
          'human_readable_name': 'an_option',
          'name': '--an_option',
          'nargs': 2,
          'param': 'option',
          'type': 'text',
          'value': ''}),
        (click.Option(["--flag/--no-flag", ], default=True, help='help'),
         {'checked': 'checked="checked"',
          'desc': 'help',
          'help': ('--flag / --no-flag', 'help'),
          'human_readable_name': 'flag',
          'name': '--flag',
          'nargs': 1,
          'param': 'option',
          'type': 'checkbox',
          'value': True}),
    ])
def test_get_input_field(ctx, cli, param, expected):
    res = click_web.utils.get_input_field(ctx, param)
    pprint.pprint(res)
    assert res == expected
