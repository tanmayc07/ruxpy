import os
import json
from ruxpy.cli import main
from click.testing import CliRunner


def test_starlog_command(tmp_path):
    repo = tmp_path / "repo"
    os.makedirs(repo)
    os.chdir(repo)
    runner = CliRunner()
    runner.invoke(main, ["start", str(repo)])

    # Create and stage files
    (repo / "file1.txt").write_text("hello")
    (repo / ".conf").mkdir(parents=True, exist_ok=True)
    (repo / ".conf" / "config.py").write_text("set_key=7ash2bs23basd")
    runner.invoke(main, ["beam", "file1.txt", ".conf/config.py"])
    runner.invoke(main, ["config", "-sn", "Jean-luc picard", "-se", "picard@gmail.com"])

    # Run starlog
    result = runner.invoke(main, ["starlog", "-cm", "Test commit"])
    assert result.exit_code == 0

    # Check starlog file exists
    starlogs_dir = repo / ".dock" / "starlogs"
    assert any(starlogs_dir.iterdir())

    # Check stage file is cleared
    with open(repo / ".dock" / "stage") as f:
        assert json.load(f) == []


def test_starlog_requires_name_and_email(tmp_path):
    repo_path = tmp_path / "repo"
    os.makedirs(repo_path)
    os.chdir(repo_path)
    runner = CliRunner()
    runner.invoke(main, ["start", str(repo_path)])

    (repo_path / "file1.txt").write_text("hello")
    runner.invoke(main, ["beam", "file1.txt"])

    result = runner.invoke(main, ["starlog", "-cm", "init"])

    assert (
        "[ERROR] Please set name and email for starlogs\n"
        " (Use ruxpy config -sn <name> -se <email>)" in result.output
    )


def test_starlog_list_with_entries(starlog_repo):
    runner = CliRunner()
    result = runner.invoke(main, ["starlog", "-l"])
    assert (
        "starlog abcdef1234 " in result.output
        and "(HELM -> core)" in result.output
        and "Author: Test" in result.output
    )


def test_starlog_list_without_entries(init_repo):
    runner = CliRunner()
    result = runner.invoke(main, ["starlog", "-l"])
    assert "[INFO] No starlog entries found!" in result.output


def test_starlog_clears_stage_if_all_beamed_files_deleted(init_repo):
    runner = CliRunner()
    (init_repo / "file1.txt").write_text("hello")
    (init_repo / "file2.txt").write_text("world")
    runner.invoke(main, ["beam", "file1.txt", "file2.txt"])

    (init_repo / "file1.txt").unlink()
    (init_repo / "file2.txt").unlink()
    assert not os.path.exists(init_repo / "file1.txt")
    assert not os.path.exists(init_repo / "file2.txt")

    runner.invoke(main, ["config", "-sn", "n", "-se", "e"])
    runner.invoke(main, ["starlog", "-cm", "init"])

    with open(init_repo / ".dock" / "stage") as f:
        assert json.load(f) == []
