import os
from ..ruxpy import Spacedock


def get_paths(base_path=None):
    if base_path is None:
        base_path = Spacedock.find_dock_root(None)
        if base_path is None:
            raise Exception("No spacedock found!")

    paths = Spacedock.get_paths_dict(str(base_path))
    paths["repo"] = base_path if base_path != "." else os.getcwd()
    return paths
