from datetime import datetime, timedelta
from pathlib import Path
import subprocess

import pytest

from chronicle.scanners.base import Scanner
from chronicle.scanners.git import GitScanner
from chronicle.scanners.git_models import FileChange
from chronicle.scanners.models import Observation
from chronicle.scanning.context import ScanContext

LOG_FORMAT = "%H|%P|%aI|%an|%s"


def _install_fake_git(
    tmp_path: Path,
    monkeypatch,
    log_output: str,
    changed_files: dict[str, str] | None = None,
) -> tuple[GitScanner, list[tuple[str, ...]]]:
    scanner = GitScanner(tmp_path)
    calls = []
    changes = changed_files or {}

    def fake_run(*arguments):
        calls.append(arguments)
        command = arguments[0]
        if command == "log":
            return log_output
        if command == "diff-tree":
            return changes.get(arguments[-1], "")
        raise AssertionError(f"unexpected git command: {arguments}")

    monkeypatch.setattr(scanner.git, "run", fake_run)
    return scanner, calls


def _scanner_with_log(
    tmp_path: Path, log_output: str, monkeypatch
) -> GitScanner:
    scanner, _ = _install_fake_git(tmp_path, monkeypatch, log_output)
    return scanner


def test_git_scanner_parses_commit_line_into_observation(
    tmp_path: Path, monkeypatch
):
    scanner = _scanner_with_log(
        tmp_path,
        "abc123||2026-08-21T12:00:00+00:00|Sakshyam|initial commit",
        monkeypatch,
    )

    observations = scanner.scan(ScanContext())

    assert len(observations) == 1
    observation = observations[0]
    assert observation.source == "git"
    assert observation.type == "commit"
    assert observation.external_id == "abc123"
    expected_timestamp = datetime.fromisoformat("2026-08-21T12:00:00+00:00")
    assert observation.timestamp == expected_timestamp
    assert observation.data["hash"] == "abc123"
    assert observation.data["message"] == "initial commit"
    assert observation.data["author"] == "Sakshyam"
    assert observation.data["parents"] == []
    assert observation.data["changes"] == []


def test_git_scanner_preserves_order_of_multiple_commits(
    tmp_path: Path, monkeypatch
):
    log_output = "\n".join(
        [
            "aaa111||2026-08-20T10:00:00+00:00|dev|first",
            "bbb222|aaa111|2026-08-21T11:00:00+00:00|dev|second",
            "ccc333|bbb222|2026-08-22T12:00:00+00:00|dev|third",
        ]
    )
    scanner = _scanner_with_log(tmp_path, log_output, monkeypatch)

    observations = scanner.scan(ScanContext())

    assert [observation.external_id for observation in observations] == [
        "aaa111",
        "bbb222",
        "ccc333",
    ]
    assert [observation.data["message"] for observation in observations] == [
        "first",
        "second",
        "third",
    ]


def test_git_scanner_skips_blank_lines(tmp_path: Path, monkeypatch):
    log_output = (
        "\n\nabc123||2026-08-21T12:00:00+00:00|dev|only commit\n   \n"
    )
    scanner = _scanner_with_log(tmp_path, log_output, monkeypatch)

    observations = scanner.scan(ScanContext())

    assert [observation.external_id for observation in observations] == [
        "abc123"
    ]


def test_git_scanner_trims_whitespace_around_lines(tmp_path: Path, monkeypatch):
    log_output = "  abc123||2026-08-21T12:00:00+00:00|dev|padded commit  \n"
    scanner = _scanner_with_log(tmp_path, log_output, monkeypatch)

    observations = scanner.scan(ScanContext())

    assert len(observations) == 1
    assert observations[0].external_id == "abc123"
    assert observations[0].data["message"] == "padded commit"


def test_git_scanner_keeps_message_containing_pipes(
    tmp_path: Path, monkeypatch
):
    log_output = (
        "abc123||2026-08-21T12:00:00+00:00|dev|fix: handle a | b | c\n"
    )
    scanner = _scanner_with_log(tmp_path, log_output, monkeypatch)

    observations = scanner.scan(ScanContext())

    assert observations[0].data["message"] == "fix: handle a | b | c"


def test_git_scanner_parses_single_parent(tmp_path: Path, monkeypatch):
    log_output = "child|parent1|2026-08-21T12:00:00+00:00|dev|regular commit"
    scanner = _scanner_with_log(tmp_path, log_output, monkeypatch)

    observations = scanner.scan(ScanContext())

    assert observations[0].data["parents"] == ["parent1"]


def test_git_scanner_parses_merge_commit_parents(tmp_path: Path, monkeypatch):
    log_output = (
        "merge|parent1 parent2|2026-08-21T12:00:00+00:00|dev|merge branch"
    )
    scanner = _scanner_with_log(tmp_path, log_output, monkeypatch)

    observations = scanner.scan(ScanContext())

    assert observations[0].data["parents"] == ["parent1", "parent2"]


def test_git_scanner_returns_empty_list_for_empty_log(
    tmp_path: Path, monkeypatch
):
    scanner = _scanner_with_log(tmp_path, "", monkeypatch)

    assert scanner.scan(ScanContext()) == []


def test_git_scanner_parses_timezone_aware_timestamps(
    tmp_path: Path, monkeypatch
):
    log_output = "abc123||2026-08-21T12:00:00+05:45|dev|nepal commit\n"
    scanner = _scanner_with_log(tmp_path, log_output, monkeypatch)

    observations = scanner.scan(ScanContext())

    assert observations[0].timestamp.utcoffset() == timedelta(
        hours=5, minutes=45
    )


def test_git_scanner_requests_full_history_without_checkpoint(
    tmp_path: Path, monkeypatch
):
    scanner, calls = _install_fake_git(
        tmp_path, monkeypatch, "abc123||2026-08-21T12:00:00+00:00|dev|hi"
    )

    scanner.scan(ScanContext())

    assert calls[0] == ("log", f"--format={LOG_FORMAT}")


def test_git_scanner_requests_only_commits_after_checkpoint(
    tmp_path: Path, monkeypatch
):
    scanner, calls = _install_fake_git(
        tmp_path, monkeypatch, "abc123||2026-08-21T12:00:00+00:00|dev|hi"
    )
    context = ScanContext(state={"git.last_commit": "oldhash"})

    scanner.scan(context)

    assert calls[0] == ("log", "oldhash..HEAD", f"--format={LOG_FORMAT}")


def test_git_scanner_looks_up_last_commit_under_git_namespace(
    tmp_path: Path, monkeypatch
):
    seen_keys = []
    scanner = GitScanner(tmp_path)

    class RecordingContext(ScanContext):
        def get_state(self, scanner_name: str, key: str) -> str | None:
            seen_keys.append((scanner_name, key))
            return None

    scanner.scan(RecordingContext())

    assert seen_keys == [("git", "last_commit")]


def test_git_scanner_embeds_changed_files_into_observation(
    tmp_path: Path, monkeypatch
):
    scanner, _ = _install_fake_git(
        tmp_path,
        monkeypatch,
        log_output="abc123||2026-08-21T12:00:00+00:00|dev|feature work",
        changed_files={
            "abc123": "M\tsrc/app.py\nA\tsrc/new.py\nD\tsrc/old.py\n"
        },
    )

    observations = scanner.scan(ScanContext())

    changes = observations[0].data["changes"]
    assert changes == [
        {"path": "src/app.py", "status": "M"},
        {"path": "src/new.py", "status": "A"},
        {"path": "src/old.py", "status": "D"},
    ]


def test_git_scanner_fetches_changes_for_every_parsed_commit(
    tmp_path: Path, monkeypatch
):
    scanner, calls = _install_fake_git(
        tmp_path,
        monkeypatch,
        log_output="\n".join(
            [
                "aaa111||2026-08-20T10:00:00+00:00|dev|first",
                "bbb222|aaa111|2026-08-21T11:00:00+00:00|dev|second",
            ]
        ),
        changed_files={"aaa111": "A\tone.txt\n", "bbb222": "M\tone.txt\n"},
    )

    observations = scanner.scan(ScanContext())

    diff_tree_calls = [call for call in calls if call[0] == "diff-tree"]
    assert diff_tree_calls == [
        ("diff-tree", "--no-commit-id", "--name-status", "-r", "aaa111"),
        ("diff-tree", "--no-commit-id", "--name-status", "-r", "bbb222"),
    ]
    assert observations[0].data["changes"] == [
        {"path": "one.txt", "status": "A"}
    ]
    assert observations[1].data["changes"] == [
        {"path": "one.txt", "status": "M"}
    ]


def test_get_changed_file_parses_all_status_types(tmp_path: Path, monkeypatch):
    scanner = GitScanner(tmp_path)
    monkeypatch.setattr(
        scanner.git,
        "run",
        lambda *arguments: "A\tadded.txt\nM\tmodified.txt\nD\tdeleted.txt\n",
    )

    changes = scanner.get_changed_file("abc123")

    assert changes == [
        FileChange(path="added.txt", status="A"),
        FileChange(path="modified.txt", status="M"),
        FileChange(path="deleted.txt", status="D"),
    ]


def test_get_changed_file_skips_blank_lines(tmp_path: Path, monkeypatch):
    scanner = GitScanner(tmp_path)
    monkeypatch.setattr(
        scanner.git,
        "run",
        lambda *arguments: "\nA\tone.txt\n   \n",
    )

    changes = scanner.get_changed_file("abc123")

    assert changes == [FileChange(path="one.txt", status="A")]


def test_get_changed_file_returns_empty_list_for_root_style_empty_output(
    tmp_path: Path, monkeypatch
):
    scanner = GitScanner(tmp_path)
    monkeypatch.setattr(scanner.git, "run", lambda *arguments: "")

    assert scanner.get_changed_file("abc123") == []


def test_git_scanner_returns_empty_list_when_git_log_fails(
    tmp_path: Path, monkeypatch
):
    scanner = GitScanner(tmp_path)

    def failing_run(*arguments):
        raise subprocess.CalledProcessError(128, ["git", "log"])

    monkeypatch.setattr(scanner.git, "run", failing_run)

    assert scanner.scan(ScanContext()) == []


def test_git_scanner_stores_project_root(tmp_path: Path):
    scanner = GitScanner(tmp_path)

    assert scanner.project_root == tmp_path


def test_scanner_cannot_be_instantiated_directly(tmp_path: Path):
    with pytest.raises(TypeError):
        Scanner(tmp_path)


def test_scanner_subclass_must_implement_scan(tmp_path: Path):
    class IncompleteScanner(Scanner):
        pass

    with pytest.raises(TypeError):
        IncompleteScanner(tmp_path)


def test_scanner_concrete_subclass_receives_context(tmp_path: Path):
    received = []

    class RecordingScanner(Scanner):
        def scan(self, context: ScanContext) -> list[Observation]:
            received.append(context)
            return []

    RecordingScanner(tmp_path).scan(ScanContext())

    assert len(received) == 1
    assert isinstance(received[0], ScanContext)


def test_observation_holds_scan_data():
    timestamp = datetime(2026, 8, 21, 12, 0, 0)

    observation = Observation(
        source="git",
        type="commit",
        external_id="abc123",
        timestamp=timestamp,
        data={"hash": "abc123", "message": "hello"},
    )

    assert observation.source == "git"
    assert observation.type == "commit"
    assert observation.external_id == "abc123"
    assert observation.timestamp == timestamp
    assert observation.data["hash"] == "abc123"
    assert observation.data["message"] == "hello"


def test_observations_with_same_values_are_equal():
    timestamp = datetime(2026, 8, 21, 12, 0, 0)

    first = Observation("git", "commit", "abc", timestamp, {"hash": "abc"})
    second = Observation("git", "commit", "abc", timestamp, {"hash": "abc"})

    assert first == second


def test_observations_with_different_external_id_are_not_equal():
    timestamp = datetime(2026, 8, 21, 12, 0, 0)

    first = Observation("git", "commit", "abc", timestamp, {})
    second = Observation("git", "commit", "def", timestamp, {})

    assert first != second


def test_file_change_holds_path_and_status():
    change = FileChange(path="src/main.py", status="M")

    assert change.path == "src/main.py"
    assert change.status == "M"


def test_file_changes_with_same_values_are_equal():
    assert FileChange("a.txt", "A") == FileChange("a.txt", "A")
    assert FileChange("a.txt", "A") != FileChange("a.txt", "M")
    assert FileChange("a.txt", "A") != FileChange("b.txt", "A")
