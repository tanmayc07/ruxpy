import os
import click
from ruxpy import (
    # find_dock_root_py,
    get_paths,
    Courses,
    Messages,
    Spacedock,
)


@click.command()
@click.argument("course_name", required=False)
@click.option("-d", "--delete", is_flag=True, help="Delete the course")
def course(course_name: str, delete: bool):
    dock_root = Spacedock.find_dock_root(None)
    if dock_root is None:  # Not a ruxpy repository
        Messages.echo_error(
            "The spacedock is not initialized. Please run 'ruxpy start'"
        )
        return
    else:
        paths = get_paths(dock_root)
        is_proper = Spacedock.check_spacedock(str(paths["repo"]))
        if not is_proper:
            Messages.echo_error("The spacedock is corrupted. Please run 'ruxpy start'")
            return

    if delete and course_name:
        try:
            Messages.echo_info(f"Deleting course: {course_name}")
            Courses.delete_course(course_name)
            Messages.echo_success(f"Successfully deleted course: {course_name}")
        except Exception as e:
            Messages.echo_error(str(e))
    elif delete and not course_name:
        Messages.echo_error("Please input the course name to delete")
    elif course_name:
        try:
            Courses.create_course(course_name)
            Messages.echo_success(f"course {course_name} set at warp speed!")
        except Exception as e:
            Messages.echo_error(str(e))
    else:
        (courses, current) = Courses.get_courses_and_current(
            os.path.join(paths["links"], "helm"), paths["helm_f"]
        )

        label = "[On Course] =>"
        padding = " " * (len(label) + 1)
        for course in courses:
            if course == current:
                click.echo(f"{click.style(label, fg='green')} {course}")
                continue

            click.echo(f"{padding}{course}")
