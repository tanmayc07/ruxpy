import os
import json
from typing import List
import click
from ruxpy import find_dock_root, list_all_files

required_items = {
    "repo": "dir",
    "dock": "dir",
    "links": "dir",
    "objects": "dir",
    "stage": "file",
    "helm": "file",
    "core": "file",
    "config": "file",
}


def find_dock_root_py(start_path="."):
    result = find_dock_root(start_path=".")
    return result


def get_paths(base_path=None):
    if base_path is None:
        base_path = find_dock_root_py()
        if base_path is None:
            raise Exception("No spacedock found!")

    paths = {}
    paths["repo"] = base_path
    paths["dock"] = os.path.join(base_path, ".dock")
    paths["stage"] = os.path.join(paths["dock"], "stage")
    paths["helm"] = os.path.join(paths["dock"], "HELM")
    paths["links"] = os.path.join(paths["dock"], "links")
    paths["core"] = os.path.join(paths["links"], "helm", "core")
    paths["config"] = os.path.join(paths["dock"], "config.toml")
    paths["objects"] = os.path.join(paths["dock"], "objects")

    return paths


def get_missing_spacedock_items(paths):
    dir_keys = ["repo", "dock", "links", "objects"]
    file_keys = ["stage", "helm", "core", "config"]
    required_keys = dir_keys + file_keys

    missing = []
    for key in required_keys:
        if key not in paths or not os.path.exists(paths[key]):
            missing.append(key)  # Integrity check failed
        if key in dir_keys and not os.path.isdir(paths[key]):
            missing.append(key)
        if key in file_keys and not os.path.isfile(paths[key]):
            missing.append(key)

    return missing


def check_spacedock(paths):
    return not get_missing_spacedock_items(paths)


def list_repo_files(repo_path) -> List[str]:
    files: List[str] = list_all_files(str(repo_path))
    return files


def list_staged_files(stage_path):
    try:
        with open(stage_path, "r") as f:
            staged_files = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        staged_files = []
    return staged_files


def list_unstaged_files(repo_path: str):
    repo_path = find_dock_root_py(repo_path)
    paths = get_paths(repo_path)

    with open(os.path.join(paths["dock"], "HELM"), "r") as f:
        branch_path = f.read().strip()

    latest_starlog_hash = ""
    if branch_path.startswith("link:"):
        course_file = branch_path.split("link:")[1].strip()
        course_path = os.path.join(paths["dock"], course_file)

        if os.path.isfile(course_path):
            with open(course_path, "r") as cf:
                latest_starlog_hash = cf.read().strip()
                if not latest_starlog_hash:
                    latest_starlog_hash = None

    try:
        committed_files = load_starlog_files(paths, latest_starlog_hash)
    except Exception:
        committed_files = []

    all_files = list_repo_files(repo_path)

    stage_path = os.path.join(repo_path, ".dock", "stage")
    staged_files = list_staged_files(stage_path)

    unstaged_files = []
    for file in all_files:
        if file not in staged_files and file not in committed_files:
            unstaged_files.append(file)

    return unstaged_files


def load_starlog_files(paths, starlog_hash):
    obj_file = os.path.join(
        paths["dock"], "starlogs", starlog_hash[:2], starlog_hash[2:]
    )
    if not os.path.isfile(obj_file):
        raise Exception("FileNotFound Error")

    with open(obj_file, "r") as f:
        starlog_obj = json.load(f)
    return starlog_obj.get("files", {})


def echo_error(msg):
    click.echo(f"{click.style('[ERROR]', fg='red')} {msg}")


def echo_warning(msg):
    click.echo(f"{click.style('[WARNING]', fg='yellow')} {msg}")


def echo_info(msg):
    click.echo(f"{click.style('[INFO]', fg='yellow')} {msg}")


def echo_success(msg):
    click.echo(f"{click.style('[SUCCESS]', fg='green')} {msg}")
