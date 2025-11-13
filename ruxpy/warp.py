import os
import click
from ruxpy import (
    get_paths,
    Messages,
    Spacedock,
    RuxpyTree,
    Courses,
    Starlog,
    safe_load_staged_files,
    list_unstaged_files,
)


@click.command
@click.argument("course", nargs=1)
def warp(course):
    """Switch to a course"""

    paths = {}
    try:
        paths = get_paths()
    except Exception:
        Messages.echo_error(
            "The spacedock is not initialized. Please run 'ruxpy start'"
        )
        return

    # Check if spacedock is initialized
    is_proper = Spacedock.check_spacedock(str(paths["repo"]))
    if not is_proper:
        Messages.echo_error(
            "The spacedock is not initialized. Please run 'ruxpy start'"
        )
        return

    try:
        course_exists = Courses.check_course_existence(str(course))
        if course_exists:
            dest_starlog_hash = Courses.get_latest_starlog_hash(str(course))
            dest_tree_hash = Starlog.get_tree_hash(dest_starlog_hash)

            # Check if there are any changes or
            # unrecorded files present to warn the user.
            staged_files = safe_load_staged_files(os.path.join(paths["dock"], "stage"))
            newly_created_files = list_unstaged_files(paths["repo"])

            if len(staged_files) > 0 or len(newly_created_files) > 0:
                Messages.echo_warning(
                    """Warping to a new course might lead to problems.\
 Beam the changes and record starlog first.
 (Use ruxpy beam [...<files>]) to beam files)
 (Use ruxpy starlog -cm to record starlog.)
                """
                )
                return

            RuxpyTree.warp_to_course(dest_tree_hash, str(paths["repo"]))

            helm_file = paths["helm_f"]
            with open(helm_file, "w") as f:
                f.write(f"link: links/helm/{course}")

            Messages.echo_success("Warped successfully")

        else:
            Messages.echo_error(
                f"Course {course} does not exist.\
                Please use `ruxpy course <course-name>` to create one."
            )

    except Exception as e:
        Messages.echo_error(e)
