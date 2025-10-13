import os
import click
from ruxpy import (
    find_dock_root_py,
    get_paths,
    check_spacedock,
    Courses,
    Messages,
)


@click.command()
@click.argument("branch_name", required=False)
def course(branch_name: str):
    dock_root = find_dock_root_py()
    if dock_root is None:  # Not a ruxpy repository
        Messages.echo_error(
            "The spacedock is not initialized. " "Please run 'ruxpy start'"
        )
        return
    else:
        paths = get_paths(dock_root)
        is_proper = check_spacedock(paths)
        if not is_proper:
            Messages.echo_error(
                "The spacedock is corrupted. " "Please run 'ruxpy start'"
            )
            return

    if not branch_name:

        (courses, current) = Courses.get_courses_and_current(
            os.path.join(paths["links"], "helm"), paths["helm"]
        )

        label = "[On Course] =>"
        padding = " " * (len(label) + 1)
        for course in courses:
            if course == current:
                click.echo(f"{click.style(label, fg="green")} {course}")
                continue

            click.echo(f"{padding}{course}")

    else:
        try:
            Courses.create_course(branch_name)
            Messages.echo_success(f"course {branch_name} set at warp speed!")
        except Exception as e:
            Messages.echo_error(str(e))
