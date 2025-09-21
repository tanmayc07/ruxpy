import click
import os
import json
import tomlkit
from tomlkit import exceptions
from datetime import datetime
from ruxpy import ruxpy
from . import utility as util


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Ruxpy - A hybrid Rust/Python version control system"""
    pass


@main.command("config")
@click.option("-su", "--set-username", help="Set username in the config")
@click.option("-se", "--set-email", help="Set email in the config")
@click.option("-sn", "--set-name", help="Set name in the config")
def config(set_username, set_email, set_name):
    base_path = os.getcwd()
    config_path = util.get_paths(base_path)["config"]

    try:
        with open(config_path, "r") as f:
            config = tomlkit.parse(f.read())
    except (FileNotFoundError, exceptions.ParseError):
        click.echo(
            f"{click.style('[ERROR]', fg="red")} "
            "Spacedock is not initialized. No .dock/ found."
        )
        return

    if set_username:
        config["username"] = set_username
    if set_email:
        config["email"] = set_email
    if set_name:
        config["name"] = set_name

    with open(config_path, "w") as f:
        f.write(tomlkit.dumps(config))

    click.echo(
        f"{click.style('[SUCCESS]', fg="green")} " "Config updated successfully!"
    )


@main.command("start")
@click.argument("path", default=".")
def start(path):
    """Start a new ruxpy repository"""

    # Check for spacedock
    dock_root = util.find_dock_root(path)

    if dock_root is None:
        # Create new spacedock
        dir_path = os.path.abspath(path)
        paths = util.get_paths(dir_path)

        dock_path = paths["dock"]
        os.makedirs(dock_path, exist_ok=True)

        # Create the objects dir
        ruxpy.init_object_dir(dir_path)

        # Create config.toml
        config_path = paths["config"]
        with open(config_path, "w") as f:
            f.write("# config.toml\n")

        # Create HELM pointer file
        helm_path = paths["helm"]
        with open(helm_path, "w") as f:
            f.write("link: links/helm/core\n")

        # Create the links directory
        links_path = paths["links"]
        os.makedirs(os.path.join(links_path, "helm"), exist_ok=True)
        core_path = paths["core"]
        with open(core_path, "w") as f:
            f.write("")

        # Create stage file for staging area
        stage_path = paths["stage"]
        with open(stage_path, "w") as f:
            f.write("[]")

        # Create the starlogs dir
        starlog_path = os.path.join(dock_path, "starlogs")
        os.makedirs(starlog_path, exist_ok=True)

        click.echo(f"Initialized ruxpy repository in {paths["repo"]}...")
    else:
        # Check if .dock/ has proper structure
        paths = util.get_paths(dock_root)
        is_proper = util.check_spacedock(paths)

        if is_proper:
            # Everything checks out, return early
            click.echo(f"Reinitialized ruxpy repository in {paths["repo"]}...")
            return
        else:
            # Initialize new spacedock
            missing_paths = util.get_missing_spacedock_items(paths)
            for path in missing_paths:
                if util.required_items[path] == "dir":
                    if path == "links":
                        links_path = paths["links"]
                        os.makedirs(os.path.join(links_path, "helm"), exist_ok=True)

                    if path == "objects":
                        ruxpy.init_object_dir(paths["repo"])

                    if path == "dock":
                        dock_path = paths["dock"]
                        os.makedirs(dock_path, exist_ok=True)

                if util.required_items[path] == "file":
                    if path == "stage":
                        with open(paths["stage"], "w") as f:
                            f.write("[]")

                    if path == "helm":
                        with open(paths["helm"], "w") as f:
                            f.write("link: links/helm/core\n")

                    if path == "core":
                        with open(paths["core"], "w") as f:
                            f.write("")

                    if path == "config":
                        with open(paths["config"], "w") as f:
                            f.write("# config.toml\n")

            click.echo(f"Initialized ruxpy repository in {paths["repo"]}...")


@main.command("scan")
def scan():
    """Show the repository status"""

    helm_path = os.path.join(".dock", "HELM")
    if not os.path.exists(helm_path):
        click.echo(
            "No repository found. \
            Please run 'ruxpy start' to initialize a repository."
        )
        return
    with open(helm_path, "r") as f:
        content = f.read().strip()

    branch_name = content.split(":")[-1].strip().split("/")[-1]

    click.echo(f"On branch '-{branch_name}-'")
    click.echo("Spacedock clear, no starlog updates required.")


@main.command("beam")
@click.argument("files", nargs=-1)
def beam(files):
    """Stage files for the next starlog (commit)"""

    paths = util.get_paths(os.getcwd())

    # Check if spacedock is initialized
    for _, path in paths.items():
        if not os.path.isfile(path) and not os.path.isdir(path):
            click.echo(
                f"{click.style('[ERROR]', fg='red')} "
                "The spacedock is not initialized. "
                "Please run 'ruxpy start'"
            )
            return

    stage_path = paths["stage"]
    staged_files = util.list_staged_files(stage_path)

    # only append if its not staged previously
    for file in files:
        if file not in staged_files:
            staged_files.append(file)

    with open(paths["stage"], "w") as f:
        json.dump(staged_files, f)

    feedback = """Files successfully beamed to the spacedock.
Use ruxpy starlog to record.
"""
    click.echo(f"{click.style('[SUCCESS]', fg='green')} " f"{feedback}")


@main.command("starlog")
@click.option(
    "-c", "--create", is_flag=True, help="Create a new starlog entry (commit)"
)
@click.option("-m", "--message", help="Commit message for the starlog entry")
def starlog(create, message):
    base_path = os.getcwd()
    paths = util.get_paths(base_path)

    if create:
        stage_path = os.path.join(paths["dock"], "stage")
        staged_files = util.list_staged_files(stage_path)

        if len(staged_files) == 0:
            unstaged_files = util.list_unstaged_files(".")
            click.echo(
                f"{click.style('[WARNING]', fg="yellow")} " "Files are not beamed yet."
            )

            click.echo(
                """
On branch core
Files yet to be beamed:
 (use "ruxpy beam <file>..." to add files for starlog)"""
            )

            for file in unstaged_files[:4]:
                click.echo(click.style(f"\tmodified:\t{file}", fg="red"))

            # Return early if there are no staged files
            return

        if message:
            # Gather config metadata
            config_path = paths["config"]
            with open(config_path, "r") as f:
                config = tomlkit.parse(f.read())

            try:
                author = config["name"]
                email = config["email"]
            except exceptions.NonExistentKey:
                click.echo(
                    f"{click.style('[ERROR]', fg="red")} "
                    "Please set name and email for starlogs\n"
                    " (Use ruxpy config -sn <name> -se <email>)"
                )
                return

            timestamp = datetime.now().isoformat()

            staged_hash_list = {}
            for file in staged_files:
                hash = ruxpy.save_blob(paths["repo"], file)
                staged_hash_list[file] = hash

            helm_path = paths["helm"]
            course_path = ""
            try:
                with open(helm_path, "r") as f:
                    content = f.read().strip()
                if content.startswith("link:"):
                    course_file = content.split("link:")[1].strip()
                    course_path = os.path.join(paths["dock"], course_file)
                    if os.path.isfile(course_path):
                        with open(course_path, "r") as cf:
                            parent = cf.read().strip()
                        if not parent:
                            parent = None  # Initial starlog
                    else:
                        click.echo(
                            "The spacedock is not initialized. "
                            "Please run 'ruxpy start'"
                        )
                        return
                else:
                    click.echo(
                        "The spacedock is not initialized. " "Please run 'ruxpy start'"
                    )
                    return
            except FileNotFoundError:
                click.echo(
                    "The spacedock is not initialized. " "Please run 'ruxpy start'"
                )
                return

            starlog_obj = {
                "message": message,
                "author": author,
                "email": email,
                "timestamp": timestamp,
                "parent": parent,
                "files": staged_hash_list,
            }

            serialized = json.dumps(starlog_obj, sort_keys=True)
            starlog_bytes = serialized.encode("utf-8")
            starlog_hash = ruxpy.save_starlog(paths["repo"], starlog_bytes)

            with open(course_path, "w") as f:
                f.write(starlog_hash)

            with open(paths["stage"], "w") as f:
                json.dump([], f)

            click.echo(
                f"{click.style('[SUCCESS]', fg="green")} "
                "Starlog entry saved! Next course?"
            )

        else:
            click.echo(
                f"{click.style('[ERROR]', fg="red")} "
                """Please include a message
 (Use ruxpy starlog -cm to create a commit with a message.)"""
            )
    else:
        click.echo(
            """Usage:
Use -cm to create a commit with a message.
Use -l to list all starlogs."""
        )


if __name__ == "__main__":
    main()
