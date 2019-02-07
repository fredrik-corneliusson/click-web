from click_web import create_click_web_app
from tests.fixtures.script import a_script

app = create_click_web_app(a_script, a_script.cli)
