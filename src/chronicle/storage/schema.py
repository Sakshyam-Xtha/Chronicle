import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS observations(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    type TEXT NOT NULL,
    external_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    data TEXT NOT NULL,
    UNIQUE(source,type,external_id)
);

CREATE TABLE IF NOT EXISTS scan_state(
    scanner TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY(scanner , key)
)
"""

def init_schema(connection:sqlite3.Connection) -> None:
    connection.executescript(SCHEMA)
    connection.commit()