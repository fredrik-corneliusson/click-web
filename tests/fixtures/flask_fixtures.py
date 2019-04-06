import pytest

from click_web import create_click_web_app

_app = None


@pytest.fixture
def app(loaded_script_module, cli):
    global _app
    if _app is None:
        _app = create_click_web_app(loaded_script_module, cli)
    with _app.app_context():
        yield _app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client
