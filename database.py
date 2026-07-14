"""
database.py
SQLite persistence layer for DisasterAid AI.
"""

import sqlite3
from contextlib import contextmanager
from typing import Any

DB_PATH = "data/disasteraid.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS incidents (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    disaster_type   TEXT,
    severity        TEXT,
    people_trapped  INTEGER DEFAULT 0,
    children        INTEGER DEFAULT 0,
    elderly         INTEGER DEFAULT 0,
    injured         BOOLEAN DEFAULT 0,
    food_needed     BOOLEAN DEFAULT 0,
    water_needed    BOOLEAN DEFAULT 0,
    medicine_needed BOOLEAN DEFAULT 0,
    location        TEXT,
    latitude        REAL,
    longitude       REAL,
    timestamp       TEXT DEFAULT CURRENT_TIMESTAMP,
    status          TEXT DEFAULT 'Pending',
    priority_score  INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS reports (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id     INTEGER REFERENCES incidents(id),
    source_type     TEXT,
    filename        TEXT,
    extracted_text  TEXT
);
"""


@contextmanager
def get_connection():
    """Yield a SQLite connection with row factory set to dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """Create tables if they do not already exist."""
    import os

    os.makedirs("data", exist_ok=True)
    with get_connection() as conn:
        conn.executescript(SCHEMA)


def insert_incident(data: dict[str, Any]) -> int:
    """Insert a structured incident record. Returns the new incident id."""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO incidents (
                disaster_type, severity, people_trapped, children, elderly,
                injured, food_needed, water_needed, medicine_needed,
                location, latitude, longitude, status, priority_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("disaster_type"),
                data.get("severity"),
                data.get("people_trapped", 0),
                data.get("children", 0),
                data.get("elderly", 0),
                data.get("injuries", False),
                data.get("food_needed", False),
                data.get("water_needed", False),
                data.get("medicine_needed", False),
                data.get("location"),
                data.get("latitude"),
                data.get("longitude"),
                data.get("status", "Pending"),
                data.get("priority_score", 0),
            ),
        )
        return cursor.lastrowid


def insert_report(
    incident_id: int, source_type: str, filename: str, extracted_text: str
) -> int:
    """Insert a raw report record linked to an incident."""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO reports (incident_id, source_type, filename, extracted_text)
            VALUES (?, ?, ?, ?)
            """,
            (incident_id, source_type, filename, extracted_text),
        )
        return cursor.lastrowid


def get_all_incidents() -> list[dict[str, Any]]:
    """Return all incidents ordered by most recent first."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM incidents ORDER BY timestamp DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def get_incident_by_id(incident_id: int) -> dict[str, Any] | None:
    """Return a single incident by id, or None if not found."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM incidents WHERE id = ?", (incident_id,)
        ).fetchone()
        return dict(row) if row else None


def search_incidents(keyword: str) -> list[dict[str, Any]]:
    """Search incidents by disaster_type or location keyword."""
    with get_connection() as conn:
        like = f"%{keyword}%"
        rows = conn.execute(
            """
            SELECT * FROM incidents
            WHERE disaster_type LIKE ? OR location LIKE ?
            ORDER BY timestamp DESC
            """,
            (like, like),
        ).fetchall()
        return [dict(row) for row in rows]


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
