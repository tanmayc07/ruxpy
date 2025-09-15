import click

@click.group()
@click.version_option(version="0.1.0")
def main():
    """Ruxpy - A hybrid Rust/Python version control system"""
    pass

@main.command()
@click.argument('path', default='.')
def init(path):
    """Initialize a new ruxpy repository"""
    click.echo(f"Initializing ruxpy repository in {path}...")
    
    # Test Rust integration
    try:
        from .ruxpy import sum_as_string
        result = sum_as_string(10, 20)
        click.echo(f"✓ Rust core is working: {result}")
    except ImportError as e:
        click.echo(f"⚠ Rust core not available: {e}")
    
    click.echo("✓ Repository initialized!")

@main.command()
@click.argument('files', nargs=-1)
def add(files):
    """Add files to the staging area"""
    if not files:
        click.echo("Usage: ruxpy add <file>...")
        return
    
    for file in files:
        click.echo(f"Adding {file}")

@main.command()
def status():
    """Show the repository status"""
    click.echo("On branch main")
    click.echo("nothing to commit, working tree clean")

if __name__ == '__main__':
    main()