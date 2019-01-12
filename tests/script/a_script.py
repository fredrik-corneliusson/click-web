import click


@click.group()
def cli():
    'the root command'
    pass


@cli.command()
@click.option("--an_option", type=str, default="option_value", help='help for an option')
@click.argument("an_argument", default=10, type=int)
def some_command(an_argument, an_option):
    'Help text'
    click.echo(f"Run command argument: {an_argument} option {an_option}")


if __name__ == '__main__':
    cli()
