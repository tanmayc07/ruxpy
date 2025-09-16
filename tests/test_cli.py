import os
from click.testing import CliRunner
from ruxpy.cli import start, scan

def test_start_creates_dock(tmp_path):
    test_repo = tmp_path / "repo"
    runner = CliRunner()
    result = runner.invoke(start, [str(test_repo)])
    assert result.exit_code == 0
    assert (test_repo / ".dock").exists()
    assert (test_repo / ".dock" / "config.toml").exists()
    assert (test_repo / ".dock" / "HELM").exists()
    
def test_scan_shows_status(tmp_path):
    test_repo = tmp_path / "repo"
    runner = CliRunner()
    runner.invoke(start, [str(test_repo)])
    # Change working directory to test_repo
    with runner.isolated_filesystem():
        os.chdir(test_repo)
        result = runner.invoke(scan)
        assert result.exit_code == 0
        assert "On branch '-core-'" in result.output
        assert "Spacedock clear, no starlog updates required." in result.output
        