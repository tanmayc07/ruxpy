import click


def echo_error(msg):
    click.echo(f"{click.style('[ERROR]', fg='red')} {msg}")


def echo_warning(msg):
    click.echo(f"{click.style('[WARNING]', fg='yellow')} {msg}")


def echo_info(msg):
    click.echo(f"{click.style('[INFO]', fg='yellow')} {msg}")


def echo_success(msg):
    click.echo(f"{click.style('[SUCCESS]', fg='green')} {msg}")
