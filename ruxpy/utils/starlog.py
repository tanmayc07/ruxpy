import os
import json


def get_latest_starlog_hash(paths):
    with open(os.path.join(paths["dock"], "HELM"), "r") as f:
        branch_path = f.read().strip()

    latest_starlog_hash = ""
    if branch_path.startswith("link:"):
        course_file = branch_path.split("link:")[1].strip()
        course_path = os.path.join(paths["dock"], course_file)

        if os.path.isfile(course_path):
            with open(course_path, "r") as cf:
                latest_starlog_hash = cf.read().strip()
                return latest_starlog_hash or None
    return None


def load_starlog_files(paths, starlog_hash):
    obj_file = os.path.join(
        paths["dock"], "starlogs", starlog_hash[:2], starlog_hash[2:]
    )
    if not os.path.isfile(obj_file):
        raise Exception("FileNotFound Error")

    with open(obj_file, "r") as f:
        starlog_obj = json.load(f)
    return starlog_obj.get("files", {})
