import os
from ..ruxpy import find_dock_root

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


def find_dock_root_py(start_path="."):
    result = find_dock_root(start_path=".")
    return result


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
