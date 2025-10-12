import os
import click
import json
import hashlib
from ruxpy import (
    get_course_name,
    check_stage_path_exists,
    load_staged_files,
    Messages,
    list_repo_files,
    find_dock_root_py,
    list_unstaged_files,
    get_paths,
    check_spacedock,
)


@click.command()
def scan():
    """Show the repository status"""

    # check for spacedock
    dock_root = find_dock_root_py()
    if dock_root is None:  # Not a ruxpy repository
        Messages.echo_error(
            "The spacedock is not initialized. " "Please run 'ruxpy start'"
        )
        return
    else:
        paths = get_paths(dock_root)
        is_proper = check_spacedock(paths)
        if not is_proper:
            Messages.echo_error(
                "The spacedock is corrupted. " "Please run 'ruxpy start'"
            )
            return

    # Scan the spacedock
    course_name = get_course_name(paths["helm"])
    click.echo(f"On course '-{course_name}-'")

    # Read staging area
    stage_path = paths["stage"]
    if not check_stage_path_exists(stage_path):
        Messages.echo_error("The spacedock is corrupted. " "Please run 'ruxpy start'")
        return

    try:
        staged_files = load_staged_files(stage_path)
    except Exception:
        staged_files = []

    # Load the latest starlog entry
    _ = os.path.join(paths["dock"], "starlogs")

    current_starlog_path = os.path.join(paths["links"], "helm", course_name)
    with open(current_starlog_path, "r") as f:
        current_starlog_hash = f.read()

    starlog_obj_path = os.path.join(
        paths["dock"], "starlogs", current_starlog_hash[:2], current_starlog_hash[2:]
    )
    if not os.path.isfile(starlog_obj_path):
        unstaged_files = list_unstaged_files(paths["repo"])

        Messages.echo_info("No starlog entries found!")

        if len(staged_files) > 0:
            click.echo()
            click.echo("Ready to record into starlog:")
            for file in staged_files:
                click.echo(f"\t{click.style(f'beamed:\t{file}', fg="green")}")

        if len(unstaged_files) > 0:
            click.echo()
            click.echo("Changes that are untracked:")
            click.echo(" (use `ruxpy beam <file>... to update`)")
            for file in unstaged_files:
                click.echo(f"\t{click.style(file, fg="red")}")

        return

    with open(starlog_obj_path, "r") as f:
        starlog_obj = json.load(f)

    working_dir = list_repo_files(paths["repo"])

    untracked = []
    modified = []
    deleted = []

    for file in working_dir:
        if file not in starlog_obj["files"]:
            untracked.append(file)
            continue

        with open(file, "rb") as f:
            content = f.read()

        hash_obj = hashlib.sha3_256()
        hash_obj.update(content)
        digest = hash_obj.hexdigest()

        if digest != starlog_obj["files"][file]:
            modified.append(file)

    for file, _ in starlog_obj["files"].items():
        if file not in working_dir:
            deleted.append(file)

    untracked = [f for f in untracked if f not in staged_files]
    modified = [f for f in modified if f not in staged_files]

    click.echo("Ready to record into starlog:")
    for file in staged_files:
        click.echo(f"\t{click.style(f'beamed:\t{file}', fg="green")}")
    click.echo()

    click.echo("Changes that can be beamed:")
    click.echo("  (use `ruxpy beam <file>...` to update)")
    for file in modified:
        click.echo(f"\t{click.style(f'modified:\t{file}', fg="red")}")

    for file in deleted:
        click.echo(f"\t{click.style(f'deleted:\t{file}', fg="red")}")
    click.echo()

    click.echo("Changes that are untracked:")
    click.echo(" (use `ruxpy beam <file>... to update`)")
    for file in untracked:
        click.echo(f"\t{click.style(file, fg="red")}")
    click.echo()

    click.echo(
        f"Modified: {modified} "
        f"Untracked: {untracked} "
        f"Deleted: {deleted} "
        f"Staged: {staged_files}"
    )
