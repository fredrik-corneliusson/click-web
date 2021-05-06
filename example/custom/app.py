from pathlib import Path

from flask import Blueprint

from click_web import create_click_web_app
from example import example_command

# create app as normal
app = create_click_web_app(example_command, example_command.cli)

# Expect any custom static and template folder to be located in same folder as this script
# Make custom folder reachable by "custom/static" url path and add templates folder
custom_folder_blueprint = Blueprint('custom', __name__,
                                    static_url_path='/custom/static',
                                    static_folder='static',
                                    template_folder='templates')
app.register_blueprint(custom_folder_blueprint)

# Set CUSTOM_CSS in flask config so click-web will use it.
app.config['CUSTOM_CSS'] = 'custom.css'
