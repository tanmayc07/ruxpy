import os
import json
import tomlkit
import pytest
from click.testing import CliRunner
from ruxpy.cli import main


@pytest.fixture
def init_repo(tmp_path):
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.chdir(repo_path)
        result = runner.invoke(main, ["start"])
        assert result.exit_code == 0
        yield repo_path


def test_start_creates_dock(tmp_path):
    test_repo = tmp_path / "repo"
    runner = CliRunner()
    result = runner.invoke(main, ["start", str(test_repo)])

    assert result.exit_code == 0
    assert (test_repo / ".dock").exists()
    assert (test_repo / ".dock" / "config.toml").exists()
    assert (test_repo / ".dock" / "HELM").exists()


def test_scan_shows_status(init_repo):
    _ = init_repo
    runner = CliRunner()
    result = runner.invoke(main, ["scan"])
    assert result.exit_code == 0
    assert "On branch '-core-'" in result.output
    assert "Spacedock clear, no starlog updates required." in result.output


def test_beam_stages_files(init_repo):
    repo_path = init_repo
    runner = CliRunner()
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


def test_set_config_individual(init_repo):
    repo_path = init_repo
    runner = CliRunner()

    runner.invoke(main, ["config", "-se", "picard@gmail.com"])
    runner.invoke(main, ["config", "-su", "picard2305"])
    runner.invoke(main, ["config", "-sn", "Jean-luc Picard"])

    with open(repo_path / ".dock" / "config.toml", "r") as f:
        config = tomlkit.parse(f.read())

    assert config["email"] == "picard@gmail.com"
    assert config["username"] == "picard2305"
    assert config["name"] == "Jean-luc Picard"


def test_set_config_together(init_repo):
    repo_path = init_repo
    runner = CliRunner()

    runner.invoke(
        main,
        [
            "config",
            "-se",
            "picard@gmail.com",
            "-su",
            "picard2305",
            "-sn",
            "Jean-luc Picard",
        ],
    )

    with open(repo_path / ".dock" / "config.toml", "r") as f:
        config = tomlkit.parse(f.read())

    assert config["email"] == "picard@gmail.com"
    assert config["username"] == "picard2305"
    assert config["name"] == "Jean-luc Picard"


def test_update_config_keys(init_repo):
    repo_path = init_repo
    runner = CliRunner()

    config_path = repo_path / ".dock" / "config.toml"
    with open(config_path, "r") as f:
        config = tomlkit.parse(f.read())

    config["username"] = "chrispike"
    config["email"] = "chris.pike@gmail.com"

    with open(config_path, "w") as f:
        tomlkit.dump(config, f)

    runner.invoke(main, ["config", "-su", "picard"])
    runner.invoke(main, ["config", "-se", "picard@gmail.com"])

    with open(config_path, "r") as f:
        config = tomlkit.parse(f.read())

    assert config["username"] == "picard"
    assert config["email"] == "picard@gmail.com"


def test_config_cmd_errors_when_config_missing(init_repo):
    repo_path = init_repo
    runner = CliRunner()

    config_path = repo_path / ".dock" / "config.toml"
    if config_path.exists():
        os.remove(config_path)

    result = runner.invoke(main, ["config", "-su", "picard2305"])
    assert result.exit_code == 0
    assert "[ERROR] Spacedock is not initialized. No .dock/ found." in result.output
