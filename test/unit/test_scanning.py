from datetime import datetime
from pathlib import Path

from chronicle.scanners.base import Scanner
from chronicle.scanners.models import Observation
from chronicle.scanning.context import ScanContext
from chronicle.scanning.engine import ScanEngine


def _observation(external_id: str) -> Observation:
    return Observation(
        source="git",
        type="commit",
        external_id=external_id,
        timestamp=datetime(2026, 8, 21, 12, 0, 0),
        data={"hash": external_id},
    )


class StubScanner(Scanner):
    def __init__(self, project_root: Path, external_ids: list[str]) -> None:
        super().__init__(project_root)
        self.external_ids = external_ids

    def scan(self, context: ScanContext) -> list[Observation]:
        return [_observation(external_id) for external_id in self.external_ids]


def test_scan_context_returns_state_for_namespaced_key():
    context = ScanContext(state={"git.last_commit": "abc123"})

    assert context.get_state("git", "last_commit") == "abc123"


def test_scan_context_returns_none_for_missing_key():
    context = ScanContext(state={"git.last_commit": "abc123"})

    assert context.get_state("git", "other_key") is None


def test_scan_context_returns_none_for_missing_scanner():
    context = ScanContext(state={"git.last_commit": "abc123"})

    assert context.get_state("filesystem", "last_commit") is None


def test_scan_context_defaults_to_empty_state():
    context = ScanContext()

    assert context.state == {}
    assert context.get_state("git", "last_commit") is None


def test_scan_engine_aggregates_observations_from_all_scanners(
    tmp_path: Path,
):
    engine = ScanEngine(
        project_root=tmp_path,
        scanners=[
            StubScanner(tmp_path, ["a", "b"]),
            StubScanner(tmp_path, ["c"]),
        ],
    )

    observations = engine.scan(context=ScanContext())

    assert [observation.external_id for observation in observations] == [
        "a",
        "b",
        "c",
    ]


def test_scan_engine_passes_context_to_every_scanner(tmp_path: Path):
    received = []

    class ContextRecorder(Scanner):
        def scan(self, context: ScanContext) -> list[Observation]:
            received.append(context)
            return []

    engine = ScanEngine(
        project_root=tmp_path,
        scanners=[ContextRecorder(tmp_path), ContextRecorder(tmp_path)],
    )
    context = ScanContext(state={"git.last_commit": "abc123"})

    engine.scan(context=context)

    assert received == [context, context]


def test_scan_engine_returns_empty_list_without_scanners(tmp_path: Path):
    engine = ScanEngine(project_root=tmp_path, scanners=[])

    assert engine.scan(context=ScanContext()) == []


def test_scan_engine_stores_project_root(tmp_path: Path):
    engine = ScanEngine(
        project_root=tmp_path,
        scanners=[StubScanner(tmp_path, [])],
    )

    assert engine.project_root == tmp_path
