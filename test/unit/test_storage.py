import json
import sqlite3
from datetime import datetime
from pathlib import Path

import pytest

from chronicle.scanners.models import Observation
from chronicle.storage.database import connect
from chronicle.storage.observations import ObservationRepo
from chronicle.storage.schema import init_schema


def _observation(**overrides) -> Observation:
    values = {
        "source": "git",
        "type": "commit",
        "external_id": "abc123",
        "timestamp": datetime(2026, 8, 21, 12, 0, 0),
        "data": {"hash": "abc123", "message": "initial commit"},
    }
    values.update(overrides)
    return Observation(**values)


def _repo(tmp_path: Path) -> tuple[ObservationRepo, sqlite3.Connection]:
    connection = connect(tmp_path / "chronicle.db")
    init_schema(connection)
    return ObservationRepo(connection), connection


def _fetch_all(connection: sqlite3.Connection) -> list[sqlite3.Row]:
    return connection.execute("SELECT * FROM observations").fetchall()


def test_connect_returns_sqlite_connection(tmp_path: Path):
    connection = connect(tmp_path / "chronicle.db")

    assert isinstance(connection, sqlite3.Connection)
    connection.close()


def test_connect_rows_are_accessible_by_column_name(tmp_path: Path):
    connection = connect(tmp_path / "chronicle.db")
    connection.execute("CREATE TABLE t(name TEXT)")
    connection.execute("INSERT INTO t VALUES ('chronicle')")

    row = connection.execute("SELECT name FROM t").fetchone()

    assert row["name"] == "chronicle"
    connection.close()


def test_init_schema_creates_observations_table():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    init_schema(connection)

    tables = [
        row["name"]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    ]
    assert "observations" in tables
    connection.close()


def test_init_schema_is_idempotent():
    connection = sqlite3.connect(":memory:")

    init_schema(connection)
    init_schema(connection)

    connection.close()


def test_observations_identity_is_unique():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    init_schema(connection)
    connection.execute(
        "INSERT INTO observations(source, type, external_id, timestamp, data)"
        " VALUES ('git', 'commit', 'abc123', '2026-08-21T12:00:00', '{}')"
    )

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            "INSERT INTO observations(source, type, external_id,"
            " timestamp, data)"
            " VALUES ('git', 'commit', 'abc123', '2026-08-22T12:00:00', '{}')"
        )

    connection.close()


def test_save_returns_true_for_new_observation(tmp_path: Path):
    repo, _ = _repo(tmp_path)

    assert repo.save(_observation()) is True


def test_save_returns_false_for_duplicate_observation(tmp_path: Path):
    repo, _ = _repo(tmp_path)
    repo.save(_observation())

    duplicate = repo.save(
        _observation(
            timestamp=datetime(2026, 8, 22, 9, 30, 0),
            data={"hash": "abc123", "message": "amended"},
        )
    )

    assert duplicate is False


def test_duplicate_save_keeps_original_row(tmp_path: Path):
    repo, connection = _repo(tmp_path)
    repo.save(_observation())
    repo.save(
        _observation(data={"hash": "abc123", "message": "overwritten?"})
    )

    rows = _fetch_all(connection)

    assert len(rows) == 1
    assert json.loads(rows[0]["data"])["message"] == "initial commit"


def test_save_persists_observation_fields(tmp_path: Path):
    repo, connection = _repo(tmp_path)
    timestamp = datetime(2026, 8, 21, 12, 0, 0)

    repo.save(_observation(timestamp=timestamp))

    row = _fetch_all(connection)[0]
    assert row["source"] == "git"
    assert row["type"] == "commit"
    assert row["external_id"] == "abc123"
    assert row["timestamp"] == "2026-08-21T12:00:00"
    assert json.loads(row["data"]) == {
        "hash": "abc123",
        "message": "initial commit",
    }


def test_save_serializes_nested_data_as_json(tmp_path: Path):
    repo, connection = _repo(tmp_path)

    repo.save(
        _observation(data={"files": ["a.py", "b.py"], "stats": {"+": 10}})
    )

    stored_data = json.loads(_fetch_all(connection)[0]["data"])
    assert stored_data == {"files": ["a.py", "b.py"], "stats": {"+": 10}}


def test_same_external_id_is_allowed_across_sources(tmp_path: Path):
    repo, connection = _repo(tmp_path)

    first = repo.save(_observation(source="git"))
    second = repo.save(_observation(source="github"))

    assert first is True
    assert second is True
    assert len(_fetch_all(connection)) == 2


def test_multiple_distinct_observations_are_all_persisted(tmp_path: Path):
    repo, connection = _repo(tmp_path)

    for index in range(3):
        repo.save(_observation(external_id=f"commit-{index}"))

    rows = _fetch_all(connection)

    assert len(rows) == 3
    assert {row["external_id"] for row in rows} == {
        "commit-0",
        "commit-1",
        "commit-2",
    }
