import os
import json
from click.testing import CliRunner
from ruxpy.cli import main


def test_start_creates_dock(tmp_path):
    test_repo = tmp_path / "repo"
    runner = CliRunner()
    result = runner.invoke(main, ["start", str(test_repo)])

    assert result.exit_code == 0
    assert (test_repo / ".dock").exists()
    assert (test_repo / ".dock" / "config.toml").exists()
    assert (test_repo / ".dock" / "HELM").exists()


def test_scan_shows_status(tmp_path):
    test_repo = tmp_path / "repo"
    runner = CliRunner()
    runner.invoke(main, ["start", str(test_repo)])

    # Change working directory to test_repo
    with runner.isolated_filesystem():
        os.chdir(test_repo)
        result = runner.invoke(main, ["scan"])
        assert result.exit_code == 0
        assert "On branch '-core-'" in result.output
        assert "Spacedock clear, no starlog updates required." in result.output


def test_beam_stages_files(tmp_path):
    runner = CliRunner()
    repo_path = tmp_path / "repo"
    os.makedirs(repo_path)
    os.chdir(repo_path)
    # Initialize repo
    runner.invoke(main, ["start"])
    # Create test files
    (repo_path / "file1.txt").write_text("hello")
    (repo_path / "file2.txt").write_text("world")
    # Run beam command
    result = runner.invoke(main, ["beam", "file1.txt", "file2.txt"])
    assert result.exit_code == 0
    # Check .dock/stage contents
    with open(repo_path / ".dock/stage") as f:
        staged = json.load(f)
    assert "file1.txt" in staged
    assert "file2.txt" in staged
