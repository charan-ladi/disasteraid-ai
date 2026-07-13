"""
db.py
-----
SQLite persistence layer for structured incident records.
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "disasteraid.db"
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS incidents (
    incident_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type     TEXT,
    source_file     TEXT,
    raw_text        TEXT,
    disaster_type   TEXT,
    severity        TEXT,
    people_trapped  INTEGER,
    children        INTEGER,
    elderly         INTEGER,
    injuries        INTEGER,
    medical_help    INTEGER,
    food_needed     INTEGER,
    water_needed    INTEGER,
    location        TEXT,
    priority_score  INTEGER,
    status          TEXT,
    engine          TEXT,
    created_at      TEXT
);
"""


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(SCHEMA)
    conn.commit()
    conn.close()


def save_incident(record, source_type="text", source_file=None, raw_text=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO incidents
           (source_type, source_file, raw_text, disaster_type, severity,
            people_trapped, children, elderly, injuries, medical_help,
            food_needed, water_needed, location, priority_score, status,
            engine, created_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            source_type,
            source_file,
            raw_text,
            record.get("disaster_type"),
            record.get("severity"),
            int(record.get("people_trapped", 0)),
            int(record.get("children", 0)),
            int(record.get("elderly", 0)),
            int(bool(record.get("injuries"))),
            int(bool(record.get("medical_help"))),
            int(bool(record.get("food_needed"))),
            int(bool(record.get("water_needed"))),
            record.get("location"),
            int(record.get("priority_score", 0)),
            record.get("status"),
            record.get("engine"),
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    incident_id = cur.lastrowid
    conn.close()
    return incident_id


def get_all_incidents(order_by="priority_score DESC"):
    allowed_orders = {
        "priority_score DESC",
        "priority_score ASC",
        "created_at DESC",
        "created_at ASC",
        "incident_id DESC",
        "incident_id ASC",
    }
    if order_by not in allowed_orders:
        order_by = "priority_score DESC"

    conn = get_connection()
    query = f"SELECT * FROM incidents ORDER BY {order_by}"  # nosec B608
    rows = conn.execute(query).fetchall()  # nosec B608

    conn.close()
    return [dict(r) for r in rows]


def get_incident(incident_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM incidents WHERE incident_id = ?", (incident_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_incident(incident_id):
    conn = get_connection()
    conn.execute("DELETE FROM incidents WHERE incident_id = ?", (incident_id,))
    conn.commit()
    conn.close()


def export_json(path):
    incidents = get_all_incidents()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(incidents, f, indent=2)
    return path


def export_csv(path):
    import csv

    incidents = get_all_incidents()
    if not incidents:
        with open(path, "w") as f:
            f.write("")
        return path
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=incidents[0].keys())
        writer.writeheader()
        writer.writerows(incidents)
    return path


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
