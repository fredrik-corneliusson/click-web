import click
import time

DEBUG = False


@click.group()
@click.option("--debug/--no-debug", help='set debug flag')
def cli(debug):
    'A stupid script to test click-web'
    global DEBUG
    DEBUG = debug


@cli.command()
@click.option('--input', type=click.File('rb'))
def process_file(input: click.File):
    'Process file'
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
def process_files(input: click.File, output: click.File):
    'Process files'
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


@cli.command()
@click.option("--delay", type=float, default=0.01, required=True, help='tid mellan varje print line')
@click.option("--message", type=click.Choice(['Hej', 'Hopp']), default='Hej', required=True,
              help='Meddelande att skriva ut.')
@click.argument("lines", default=10, type=int)
def printa_rader(lines, message, delay):
    'printa massa rader'
    if DEBUG:
        click.echo("global debug set, printing some debug output")
    click.echo(f"writing: {lines} with {delay}")
    for i in range(lines):
        click.echo(f"{message} rad: {i}")
        time.sleep(delay)


@cli.command()
@click.option("--email", help='the email for user')
@click.option("--nummer", type=int, help='ett nummer')
@click.argument("user", default="bode")
def commando_1(user, email, nummer=None):
    'subkommando'
    click.echo("hejsan {} du har satt och din email: {} nummer är: {}".format(user, email, nummer))


@cli.group()
def sub():
    'subgrupp'


@sub.command()
@click.option("--blubb/--no-blubb", help='set blubb flag')
@click.option("--email", help='the email for user', default='some@thing.xyz', nargs=2)
@click.argument("user", default="bode")
def commando_2(user, blubb, email):
    'subkommando med nargs'
    click.echo("hejsan {} du har satt blubb till {} och din email: {}".format(user, blubb, email))


@cli.group()
def sub2():
    'subgrupp'


@sub2.command()
@click.option("--debug/--no-debug", help='set debug flag')
@click.option("--email", help='the email for user')
@click.argument("user", default="bode")
def commando_2_2(user, debug, email):
    'subkommando'
    click.echo("hejsan {} du har satt debug till {} och din email: {}".format(user, debug, email))


def add_external_command(USE_MULTI_COMMAND=False):
    """
    Shows an example on how to add external click commands from other modules
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
