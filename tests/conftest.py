import os
import json
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


@pytest.fixture
def starlog_repo(tmp_path):
    # Setup minimal spacedock structure
    repo_path = tmp_path / "repo"
    repo_path.mkdir()

    runner = CliRunner()
    with runner.isolated_filesystem():
        os.chdir(repo_path)
        result = runner.invoke(main, ["start"])
        assert result.exit_code == 0
        starlogs_dir = repo_path / ".dock" / "starlogs" / "ab"
        starlogs_dir.mkdir(parents=True, exist_ok=True)

        # Create a mock starlog file
        starlog_obj = {
            "author": "Test",
            "email": "test@example.com",
            "message": "Test commit",
            "timestamp": "2025-09-23T00:00:00",
            "parent": None,
            "files": {},
        }

        with open(starlogs_dir / "cdef1234", "w") as f:
            json.dump(starlog_obj, f)

        helm_path = repo_path / ".dock" / "HELM"
        with open(helm_path, "w") as f:
            f.write("link: links/helm/core")

        core_path = repo_path / ".dock" / "links" / "helm" / "core"
        with open(core_path, "w") as f:
            f.write("abcdef1234")

        yield repo_path
