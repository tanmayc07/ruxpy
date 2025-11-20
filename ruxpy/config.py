import os
import click
from ruxpy import Config, get_paths, Messages
import re


@click.command()
@click.option("-l", "--list", is_flag=True, help="List the configuration values")
@click.option("-su", "--set-username", help="Set username in the config")
@click.option("-se", "--set-email", help="Set email in the config")
@click.option("-sn", "--set-name", help="Set name in the config")
def config(list, set_username, set_email, set_name):
    base_path = os.getcwd()
    config_path = get_paths(base_path)["config"]

    config = Config.read_config(config_path)
    if config is None:
        Messages.echo_error("Spacedock is not initialized. No .dock/ found.")
        return

    if list:
        click.echo(
            f"{click.style('Configuration:', fg="red")}\n\n"
            f"{click.style('Username:', fg="yellow")} {config.get('username', '')}\n"
            f"{click.style('Email:', fg="yellow")} {config.get('email', '')}\n"
            f"{click.style('Name:', fg="yellow")} {config.get('name', '')}"
        )
        return

    if not (set_username or set_email or set_name):
        click.echo(click.get_current_context().get_help())
        return

    if set_username:
        set_username = set_username.strip()
        if not set_username.isalnum():
            Messages.echo_error("username must only contain letters or numbers.")
            return
        elif len(set_username) <= 2:
            Messages.echo_error("username must be atleast greater than 2 characters.")
            return
        else:
            config["username"] = set_username

    if set_email:
        set_email = set_email.strip()
        email_regex = r"^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if not re.match(email_regex, set_email):
            Messages.echo_error("Enter a valid email.")
            return

        config["email"] = set_email

    if set_name:
        set_name = set_name.strip()

        cleaned_name = set_name.replace(" ", "").replace("-", "")

        if not cleaned_name.isalpha() or len(set_name) < 2:
            Messages.echo_error(
                "Name should only contain alphabets, spaces,"
                " and hyphens, and should be at least 2 letters long."
            )
            return

        config["name"] = set_name

    Config.write_config(config_path, config)
    Messages.echo_success("Config updated successfully!")
