import os
import click
from ruxpy import Config, get_paths, Messages


@click.command()
@click.option("-su", "--set-username", help="Set username in the config")
@click.option("-se", "--set-email", help="Set email in the config")
@click.option("-sn", "--set-name", help="Set name in the config")
def config(set_username, set_email, set_name):
    base_path = os.getcwd()
    config_path = get_paths(base_path)["config"]

    config = Config.read_config(config_path)
    if config is None:
        Messages.echo_error("Spacedock is not initialized. No .dock/ found.")
        return

    if set_username:
        config["username"] = set_username
    if set_email:
        config["email"] = set_email
    if set_name:
        config["name"] = set_name

    Config.write_config(config_path, config)
    Messages.echo_success("Config updated successfully!")
