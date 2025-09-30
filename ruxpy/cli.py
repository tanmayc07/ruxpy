import click
from .starlog import starlog
from .config import config
from .start import start
from .scan import scan
from .beam import beam


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Ruxpy - A hybrid Rust/Python version control system"""
    pass


main.add_command(starlog)
main.add_command(config)
main.add_command(start)
main.add_command(scan)
main.add_command(beam)


if __name__ == "__main__":
    main()
