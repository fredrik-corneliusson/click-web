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


@cli.group()
def sub_group():
    'a sub group'
    pass

@sub_group.command()
def a_sub_group_command():
    'Help for sub_group.sub_group_command '
    click.echo(f"Run a_sub_group_command")

if __name__ == '__main__':
    cli()
