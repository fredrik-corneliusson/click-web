from pathlib import Path

import pytest

import click_web
import click_web.utils


def test_register(cli, loaded_script_module):
    click_web.register(loaded_script_module, cli)

    assert click_web.script_file == str(Path(loaded_script_module.__file__).absolute())
    assert click_web.click_root_cmd == cli


@pytest.mark.parametrize('command_path, command_name, command_help', [
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
