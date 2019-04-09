from click_web import create_click_web_app
from example import example_command
from pathlib import Path

from flask import Blueprint

custom_folder = (Path(__file__).parent / 'custom').absolute()
custom_folder_blueprint = Blueprint(
    'custom',
    __name__,
    static_url_path='/custom',
    static_folder=custom_folder)

app = create_click_web_app(example_command, example_command.cli)

app.config['CUSTOM_CSS'] = (custom_folder / 'custom.css').exists()
app.register_blueprint(custom_folder_blueprint)
