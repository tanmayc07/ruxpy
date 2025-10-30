import os
import click
import json
import hashlib
from ruxpy import (
    Messages,
    safe_load_staged_files,
    get_paths,
    check_spacedock,
)
from ruxpy import filter_ignored_files


@click.command()
@click.argument("files", nargs=-1)
def beam(files):
    """Stage files for the next starlog (commit)"""

    paths = {}
    try:
        paths = get_paths()
    except Exception:
        Messages.echo_error(
            "The spacedock is not initialized. Please run 'ruxpy start'"
        )
        return

    # Check if spacedock is initialized
    is_proper = check_spacedock(paths)
    if not is_proper:
        Messages.echo_error(
            "The spacedock is not initialized. Please run 'ruxpy start'"
        )
        return

    stage_path = paths["stage"]
    staged_files = safe_load_staged_files(stage_path)

    files_to_check = list(files)
    files_not_ignored = filter_ignored_files(files_to_check)

    if len(files_not_ignored) == 0:
        Messages.echo_info(
            "No files beamed!\n"
            "If you think it's unexpected, check if .dockignore is present."
        )
        return

    # Load the latest starlog
    with open(paths["helm_f"], "r") as f:
        content = f.read().strip()

    course_name = content.split(":")[-1].strip().split("/")[-1]

    current_starlog_path = os.path.join(paths["links"], "helm", course_name)

    try:
        with open(current_starlog_path, "r") as f:
            current_starlog_hash = f.read()

        if not current_starlog_hash:
            # No starlogs yet
            starlog_obj = {"files": {}}
        else:
            starlog_obj_path = os.path.join(
                paths["dock"],
                "starlogs",
                current_starlog_hash[:2],
                current_starlog_hash[2:],
            )

            if not os.path.isfile(starlog_obj_path):
                # No starlogs yet
                starlog_obj = {"files": {}}
            else:
                with open(starlog_obj_path, "r") as f:
                    starlog_obj = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # No starlogs yet
        starlog_obj = {"files": {}}

    Messages.echo_info("Starting to beam the files...")

    # only append if its not staged previously
    total = len(files_not_ignored)
    for idx, file in enumerate(files_not_ignored, 1):
        percent_done = int((idx / total) * 100)

        if file in starlog_obj["files"]:
            if not os.path.exists(file):
                # File is deleted or missing
                click.echo(
                    f"{file}\t\t[{percent_done}%] "
                    f"{click.style('[skipped: not found]', fg='yellow')}"
                )
                continue

            with open(file, "rb") as f:
                content = f.read()

            hash_obj = hashlib.sha3_256()
            hash_obj.update(content)
            digest = hash_obj.hexdigest()

            if digest == starlog_obj["files"][file]:
                # File is already committed and unchanged, skip staging
                click.echo(
                    f"{file}\t\t[{percent_done}%] "
                    f"{
                        click.style(
                            '[skipped: unchanged and present in latest starlog]',
                            fg='yellow',
                        )
                    }"
                )
                continue

        click.echo(f"{file}\t\t[...{percent_done}%]")

        if file not in staged_files:
            staged_files.append(file)

    with open(paths["stage"], "w") as f:
        json.dump(staged_files, f)

    feedback = """Files successfully beamed to the spacedock.
Use ruxpy starlog to record."""

    Messages.echo_success(f"{feedback}")
