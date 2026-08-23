import sqlite3
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from chronicle.cli.main import app

runner = CliRunner()

GIT_IDENTITY = [
    "-c",
    "user.name=Chronicle Tests",
    "-c",
    "user.email=tests@chronicle.local",
]


def _init_repo(path: Path) -> Path:
    path.mkdir(parents=True)
    subprocess.run(["git", "init"], cwd=path, capture_output=True, check=True)
    (path / ".chronicle").mkdir()
    return path


def _commit_all(repo: Path, message: str) -> str:
    subprocess.run(["git", "add", "."], cwd=repo, capture_output=True, check=True)
    subprocess.run(
        ["git", *GIT_IDENTITY, "commit", "-m", message],
        cwd=repo,
        capture_output=True,
        check=True,
    )
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout.strip()


def _head_hash(repo: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout.strip()


def _open_db(repo: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(repo / ".chronicle" / "chronicle.db")
    connection.row_factory = sqlite3.Row
    return connection


def _stored_hashes(repo: Path) -> set[str]:
    connection = _open_db(repo)
    rows = connection.execute(
        "SELECT external_id FROM observations"
    ).fetchall()
    connection.close()
    return {row["external_id"] for row in rows}


def _checkpoint(repo: Path) -> str | None:
    connection = _open_db(repo)
    row = connection.execute(
        "SELECT value FROM scan_state WHERE scanner = 'git'"
        " AND key = 'last_commit'"
    ).fetchone()
    connection.close()
    return row["value"] if row else None


def test_scan_command_stores_observations_and_checkpoint(
    monkeypatch, tmp_path: Path
):
    repo = _init_repo(tmp_path / "repo")
    (repo / "README.md").write_text("demo", encoding="utf-8")
    head_hash = _commit_all(repo, "initial commit")
    monkeypatch.chdir(repo)

    result = runner.invoke(app, ["scan"])

    assert result.exit_code == 0
    assert "Collected 1 observation(s)." in result.stdout
    assert "Stored 1 new observation(s)" in result.stdout
    assert _stored_hashes(repo) == {head_hash}
    assert _checkpoint(repo) == head_hash


def test_scan_command_second_run_without_changes_stores_nothing(
    monkeypatch, tmp_path: Path
):
    repo = _init_repo(tmp_path / "repo")
    (repo / "README.md").write_text("demo", encoding="utf-8")
    _commit_all(repo, "initial commit")
    monkeypatch.chdir(repo)

    first_run = runner.invoke(app, ["scan"])
    second_run = runner.invoke(app, ["scan"])

    assert first_run.exit_code == 0
    assert second_run.exit_code == 0
    assert "All observation(s) already stored." in second_run.stdout
    assert len(_stored_hashes(repo)) == 1


def test_scan_command_picks_up_commits_since_checkpoint(
    monkeypatch, tmp_path: Path
):
    repo = _init_repo(tmp_path / "repo")
    (repo / "first.txt").write_text("one", encoding="utf-8")
    first_hash = _commit_all(repo, "first commit")
    monkeypatch.chdir(repo)
    runner.invoke(app, ["scan"])

    (repo / "second.txt").write_text("two", encoding="utf-8")
    intermediate_hash = _commit_all(repo, "second commit")
    (repo / "third.txt").write_text("three", encoding="utf-8")
    final_hash = _commit_all(repo, "third commit")

    incremental_run = runner.invoke(app, ["scan"])

    assert incremental_run.exit_code == 0
    assert "Collected 2 observation(s)." in incremental_run.stdout
    assert "Stored 2 new observation(s)" in incremental_run.stdout
    assert _stored_hashes(repo) == {first_hash, intermediate_hash, final_hash}
    assert _checkpoint(repo) == final_hash


def test_scan_command_does_not_duplicate_existing_observations(
    monkeypatch, tmp_path: Path
):
    repo = _init_repo(tmp_path / "repo")
    (repo / "README.md").write_text("demo", encoding="utf-8")
    head_hash = _commit_all(repo, "initial commit")
    monkeypatch.chdir(repo)
    runner.invoke(app, ["scan"])

    stale_context_run = runner.invoke(app, ["scan"])

    assert stale_context_run.exit_code == 0
    assert _stored_hashes(repo) == {head_hash}


def test_scan_command_fails_outside_git_repo(monkeypatch, tmp_path: Path):
    empty_directory = tmp_path / "not-a-repo"
    empty_directory.mkdir()
    monkeypatch.chdir(empty_directory)

    result = runner.invoke(app, ["scan"])

    assert result.exit_code == 1
    assert "Error: could not find git repo." in result.output
