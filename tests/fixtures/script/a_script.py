import click


@click.group()
@click.option("--debug/--no-debug", help='Global debug flag')
def cli(debug):
    'the root command'
    pass


@cli.command()
def simple_no_params_command():
    'Help text'
    click.echo("Simpel noparams command called")


@cli.group()
def sub_group():
    'a sub group'
    pass


@sub_group.command()
def a_sub_group_command():
    'Help for sub_group.sub_group_command '
    click.echo("Sub group command called")


@cli.command()
@click.option("--an-option", type=str, default="option_value", help='help for an option')
@click.argument("an-argument", default=10, type=int)
def command_with_option_and_argument(an_argument, an_option):
    'Help text'
    click.echo("Ran command with option: {} argument {}".format(an_option, an_argument))


@cli.command()
@click.argument('folder', type=click.Path(exists=True))
def command_with_input_folder(folder):
    click.echo(click.format_filename(folder))


@cli.command()
@click.argument('folder', type=click.Path())
def command_with_output_folder(folder):
    click.echo(click.format_filename(folder))


if __name__ == '__main__':
    cli()
