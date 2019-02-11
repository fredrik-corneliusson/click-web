import click
import pytest


@pytest.fixture()
def loaded_script_module():
    import tests.fixtures.script.a_script
    yield tests.fixtures.script.a_script


@pytest.fixture()
def cli(loaded_script_module):
    yield loaded_script_module.cli


@pytest.fixture()
def ctx(cli):
    with click.Context(cli, info_name=cli, parent=None) as ctx:
        yield ctx
