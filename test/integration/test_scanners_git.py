import subprocess
from datetime import datetime
from pathlib import Path

import pytest

from chronicle.scanners.base import Scanner
from chronicle.scanners.git import GitScanner
from chronicle.scanners.models import Observation

GIT_IDENTITY = [
    "-c",
    "user.name=Chronicle Tests",
    "-c",
    "user.email=tests@chronicle.local",
]


def _init_repo(path: Path) -> Path:
    path.mkdir(parents=True)
    subprocess.run(["git", "init"], cwd=path, capture_output=True, check=True)
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


def test_git_scanner_returns_latest_commit_observation(tmp_path: Path):
    repo = _init_repo(tmp_path / "repo")
    (repo / "README.md").write_text("demo", encoding="utf-8")
    expected_hash = _commit_all(repo, "initial commit")

    observations = GitScanner(repo).scan()

    assert len(observations) == 1
    observation = observations[0]
    assert observation.source == "git"
    assert observation.type == "commit"
    assert observation.data["hash"] == expected_hash
    assert observation.data["message"] == "initial commit"
    assert isinstance(observation.timestamp, datetime)


def test_git_scanner_keeps_full_message_containing_pipes(tmp_path: Path):
    repo = _init_repo(tmp_path / "repo")
    (repo / "file.txt").write_text("data", encoding="utf-8")
    _commit_all(repo, "fix: handle a | b | c")

    observations = GitScanner(repo).scan()

    assert observations[0].data["message"] == "fix: handle a | b | c"


def test_git_scanner_returns_empty_list_for_repo_without_commits(tmp_path: Path):
    repo = _init_repo(tmp_path / "repo")

    observations = GitScanner(repo).scan()

    assert observations == []


def test_git_scanner_returns_empty_list_on_empty_log_output(
    tmp_path: Path, monkeypatch
):
    scanner = GitScanner(tmp_path)
    monkeypatch.setattr(scanner.git, "run", lambda *arguments: "\n")

    observations = scanner.scan()

    assert observations == []


def test_scanner_cannot_be_instantiated_directly(tmp_path: Path):
    with pytest.raises(TypeError):
        Scanner(tmp_path)


def test_scanner_subclass_must_implement_scan(tmp_path: Path):
    class IncompleteScanner(Scanner):
        pass

    with pytest.raises(TypeError):
        IncompleteScanner(tmp_path)


def test_observation_holds_scan_data():
    timestamp = datetime(2026, 8, 21, 12, 0, 0)

    observation = Observation(
        source="git",
        type="commit",
        timestamp=timestamp,
        data={"hash": "abc123", "message": "hello"},
    )

    assert observation.source == "git"
    assert observation.type == "commit"
    assert observation.timestamp == timestamp
    assert observation.data["hash"] == "abc123"
    assert observation.data["message"] == "hello"
