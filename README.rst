click-web
=========

Serve click scripts over the web with minimal effort.

*Caution*: No security (login etc.), do not serve scripts publicly.

usage
-----

Take an existing click script, like this one:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``test_command.py``

::

   import click
   import time

   @click.group()
   def cli():
       'A stupid script to test click-web'
       pass

   @cli.command()
   @click.option("--delay", type=float, default=0.01, help='delay for every line print')
   @click.argument("lines", default=10, type=int)
   def print_rows(lines, delay):
       'Prints lines with a delay'
       click.echo(f"writing: {lines} with {delay}")
       for i in range(lines):
           click.echo("hejsan rad: {}".format(i))
           time.sleep(delay)

   if __name__ == '__main__':
       cli()

Create a minimal script to run with flask
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``app.py``

::

   from click_web import create_click_web_app
   from example import example_command

   app = create_click_web_app(example_command, example_command.cli)

Running example app:
~~~~~~~~~~~~~~~~~~~~

In Bash:

::

   export FLASK_ENV=development
   export FLASK_APP=app.py
   flask run

Unsupported click features
==========================

It has only been tested with basic click features, and most advanced
features will probably not work.

-  Variadic Arguments (will need some JS on client side)
-  Promts (probably never will)
-  Custom ParamTypes (depending on implementation)

TODO
====

-  Abort started/running processes.