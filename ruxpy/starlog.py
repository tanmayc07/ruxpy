import os
from datetime import datetime
import json
import hashlib
import tomlkit
from tomlkit import exceptions
import click
from ruxpy import ruxpy
from ruxpy import (
    Messages,
    safe_load_staged_files,
    find_dock_root_py,
    get_paths,
    check_spacedock,
    list_unstaged_files,
    load_starlog_files,
    list_repo_files,
)


@click.command()
@click.option(
    "-c", "--create", is_flag=True, help="Create a new starlog entry (commit)"
)
@click.option("-m", "--message", help="Commit message for the starlog entry")
@click.option("-l", "--list", is_flag=True, help="List all starlog entries (commits)")
def starlog(create, message, list):
    # Find the root and check integrity
    base_path = find_dock_root_py()
    paths = get_paths(base_path)

    is_proper = check_spacedock(paths)
    if not is_proper:
        Messages.echo_error(
            "The spacedock is not initialized. " "Please run 'ruxpy start'"
        )
        return

    if list:
        starlogs_dir = os.path.join(paths["dock"], "starlogs")
        starlogs_obj_list = []

        found_logs = False
        for root, _, files in os.walk(starlogs_dir):
            for file in files:
                found_logs = True
                dirpart = os.path.basename(root)
                full_hash = dirpart + file
                starlog_path = os.path.join(root, file)
                with open(starlog_path, "r") as f:
                    starlog_obj = json.load(f)
                    starlog_obj["hash"] = full_hash
                    starlogs_obj_list.append(starlog_obj)

        if not found_logs:
            Messages.echo_info("No starlog entries found!")
            return

        starlogs_obj_list.sort(key=lambda x: x["timestamp"], reverse=True)

        for starlog_obj in starlogs_obj_list:
            click.echo(
                f"Hash: {starlog_obj["hash"]}\n"
                f"Author: {starlog_obj.get('author')}\n"
                f"Email: {starlog_obj.get('email')}\n"
                f"Message: {starlog_obj.get('message')}\n"
                f"Timestamp: {starlog_obj.get('timestamp')}\n"
                f"Parent: {starlog_obj.get('parent')}\n"
                "-------------------------------------------------------------------"
            )

        return

    if create:
        stage_path = os.path.join(paths["dock"], "stage")
        staged_files = safe_load_staged_files(stage_path)

        if len(staged_files) == 0:
            unstaged_files = list_unstaged_files(".")
            Messages.echo_warning("Files are not beamed yet.")

            click.echo(
                """
On branch core
Files yet to be beamed:
 (use "ruxpy beam <file>..." to add files for starlog)"""
            )

            for file in unstaged_files:
                click.echo(click.style(f"\tuntracked:\t{file}", fg="red"))

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
                Messages.echo_error(
                    "Please set name and email for starlogs\n"
                    " (Use ruxpy config -sn <name> -se <email>)"
                )
                return

            timestamp = datetime.now().isoformat()

            staged_hash_list = {}
            saved_count = 0
            for file in staged_files:
                # if file is deleted or missing from working_dir, then skip it
                if not os.path.exists(file):
                    Messages.echo_warning(
                        f"File '{file}' was deleted and will not be committed."
                    )
                    continue
                hash = ruxpy.Blob.save_blob(paths["repo"], file)
                staged_hash_list[file] = hash
                saved_count += 1

            if saved_count == 0:
                Messages.echo_warning("No files to make a starlog entry!")
                with open(paths["stage"], "w") as f:
                    json.dump([], f)
                return

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

            if starlog_obj["parent"] is not None:
                try:
                    parent_files = load_starlog_files(paths, parent)
                except Exception:
                    Messages.echo_error("Opening parent starlog failed!")
                    return

                all_files = list_repo_files(paths["repo"])
                current_hashes = {}
                for file in all_files:
                    with open(file, "rb") as f:
                        content = f.read()
                    hash_obj = hashlib.sha3_256()
                    hash_obj.update(content)
                    digest = hash_obj.hexdigest()
                    current_hashes[file] = digest

                for pfile, pf_hash in parent_files.items():
                    if pfile in all_files:
                        # check if file is modified but not staged
                        if pfile not in staged_files:
                            starlog_obj["files"][pfile] = pf_hash
                    else:
                        # check for renamed files
                        for file, fhash in current_hashes.items():
                            if fhash == pf_hash and file not in parent_files:
                                starlog_obj["files"][file] = pf_hash

            serialized = json.dumps(starlog_obj, sort_keys=True)
            starlog_bytes = serialized.encode("utf-8")
            starlog_hash = ruxpy.save_starlog(paths["repo"], starlog_bytes)

            with open(course_path, "w") as f:
                f.write(starlog_hash)

            with open(paths["stage"], "w") as f:
                json.dump([], f)

            Messages.echo_success("Starlog entry saved! Next course?")

        else:
            Messages.echo_error(
                """Please include a message
 (Use ruxpy starlog -cm to create a commit with a message.)"""
            )
    else:
        click.echo(
            """Usage:
Use -cm to create a commit with a message.
Use -l to list all starlogs."""
        )
