import click


@click.group()
@click.option("--debug/--no-debug", help='Global debug flag')
def cli(debug):
    'the root command'
    pass


@cli.command()
def simple_no_params_command():
    'Help text'
    click.echo(f"Simpel noparams command called")


@cli.group()
def sub_group():
    'a sub group'
    pass


@sub_group.command()
def a_sub_group_command():
    'Help for sub_group.sub_group_command '
    click.echo(f"Sub group command called")


@cli.command()
@click.option("--an-option", type=str, default="option_value", help='help for an option')
@click.argument("an-argument", default=10, type=int)
def command_with_option_and_argument(an_argument, an_option):
    'Help text'
    click.echo(f"Ran command with option: {an_option} argument {an_argument}")


if __name__ == '__main__':
    cli()
