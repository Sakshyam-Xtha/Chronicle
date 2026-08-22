from datetime import datetime, timedelta
from pathlib import Path
import subprocess

import pytest

from chronicle.scanners.base import Scanner
from chronicle.scanners.git import GitScanner
from chronicle.scanners.models import Observation


def _scanner_with_log(
    tmp_path: Path, log_output: str, monkeypatch
) -> GitScanner:
    scanner = GitScanner(tmp_path)
    monkeypatch.setattr(scanner.git, "run", lambda *arguments: log_output)
    return scanner


def test_git_scanner_parses_commit_line_into_observation(
    tmp_path: Path, monkeypatch
):
    scanner = _scanner_with_log(
        tmp_path,
        "abc123|2026-08-21T12:00:00+00:00|initial commit",
        monkeypatch,
    )

    observations = scanner.scan()

    assert len(observations) == 1
    observation = observations[0]
    assert observation.source == "git"
    assert observation.type == "commit"
    assert observation.external_id == "abc123"
    expected_timestamp = datetime.fromisoformat("2026-08-21T12:00:00+00:00")
    assert observation.timestamp == expected_timestamp
    assert observation.data == {"hash": "abc123", "message": "initial commit"}


def test_git_scanner_preserves_order_of_multiple_commits(
    tmp_path: Path, monkeypatch
):
    log_output = "\n".join(
        [
            "aaa111|2026-08-20T10:00:00+00:00|first",
            "bbb222|2026-08-21T11:00:00+00:00|second",
            "ccc333|2026-08-22T12:00:00+00:00|third",
        ]
    )
    scanner = _scanner_with_log(tmp_path, log_output, monkeypatch)

    observations = scanner.scan()

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
    log_output = "\n\nabc123|2026-08-21T12:00:00+00:00|only commit\n   \n"
    scanner = _scanner_with_log(tmp_path, log_output, monkeypatch)

    observations = scanner.scan()

    assert [observation.external_id for observation in observations] == [
        "abc123"
    ]


def test_git_scanner_trims_whitespace_around_lines(tmp_path: Path, monkeypatch):
    log_output = "  abc123|2026-08-21T12:00:00+00:00|padded commit  \n"
    scanner = _scanner_with_log(tmp_path, log_output, monkeypatch)

    observations = scanner.scan()

    assert len(observations) == 1
    assert observations[0].external_id == "abc123"
    assert observations[0].data["message"] == "padded commit"


def test_git_scanner_keeps_message_containing_pipes(
    tmp_path: Path, monkeypatch
):
    log_output = "abc123|2026-08-21T12:00:00+00:00|fix: handle a | b | c\n"
    scanner = _scanner_with_log(tmp_path, log_output, monkeypatch)

    observations = scanner.scan()

    assert observations[0].data["message"] == "fix: handle a | b | c"


def test_git_scanner_returns_empty_list_for_empty_log(
    tmp_path: Path, monkeypatch
):
    scanner = _scanner_with_log(tmp_path, "", monkeypatch)

    assert scanner.scan() == []


def test_git_scanner_parses_timezone_aware_timestamps(
    tmp_path: Path, monkeypatch
):
    log_output = "abc123|2026-08-21T12:00:00+05:45|nepal commit\n"
    scanner = _scanner_with_log(tmp_path, log_output, monkeypatch)

    observations = scanner.scan()

    assert observations[0].timestamp.utcoffset() == timedelta(
        hours=5, minutes=45
    )


def test_git_scanner_returns_empty_list_when_git_log_fails(
    tmp_path: Path, monkeypatch
):
    scanner = GitScanner(tmp_path)

    def failing_run(*arguments):
        raise subprocess.CalledProcessError(128, ["git", "log"])

    monkeypatch.setattr(scanner.git, "run", failing_run)

    assert scanner.scan() == []


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


def test_scanner_concrete_subclass_can_scan(tmp_path: Path):
    class RecordingScanner(Scanner):
        def scan(self) -> list[Observation]:
            return [
                Observation(
                    source="recording",
                    type="ping",
                    external_id="1",
                    timestamp=datetime(2026, 8, 21),
                    data={"root": str(self.project_root)},
                )
            ]

    observations = RecordingScanner(tmp_path).scan()

    assert len(observations) == 1
    assert observations[0].source == "recording"
    assert observations[0].data["root"] == str(tmp_path)


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
