import click
import os

@click.group()
@click.version_option(version="0.1.0")
def main():
    """Ruxpy - A hybrid Rust/Python version control system"""
    pass

@main.command('start')
@click.argument('path', default='.')
def start(path):
    """Start a new ruxpy repository"""
    
    dir_path = os.path.abspath(path)
    dock_path = os.path.join(dir_path, ".dock")
    
    if os.path.exists(dock_path):
        click.echo(f"Repository already initialized.")
        return
    else:
        os.makedirs(dock_path, exist_ok=True)
        
        # Create config.toml
        config_path = os.path.join(dock_path, "config.toml")
        with open(config_path, "w") as f:
            f.write("# config.toml\n")
            
        # Create HELM pointer file
        helm_path = os.path.join(dock_path, "HELM")
        with open(helm_path, "w") as f:
            f.write("links: links/helm/core\n")
            
        click.echo(f"Initializing ruxpy repository in {dock_path}...")

@main.command('scan')
def scan():
    """Show the repository status"""
    
    helm_path = os.path.join('.dock', 'HELM')
    if not os.path.exists(helm_path):
        click.echo("No repository found. Please run 'ruxpy start' to initialize a repository.")
        return
    with open(helm_path, "r") as f:
        content = f.read().strip()
    
    branch_name = content.split(":")[-1].strip().split("/")[-1]

    click.echo(f"On branch '-{branch_name}-'")
    click.echo("Spacedock clear, no starlog updates required.")

if __name__ == '__main__':
    main()