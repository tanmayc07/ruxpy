import os
import json
from .init import find_dock_root_py, get_paths
from .starlog import Starlog
from ..ruxpy import list_all_files


def get_course_name(path):
    with open(path, "r") as f:
        content = f.read().strip()

    course_name = content.split(":")[-1].strip().split("/")[-1]
    return course_name


def list_repo_files(repo_path):
    files = list_all_files(str(repo_path))
    return files


def load_staged_files(stage_path):
    with open(stage_path, "r") as f:
        return json.load(f)


def safe_load_staged_files(stage_path, default=None):
    try:
        return load_staged_files(stage_path)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else []


def check_stage_path_exists(stage_path):
    return os.path.exists(stage_path)


def list_unstaged_files(repo_path: str):
    repo_path = find_dock_root_py(repo_path)
    paths = get_paths(repo_path)

    latest_starlog_hash = Starlog.get_latest_starlog_hash(paths)

    try:
        committed_files = Starlog.load_starlog_files(paths, latest_starlog_hash)
    except Exception:
        committed_files = []

    all_files = list_repo_files(repo_path)

    stage_path = os.path.join(repo_path, ".dock", "stage")
    staged_files = safe_load_staged_files(stage_path)

    unstaged_files = []
    for file in all_files:
        if file not in staged_files and file not in committed_files:
            unstaged_files.append(file)

    return unstaged_files
