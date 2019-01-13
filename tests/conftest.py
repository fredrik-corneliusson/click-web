import click
import pytest


@pytest.fixture(name='loaded_script_module')
def _loaded_script_module():
    import tests.script.a_script
    yield tests.script.a_script


@pytest.fixture(name='ctx')
def _ctx(cli):
    with click.Context(cli, info_name=cli, parent=None) as ctx:
        yield ctx

@pytest.fixture(name='cli')
def _click_command(loaded_script_module):
    yield loaded_script_module.cli
