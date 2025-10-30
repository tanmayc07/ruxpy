import os
import click
from ruxpy import Spacedock, ruxpy
from ruxpy import (
    # required_items,
    find_dock_root_py,
    get_paths,
    check_spacedock,
    get_missing_spacedock_items,
)


@click.command()
@click.argument("path", default=".")
def start(path):
    """Start a new ruxpy repository"""

    # Check for spacedock
    dock_root = find_dock_root_py(path)

    if dock_root is None:
        # Create new spacedock
        dir_path = os.path.abspath(path)
        paths = get_paths(dir_path)

        dock_path = paths["dock"]
        os.makedirs(dock_path, exist_ok=True)

        # Create the objects dir
        ruxpy.init_object_dir(dir_path)

        # Create config.toml
        config_path = paths["config"]
        with open(config_path, "w") as f:
            f.write("# config.toml\n")

        # Create HELM pointer file
        helm_path = paths["helm_f"]
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

        click.echo(f"Initialized ruxpy repository in {paths['repo']}...")
    else:
        # Check if .dock/ has proper structure
        paths = get_paths(dock_root)
        is_proper = check_spacedock(paths)

        if is_proper:
            # Everything checks out, return early
            click.echo(f"Reinitialized ruxpy repository in {paths['repo']}...")
            return
        else:
            # Initialize new spacedock
            missing_paths = get_missing_spacedock_items(paths)
            for path in missing_paths:
                if Spacedock.get_path_kind(path) == "Dir":
                    if path == "links":
                        links_path = paths["links"]
                        os.makedirs(os.path.join(links_path, "helm"), exist_ok=True)

                    if path == "objects":
                        ruxpy.init_object_dir(paths["repo"])

                    if path == "dock":
                        dock_path = paths["dock"]
                        os.makedirs(dock_path, exist_ok=True)

                if Spacedock.get_path_kind(path) == "File":
                    if path == "stage":
                        with open(paths["stage"], "w") as f:
                            f.write("[]")

                    if path == "helm_f":
                        with open(paths["helm_f"], "w") as f:
                            f.write("link: links/helm/core\n")

                    if path == "core":
                        with open(paths["core"], "w") as f:
                            f.write("")

                    if path == "config":
                        with open(paths["config"], "w") as f:
                            f.write("# config.toml\n")

            click.echo(f"Initialized ruxpy repository in {paths['repo']}...")
