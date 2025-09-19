import os
import json
from typing import List


def get_paths(base_path):
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


def list_repo_files(repo_path) -> List[str]:
    files: List[str] = []
    for root, dirs, filenames in os.walk(repo_path):
        # Skip internal directories
        if ".dock" in root or "__pycache__" in root:
            continue
        for filename in filenames:
            # Get relative path
            rel_path = os.path.relpath(os.path.join(root, filename), repo_path)
            files.append(rel_path)
    return files


def list_staged_files(stage_path):
    try:
        with open(stage_path, "r") as f:
            staged_files = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        staged_files = []
    return staged_files


def list_unstaged_files(repo_path: str):
    all_files = list_repo_files(repo_path)

    stage_path = os.path.join(repo_path, ".dock", "stage")
    staged_files = list_staged_files(stage_path)

    unstaged_files = []
    for file in all_files:
        if file not in staged_files:
            unstaged_files.append(file)

    return unstaged_files
