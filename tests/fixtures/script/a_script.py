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


@cli.command()
@click.option("--unicode-msg", type=click.Choice(['Åäö']), default='Åäö', required=True,
              help='Message with unicide chars to print.')
def unicode_test(unicode_msg):
    "Just print unicode message"
    click.echo(f"This {unicode_msg} should be Åäö")


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
    click.echo(f"Ran command with option: {an_option} argument {an_argument}")


@cli.command()
@click.option("--an-option", type=str, nargs=2, help='help for an option')
def command_with_nargs_option(an_option):
    'Help text'
    click.echo(f"Ran command with option: {an_option}")


@cli.command()
@click.option("--flag", is_flag=True, default=False, help='help for flag')
def command_with_flag_without_off_option(flag):
    'Help text'
    click.echo(f"Ran command with flag {flag}")


@cli.command()
@click.option("--flag/--no-flag", default=True, help='help for flag')
def command_with_default_on_flag_option(flag):
    'Help text'
    click.echo(f"Ran command with flag {flag}")


@cli.command()
@click.argument('folder', type=click.Path(exists=True))
def command_with_input_folder(folder):
    click.echo(click.format_filename(folder))


@cli.command()
@click.argument('folder', type=click.Path())
def command_with_output_folder(folder):
    click.echo(click.format_filename(folder))


@cli.command()
@click.option('--outfile', type=click.File('w'))
def command_with_output_file(outfile):
    click.echo(outfile)
    if outfile:
        outfile.write("test")


class ACustomParamType(click.ParamType):
    """Just a stupid custom param type"""
    name = 'my_custom_type'

    def convert(self, value, param, ctx):
        if value.lower() == 'spamspam':
            return value
        else:
            self.fail(f'{value} is not valid', param, ctx)


@cli.command()
@click.argument('custom', type=ACustomParamType())
def command_with_custom_type(custom):
    "Argument must be set to 'spamspam' to be valid"
    click.echo(f'{custom} is valid.')


@cli.command()
@click.argument("users", nargs=-1)
def command_with_variadic_args(users):
    "Command with variadic args"
    for i, user in enumerate(users):
        click.echo(f"Hi {user}, you are number {i + 1}")


if __name__ == '__main__':
    cli()
