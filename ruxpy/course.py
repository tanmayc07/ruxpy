import os
import click
from ruxpy import (
    find_dock_root_py,
    get_paths,
    check_spacedock,
    get_courses_and_current,
    echo_error,
)


@click.command()
def course():
    dock_root = find_dock_root_py()
    if dock_root is None:  # Not a ruxpy repository
        echo_error("The spacedock is not initialized. " "Please run 'ruxpy start'")
        return
    else:
        paths = get_paths(dock_root)
        is_proper = check_spacedock(paths)
        if not is_proper:
            echo_error("The spacedock is corrupted. " "Please run 'ruxpy start'")
            return

    (courses, current) = get_courses_and_current(
        os.path.join(paths["links"], "helm"), paths["helm"]
    )

    label = "[On Course] =>"
    padding = " " * (len(label) + 1)
    for course in courses:
        if course == current:
            click.echo(f"{click.style(label, fg="green")} {course}")
            continue

        click.echo(f"{padding}{course}")
