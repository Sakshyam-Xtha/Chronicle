from pathlib import Path

from typer.testing import CliRunner

from chronicle.cli.main import app
from chronicle.project.status import get_status

runner = CliRunner()


def _make_git_project(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    project.mkdir()
    (project / ".git").mkdir()
    return project


def _initialize_chronicle(project: Path) -> None:
    chronicle_dir = project / ".chronicle"
    chronicle_dir.mkdir()
    (chronicle_dir / "config.toml").touch()


def test_get_status_detects_git_repo(monkeypatch, tmp_path: Path):
    project = _make_git_project(tmp_path)
    monkeypatch.chdir(project)

    status = get_status()

    assert status is not None
    assert status.project_root == project
    assert status.git_detected is True
    assert status.chronicle_initialized is False
    assert status.config_exists is False


def test_get_status_detects_initialized_chronicle(monkeypatch, tmp_path: Path):
    project = _make_git_project(tmp_path)
    _initialize_chronicle(project)
    monkeypatch.chdir(project)

    status = get_status()

    assert status is not None
    assert status.chronicle_initialized is True
    assert status.config_exists is True
    assert status.git_detected is True


def test_get_status_returns_none_without_git(monkeypatch, tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)

    status = get_status()

    assert status is None


def test_status_command_prints_project_summary(monkeypatch, tmp_path: Path):
    project = _make_git_project(tmp_path)
    monkeypatch.chdir(project)

    result = runner.invoke(app, ["status"])

    assert result.exit_code == 0
    assert "Project: project" in result.stdout
    assert f"Root: {project}" in result.stdout
    assert "Git: detected" in result.stdout
    assert "Chronicle: not initialized" in result.stdout
    assert "Configuration: missing" in result.stdout


def test_status_command_prints_initialized_state(monkeypatch, tmp_path: Path):
    project = _make_git_project(tmp_path)
    _initialize_chronicle(project)
    monkeypatch.chdir(project)

    result = runner.invoke(app, ["status"])

    assert result.exit_code == 0
    assert "Chronicle: initialized" in result.stdout
    assert "Configuration: found" in result.stdout


def test_status_command_fails_cleanly_outside_git_repo(monkeypatch, tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)

    result = runner.invoke(app, ["status"])

    assert result.exit_code == 1
    assert "Error: could not find a Git repo in the project." in result.stdout
