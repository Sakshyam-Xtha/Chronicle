import subprocess
from datetime import datetime
from pathlib import Path

from chronicle.scanning.context import ScanContext
from chronicle.scanning.scanners.git import GitScanner

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

    observations = GitScanner(repo).scan(ScanContext())

    assert len(observations) == 1
    observation = observations[0]
    assert observation.source == "git"
    assert observation.type == "commit"
    assert observation.external_id == expected_hash
    assert observation.data["hash"] == expected_hash
    assert observation.data["message"] == "initial commit"
    assert isinstance(observation.timestamp, datetime)


def test_git_scanner_keeps_full_message_containing_pipes(tmp_path: Path):
    repo = _init_repo(tmp_path / "repo")
    (repo / "file.txt").write_text("data", encoding="utf-8")
    _commit_all(repo, "fix: handle a | b | c")

    observations = GitScanner(repo).scan(ScanContext())

    assert observations[0].data["message"] == "fix: handle a | b | c"


def test_git_scanner_returns_empty_list_for_repo_without_commits(tmp_path: Path):
    repo = _init_repo(tmp_path / "repo")

    observations = GitScanner(repo).scan(ScanContext())

    assert observations == []


def test_git_scanner_returns_empty_list_on_empty_log_output(
    tmp_path: Path, monkeypatch
):
    scanner = GitScanner(tmp_path)
    monkeypatch.setattr(scanner.git, "run", lambda *arguments: "\n")

    observations = scanner.scan(ScanContext())

    assert observations == []


def test_git_scanner_captures_author_and_parent_chain(tmp_path: Path):
    repo = _init_repo(tmp_path / "repo")
    (repo / "first.txt").write_text("one", encoding="utf-8")
    root_hash = _commit_all(repo, "root commit")
    (repo / "second.txt").write_text("two", encoding="utf-8")
    child_hash = _commit_all(repo, "child commit")

    observations = GitScanner(repo).scan(ScanContext())

    by_hash = {
        observation.external_id: observation for observation in observations
    }
    root = by_hash[root_hash]
    child = by_hash[child_hash]
    assert root.data["parents"] == []
    assert child.data["parents"] == [root_hash]
    assert root.data["author"] == "Chronicle Tests"
    assert child.data["author"] == "Chronicle Tests"


def test_git_scanner_captures_merge_commit_parents(tmp_path: Path):
    repo = _init_repo(tmp_path / "repo")
    (repo / "base.txt").write_text("base", encoding="utf-8")
    _commit_all(repo, "base commit")

    subprocess.run(
        ["git", *GIT_IDENTITY, "checkout", "-b", "feature"],
        cwd=repo,
        capture_output=True,
        check=True,
    )
    (repo / "feature.txt").write_text("feature", encoding="utf-8")
    feature_hash = _commit_all(repo, "feature commit")
    subprocess.run(
        ["git", *GIT_IDENTITY, "checkout", "-"],
        cwd=repo,
        capture_output=True,
        check=True,
    )
    (repo / "main.txt").write_text("main", encoding="utf-8")
    main_tip_hash = _commit_all(repo, "main commit")
    subprocess.run(
        ["git", *GIT_IDENTITY, "merge", "--no-ff", "feature"],
        cwd=repo,
        capture_output=True,
        check=True,
    )
    merge_hash = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        capture_output=True,
        check=True,
        text=True,
    ).stdout.strip()

    observations = GitScanner(repo).scan(ScanContext())

    by_hash = {
        observation.external_id: observation for observation in observations
    }
    merge = by_hash[merge_hash]
    assert merge.data["message"].startswith("Merge branch 'feature'")
    assert sorted(merge.data["parents"]) == sorted(
        [main_tip_hash, feature_hash]
    )


def test_git_scanner_reports_file_change_statuses_per_commit(tmp_path: Path):
    repo = _init_repo(tmp_path / "repo")
    (repo / "bootstrap.txt").write_text("bootstrap", encoding="utf-8")
    _commit_all(repo, "bootstrap")
    (repo / "added.txt").write_text("v1", encoding="utf-8")
    (repo / "doomed.txt").write_text("bye", encoding="utf-8")
    first_hash = _commit_all(repo, "first batch")
    (repo / "added.txt").write_text("v2", encoding="utf-8")
    (repo / "extra.txt").write_text("new", encoding="utf-8")
    (repo / "doomed.txt").unlink()
    second_hash = _commit_all(repo, "second batch")

    observations = GitScanner(repo).scan(ScanContext())

    by_hash = {
        observation.external_id: observation for observation in observations
    }
    first_changes = {
        (change["status"], change["path"])
        for change in by_hash[first_hash].data["changes"]
    }
    second_changes = {
        (change["status"], change["path"])
        for change in by_hash[second_hash].data["changes"]
    }
    assert first_changes == {("A", "added.txt"), ("A", "doomed.txt")}
    assert second_changes == {
        ("M", "added.txt"),
        ("A", "extra.txt"),
        ("D", "doomed.txt"),
    }


def test_git_scanner_incremental_scan_returns_only_new_commits(
    tmp_path: Path,
):
    repo = _init_repo(tmp_path / "repo")
    (repo / "first.txt").write_text("one", encoding="utf-8")
    first_hash = _commit_all(repo, "first commit")

    full_scan = GitScanner(repo).scan(ScanContext())
    checkpoint = ScanContext(state={"git.last_commit": first_hash})
    no_new_commits = GitScanner(repo).scan(checkpoint)

    assert len(full_scan) == 1
    assert no_new_commits == []

    (repo / "second.txt").write_text("two", encoding="utf-8")
    second_hash = _commit_all(repo, "second commit")

    incremental_scan = GitScanner(repo).scan(checkpoint)

    assert [
        observation.external_id for observation in incremental_scan
    ] == [second_hash]


def test_git_scanner_handles_paths_with_spaces_in_changes(tmp_path: Path):
    repo = _init_repo(tmp_path / "repo")
    (repo / "bootstrap.txt").write_text("bootstrap", encoding="utf-8")
    _commit_all(repo, "bootstrap")
    (repo / "my notes.txt").write_text("hello", encoding="utf-8")
    commit_hash = _commit_all(repo, "add spaced file")

    observations = GitScanner(repo).scan(ScanContext())

    by_hash = {
        observation.external_id: observation for observation in observations
    }
    changes = by_hash[commit_hash].data["changes"]
    assert changes == [{"path": "my notes.txt", "status": "A"}]


def test_git_scanner_reports_no_changes_for_root_commit(tmp_path: Path):
    repo = _init_repo(tmp_path / "repo")
    (repo / "README.md").write_text("demo", encoding="utf-8")
    root_hash = _commit_all(repo, "root commit")

    observations = GitScanner(repo).scan(ScanContext())

    by_hash = {
        observation.external_id: observation for observation in observations
    }
    assert by_hash[root_hash].data["changes"] == []


