"""
This example shows how to serve multiple click scripts at the same time under different url paths.
It uses Flask DispatcherMiddleware in order to route to each individual Flask app for each Click command and provides a
hard coded index page to reach them.
"""
from flask import Flask, render_template_string
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from click_web import create_click_web_app
from example import example_command
from example.multi_app import example_command2

# Create the main Flask app
app = Flask(__name__)


# Create the index route in the main app
@app.route('/')
def index():
    commands = [
        {'name': 'Command 1', 'path': '/command1'},
        {'name': 'Command 2', 'path': '/command2'},
    ]
    return render_template_string('''
    <!doctype html>
    <html lang="en">
    <head>
        <title>Available Commands</title>
    </head>
    <body>
        <h1>Available Commands</h1>
        <ul>
            {% for cmd in commands %}
                <li><a href="{{ cmd.path }}">{{ cmd.name }}</a></li>
            {% endfor %}
        </ul>
    </body>
    </html>
    ''', commands=commands)


# Create individual Flask apps for each Click command
app1 = create_click_web_app(example_command, example_command.cli)
app2 = create_click_web_app(example_command2, example_command2.cli)

# Wrap the original app.wsgi_app with DispatcherMiddleware
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/command1': app1,
    '/command2': app2
})

if __name__ == '__main__':
    app.run()
