# click-web
Serve click scripts over the web with minimal effort.

## usage

### Take an existing click script, like this one:
`test_command.py`
```
import click
import time

@click.group()
def cli():
    'A stupid script to test click-web'
    pass

@cli.command()
@click.option("--delay", type=float, default=0.01, help='delay for every line print')
@click.argument("lines", default=10, type=int)
def printa_rader(lines, delay):
    'Prints lines with a delay'
    click.echo(f"writing: {lines} with {delay}")
    for i in range(lines):
        click.echo("hejsan rad: {}".format(i))
        time.sleep(delay)
        
if __name__ == '__main__':
    cli()

```

### Create a minimal script to run with flask
`app.py`
```
from click_web import flask_app, register

import test_command

register(test_command, test_command.cli)
```

### Running example app:
In Bash:
```
export FLASK_ENV=development
export FLASK_APP=app.py
flask run
```
 
# TODO
* File and directory support
* Abort started/running processes.
