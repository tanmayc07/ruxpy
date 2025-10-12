__version__ = "1.0.0"

from ruxpy.utils.config import read_config, write_config
from ruxpy.utils.messages import echo_error, echo_info, echo_success, echo_warning
from ruxpy.utils.course import (
    get_course_name,
    list_repo_files,
    load_staged_files,
    safe_load_staged_files,
    check_stage_path_exists,
    list_unstaged_files,
)
from ruxpy.utils.init import (
    required_items,
    get_paths,
    find_dock_root_py,
    get_missing_spacedock_items,
    check_spacedock,
)
from ruxpy.utils.starlog import get_latest_starlog_hash, load_starlog_files

# Import Rust extension and expose its functions
from .ruxpy import (
    init_object_dir,
    save_starlog,
    find_dock_root,
    list_all_files,
    filter_ignored_files,
    Courses,
    Blob,
)

__all__ = [
    # Rust extensions
    "init_object_dir",
    "save_starlog",
    "find_dock_root",
    "list_all_files",
    "filter_ignored_files",
    "Courses",
    "Blob",
    # Python utils
    "read_config",
    "write_config",
    "get_course_name",
    "get_latest_starlog_hash",
    "check_spacedock",
    "list_repo_files",
    "load_staged_files",
    "safe_load_staged_files",
    "check_stage_path_exists",
    "list_unstaged_files",
    "load_starlog_files",
    "required_items",
    "get_paths",
    "find_dock_root_py",
    "get_missing_spacedock_items",
    "echo_error",
    "echo_info",
    "echo_warning",
    "echo_success",
]
