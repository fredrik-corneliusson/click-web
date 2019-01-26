import click
import time

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
        click.echo(f"{message} rad: {i}")
        time.sleep(delay)


@cli.command()
@click.option("--email", help='the email for user')
@click.option("--number", type=int, help='a number')
@click.argument("user", default="bode")
def a_sub_command(user, email, number=None):
    "A sub command"
    click.echo(f"Hi {user}, your email was set to: {email} and number is: {number}")


@cli.group()
def sub():
    'A sub group'


@sub.command()
@click.option("--blubb/--no-blubb", help='set blubb flag')
@click.option("--email", help='the email for user', default='some@thing.xyz', nargs=2)
@click.argument("user", default="johnny bode")
def nargs_test(user, blubb, email):
    "Command with nargs option"
    click.echo(f"Hi {user}, blubb flag is {blubb} and emails sent in is: {email}")


@cli.group()
def sub2():
    'subgrupp'


@sub2.command()
@click.option("--debug/--no-debug", help='set debug flag')
@click.option("--email", help='the email for user')
@click.argument("user", default="bode")
def a_nested_sub_command(user, debug, email):
    "2:nd level sub command"
    click.echo(f"Hi {user}, debug set to {debug} and email: {email}")


@cli.command()
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


@cli.command()
@click.argument('input', type=click.File('rb'))
@click.argument('output', type=click.File('wb'))
def process_input_file(input: click.File, output: click.File):
    "Process file and create a download link for output file"
    if DEBUG:
        click.echo("global debug set, printing some debug output")
    while True:
        click.echo(f"Reading from {input.name}...")
        chunk = input.read(2048)
        if not chunk:
            break
        click.echo(f"Writing to {output.name}...")

        chunk = chunk.upper()
        output.write(chunk)
    click.echo({output.name})


def add_external_command(USE_MULTI_COMMAND=False):
    """
    Shows an example of how to add external click commands from other modules
    """
    global cli
    import flask.cli

    @click.group()
    def flask_cli():
        'flask cli'
        pass

    flask_cli.add_command(flask.cli.run_command)
    if USE_MULTI_COMMAND:
        # Using CommandCollection will work but you will loose the group level options
        cli = click.CommandCollection(name='A multi command example', sources=[cli, flask_cli])
    else:
        # adding command or group to existing hierarchy
        cli.add_command(flask_cli)


add_external_command(False)

if __name__ == '__main__':
    cli()
