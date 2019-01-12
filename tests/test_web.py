from pathlib import Path
import click_web


def test_register(cli, loaded_script_module):
    click_web.register(loaded_script_module, cli)

    assert click_web.script_file == str(Path(loaded_script_module.__file__).absolute())
    assert click_web.click_root_cmd == cli
