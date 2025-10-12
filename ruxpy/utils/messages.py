import click


class Messages:
    @staticmethod
    def echo_error(msg):
        click.echo(f"{click.style('[ERROR]', fg='red')} {msg}")

    @staticmethod
    def echo_warning(msg):
        click.echo(f"{click.style('[WARNING]', fg='yellow')} {msg}")

    @staticmethod
    def echo_info(msg):
        click.echo(f"{click.style('[INFO]', fg='yellow')} {msg}")

    @staticmethod
    def echo_success(msg):
        click.echo(f"{click.style('[SUCCESS]', fg='green')} {msg}")
