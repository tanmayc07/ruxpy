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

    # Run starlog
    result = runner.invoke(main, ["starlog", "-cm", "Test commit"])
    assert result.exit_code == 0

    # Check starlog file exists
    starlogs_dir = repo / ".dock" / "starlogs"
    assert any(starlogs_dir.iterdir())

    # Check stage file is cleared
    with open(repo / ".dock" / "stage") as f:
        assert json.load(f) == []
