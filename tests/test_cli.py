import os
import json
import tomlkit
import pytest
from click.testing import CliRunner
from ruxpy.cli import main
from ruxpy import get_paths, Spacedock


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


def test_start_creates_spacedock(tmp_path):
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    runner = CliRunner()

    with runner.isolated_filesystem():
        os.chdir(repo_path)
        result = runner.invoke(main, ["start"])

        paths = get_paths(repo_path)
        is_proper = Spacedock.check_spacedock(str(paths["repo"]))

        assert is_proper
        assert f"Initialized ruxpy repository in {paths['repo']}..." in result.output


def test_start_creates_dock_at_path(tmp_path):
    test_repo = tmp_path / "repo"
    test_repo.mkdir()

    runner = CliRunner()
    _ = runner.invoke(main, ["start", str(test_repo)])

    paths = get_paths(test_repo)
    is_proper = Spacedock.check_spacedock(str(paths["repo"]))

    assert is_proper


def test_start_reinitializes(tmp_path):
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    runner = CliRunner()

    with runner.isolated_filesystem():
        os.chdir(repo_path)
        _ = runner.invoke(main, ["start"])
        result = runner.invoke(main, ["start"])

        paths = get_paths(repo_path)
        is_proper = Spacedock.check_spacedock(str(paths["repo"]))

        assert is_proper
        assert "Reinitialized ruxpy repository in" in result.output


def test_start_initializes_with_missing_items(tmp_path):
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    runner = CliRunner()

    with runner.isolated_filesystem():
        os.chdir(repo_path)
        _ = runner.invoke(main, ["start"])

        paths = get_paths(repo_path)

        config_path = repo_path / ".dock" / "config.toml"
        if config_path.exists():
            os.remove(config_path)

        objects_path = repo_path / ".dock" / "objects"
        if objects_path.exists():
            os.rmdir(objects_path)

        result = runner.invoke(main, ["start"])

        is_proper = Spacedock.check_spacedock(str(paths["repo"]))
        assert is_proper
        assert "Initialized ruxpy repository in" in result.output


def test_scan_shows_status(init_repo):
    _ = init_repo
    runner = CliRunner()
    result = runner.invoke(main, ["scan"])
    assert result.exit_code == 0
    assert "On course '-core-'" in result.output
    assert "No starlog entries found!\n" in result.output


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


def test_beam_fails_when_spacedock_uninitialized(tmp_path):
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    os.chdir(repo_path)

    runner = CliRunner()
    (repo_path / "file1.txt").write_text("hello")

    result = runner.invoke(main, ["beam", "file1.txt"])
    assert (
        "[ERROR] The spacedock is not initialized. Please run 'ruxpy start'"
        in result.output
    )


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


def test_course_lists_courses_and_current(init_repo):
    repo_path = init_repo
    helm = repo_path / ".dock" / "links" / "helm"
    (helm / "feat-x").write_text("dummyhash1")
    (helm / "bugfix").write_text("dummyhash2")
    (helm / "main").write_text("dummyhash3")

    (repo_path / ".dock" / "HELM").write_text("link: links/helm/feat-x")

    runner = CliRunner()
    result = runner.invoke(main, ["course"])

    assert "[On Course] => feat-x" in result.output
    assert "core" in result.output
    assert "bugfix" in result.output
    assert "main" in result.output
