import click
import time

@click.group()
def cli():
    'A stupid script to test click-web'
    pass

@cli.command()
@click.option("--delay", type=float, default=0.01, help='tid mellan varje print line')
@click.argument("lines", default=10, type=int)
def printa_rader(lines, delay):
    'printa massa rader'
    click.echo(f"writing: {lines} with {delay}")
    for i in range(lines):
        click.echo("hejsan rad: {}".format(i))
        time.sleep(delay)


@cli.command()
@click.option("--debug/--no-debug", help='set debug flag')
@click.option("--email", help='the email for user')
@click.option("--nummer", type=int, help='ett nummer')
@click.argument("user", default="bode")
def commando_1(user, debug, email, nummer=None):
    'subkommando'
    click.echo("hejsan {} du har satt debug till {} och din email: {} nummer är: {}".format(user, debug, email, nummer))


@cli.group()
def sub():
    'subgrupp'

@sub.command()
@click.option("--debug/--no-debug", help='set debug flag')
@click.option("--email", help='the email for user', default='some@thing.xyz', nargs=2)
@click.argument("user", default="bode")
def commando_2(user, debug, email):
    'subkommando med nargs'
    click.echo("hejsan {} du har satt debug till {} och din email: {}".format(user, debug, email))

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
