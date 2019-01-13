import click
import time

DEBUG = False
@click.group()
# TODO: support options on parent group
@click.option("--debug/--no-debug", help='set debug flag')
def cli(debug):
    'A stupid script to test click-web'
    global DEBUG
    DEBUG=debug


@cli.command()
@click.option("--delay", type=float, default=0.01, required=True, help='tid mellan varje print line')
@click.argument("lines", default=10, type=int)
def printa_rader(lines, delay):
    'printa massa rader'
    if DEBUG:
        click.echo("global debug set, printing some debug output")
    click.echo(f"writing: {lines} with {delay}")
    for i in range(lines):
        click.echo("hejsan rad: {}".format(i))
        time.sleep(delay)


@cli.command()
@click.option("--email", help='the email for user')
@click.option("--nummer", type=int, help='ett nummer')
@click.argument("user", default="bode")
def commando_1(user, email, nummer=None):
    'subkommando'
    click.echo("hejsan {} du har satt och din email: {} nummer är: {}".format(user,  email, nummer))


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
def commando_2(user, debug, email):
    'subkommando'
    click.echo("hejsan {} du har satt debug till {} och din email: {}".format(user, debug, email))

if __name__ == '__main__':
    cli()
