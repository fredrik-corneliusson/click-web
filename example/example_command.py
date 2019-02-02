from datetime import datetime
from pathlib import Path

import click
import time

from click_web.web_click_types import EMAIL_TYPE

DEBUG = False


@click.group()
@click.option("--debug/--no-debug", help='set debug flag')
def cli(debug):
    'An example click script to test click-web'
    global DEBUG
    DEBUG = debug


@cli.command()
@click.option("--delay", type=float, default=0.01, required=True, help='delay between each print line')
@click.option("--message", type=click.Choice(['Red', 'Blue']), default='Blue', required=True,
              help='Message to print.')
@click.argument("lines", default=10, type=int)
def print_lines(lines, message, delay):
    "Just print lines with delay (demonstrates the output streaming to browser)"
    if DEBUG:
        click.echo("global debug set, printing some debug output")
    click.echo(f"writing: {lines} lines with delay {delay}s")
    for i in range(lines):
        click.echo(f"{message} row: {i}")
        time.sleep(delay)


@cli.command()
@click.option("--email", type=EMAIL_TYPE, help='the email for user')
@click.option("--number", type=int, help='a number')
@click.argument("user", default="bode")
def simple_command(user, email, number=None):
    "Command with text and number inputs"
    click.echo(f"Hi {user}, your email was set to: {email} and number is: {number}")


@cli.command()
@click.option("--someopt", help='the email for user')
@click.argument("user")
def simple_command_missing_default_value(user, someopt=None):
    "Command with text and number inputs"
    click.echo(f"Hi {user}, option was set to: {someopt}")


@cli.group()
def sub():
    'A sub group'


@sub.command()
@click.option("--blubb/--no-blubb", help='set blubb flag')
@click.option("--email", type=EMAIL_TYPE, help='the email for user', default='some@thing.xyz', nargs=2)
@click.argument("user", default="johnny bode")
def nargs_test(user, blubb, email):
    "Command with nargs option"
    click.echo(f"Hi {user}, blubb flag is {blubb} and emails sent in is: {email}")


@sub.group()
def sub2():
    'subgrupp'


@sub2.command()
@click.option("--debug/--no-debug", help='set debug flag')
@click.option("--email", help='the email for user')
@click.argument("user", default="bode")
def a_nested_sub_command(user, debug, email):
    "2:nd level sub command"
    click.echo(f"Hi {user}, global debug is {DEBUG} and local debug is {debug} and email: {email}")


@cli.group()
def file_handling():
    "Commands to test file and folder handling"


@file_handling.command()
@click.option('--input', type=click.File('rb'))
def process_optional_file(input: click.File):
    "Process a file given as option"
    if input is None:
        click.echo("no input file given")
    while True:
        click.echo(f"Reading from {input.name}...")
        chunk = input.read(2048)
        if not chunk:
            break
        click.echo(chunk.upper())


@file_handling.command()
@click.option('--output', type=click.File('w'))
def process_optional_output_file(output: click.File):
    "Process an output file given as option"
    if output is None:
        click.echo("No input file given")
    else:
        output.write('Some text written to optional output file')


@file_handling.command()
@click.argument('input', type=click.File('rb'))
@click.argument('output', type=click.File('wb'))
def process_input_file(input: click.File, output: click.File):
    "Process file and create a download link for output file"
    if DEBUG:
        click.echo("Global debug set, printing some debug output")
    while True:
        click.echo(f"Reading from {input.name}...")
        chunk = input.read(2048)
        if not chunk:
            break
        click.echo(f"Writing to {output.name}...")

        chunk = chunk.upper()
        output.write(chunk)
    click.echo({output.name})


@file_handling.command()
@click.argument('folder', type=click.Path(exists=True))
def process_input_folder(folder):
    "Process a folder"
    click.echo(click.format_filename(folder))
    all_files = Path(folder).rglob("*")
    click.echo('\n'.join(str(f) for f in all_files))


@file_handling.command()
@click.argument('folder', type=click.Path())
def process_output_folder(folder):
    "Produce output in a folder"
    click.echo(click.format_filename(folder))
    out_file = (Path(folder) / 'out_file.txt')
    with open(out_file, 'w') as out:
        out.write(f"This was written by process_output_folder {datetime.now()}")


@file_handling.command()
@click.argument('input_folder', type=click.Path(exists=True))
@click.argument('out_folder', type=click.Path())
def process_input_output_folder(input_folder, out_folder):
    "Process a input folder and produce output folder"
    click.echo(click.format_filename(input_folder))
    all_files = Path(input_folder).rglob("*")
    click.echo('\n'.join(str(f) for f in all_files))
    out_file = (Path(out_folder) / 'out_file.txt')
    with open(out_file, 'w') as out:
        out.write(f"This was written by process_output_folder {datetime.now()}")


def add_external_command(USE_MULTI_COMMAND=False):
    """
    Shows an example of how to add external click commands from other modules
    """
    global cli
    import flask.cli

    @cli.group()
    def test_external():
        'Shows an example of how to add external click commands from other modules'
        pass

    @test_external.group()
    def flask_cli():
        'flask cli'
        pass

    flask_cli.add_command(flask.cli.run_command)
    if USE_MULTI_COMMAND:
        # Using CommandCollection will work but you will loose the group level options
        cli = click.CommandCollection(name='A multi command example', sources=[cli, flask_cli])


add_external_command(False)

if __name__ == '__main__':
    cli()
