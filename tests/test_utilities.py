import os
from ruxpy.cli import main
from ruxpy import (
    list_repo_files,
    load_staged_files,
    list_unstaged_files,
    echo_success,
    echo_error,
    echo_info,
    echo_warning,
)
from click.testing import CliRunner


def test_list_staged_files(tmp_path):
    test_repo = tmp_path / "repo"
    os.makedirs(test_repo)
    os.chdir(test_repo)

    runner = CliRunner()
    runner.invoke(main, ["start", str(test_repo)])

    (test_repo / "file1.txt").write_text("hello")
    (test_repo / "file2.txt").write_text("world")

    runner.invoke(main, ["beam", "file1.txt", "file2.txt"])

    staged_path = os.path.join(test_repo, ".dock", "stage")
    staged_files = load_staged_files(staged_path)

    assert set(staged_files) == {"file1.txt", "file2.txt"}


def test_list_unstaged_files(tmp_path):
    test_repo = tmp_path / "repo"
    os.makedirs(test_repo)
    os.chdir(test_repo)

    runner = CliRunner()
    runner.invoke(main, ["start", str(test_repo)])

    (test_repo / "file1.txt").write_text("hello")
    (test_repo / "file2.txt").write_text("world")

    runner.invoke(main, ["beam", "file1.txt"])

    unstaged_files = list_unstaged_files(test_repo)
    assert unstaged_files == ["file2.txt"]


def test_list_repo_files(tmp_path):
    test_repo = tmp_path / "repo"
    os.makedirs(test_repo)
    os.chdir(test_repo)

    runner = CliRunner()
    runner.invoke(main, ["start", str(test_repo)])

    (test_repo / "file1.txt").write_text("hello")
    (test_repo / "file2.txt").write_text("world")
    (test_repo / "src").mkdir(parents=True, exist_ok=True)
    (test_repo / "src" / "file1.txt").write_text("Hello World")

    all_files = list_repo_files(test_repo)
    assert set(all_files) == {"file1.txt", "file2.txt", "src/file1.txt"}


def test_echo_error(capsys):
    msg = "Spacedock is not initialized."
    echo_error(msg)
    captured = capsys.readouterr()
    assert f"[ERROR] {msg}" in captured.out


def test_echo_warning(capsys):
    msg = "No files to make a starlog entry!"
    echo_warning(msg)
    captured = capsys.readouterr()
    assert f"[WARNING] {msg}" in captured.out


def test_echo_info(capsys):
    msg = "No files beamed yet"
    echo_info(msg)
    captured = capsys.readouterr()
    assert f"[INFO] {msg}" in captured.out


def test_echo_success(capsys):
    msg = "Files beamed successfully"
    echo_success(msg)
    captured = capsys.readouterr()
    assert f"[SUCCESS] {msg}" in captured.out
