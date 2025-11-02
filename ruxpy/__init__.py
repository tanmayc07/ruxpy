__version__ = "1.0.0"

from ruxpy.utils.config import Config
from ruxpy.utils.messages import Messages
from ruxpy.utils.course import (
    get_course_name,
    list_repo_files,
    load_staged_files,
    safe_load_staged_files,
    check_stage_path_exists,
    list_unstaged_files,
)
from ruxpy.utils.init import (
    get_paths,
)

# Import Rust extension and expose its functions
from .ruxpy import (
    init_object_dir,
    save_starlog,
    list_all_files,
    filter_ignored_files,
    Courses,
    Blob,
    Spacedock,
    Starlog,
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
    "Spacedock",
    "Starlog",
    # Python utils
    "get_course_name",
    "list_repo_files",
    "load_staged_files",
    "safe_load_staged_files",
    "check_stage_path_exists",
    "list_unstaged_files",
    "get_paths",
    "Messages",
    "Config",
]
