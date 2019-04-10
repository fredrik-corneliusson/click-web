from pathlib import Path

from flask import Blueprint

from click_web import create_click_web_app
from example import example_command

# create app as normal
app = create_click_web_app(example_command, example_command.cli)

# Expect any custom folder to be located in same folder as this script
custom_folder = (Path(__file__).parent / 'custom').absolute()
# Make custom folder reachable by "custom/static" url path (via a Flask blueprint)
custom_folder_blueprint = Blueprint('custom', __name__,
                                    static_url_path='/custom',
                                    static_folder=custom_folder)
app.register_blueprint(custom_folder_blueprint)

# Set CUSTOM_CSS in flask config so the click-web will use it.
app.config['CUSTOM_CSS'] = 'custom.css'
