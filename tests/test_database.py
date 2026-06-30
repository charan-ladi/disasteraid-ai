"""Unit tests for database.py"""

import os

import pytest

import database


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    """Point the DB at a temp file for each test, and initialize it."""
    db_file = tmp_path / "test.db"
    monkeypatch.setattr(database, "DB_PATH", str(db_file))
    database.init_db()
    yield
    if os.path.exists(db_file):
        os.remove(db_file)


def test_insert_and_fetch_incident():
    incident_id = database.insert_incident(
        {
            "disaster_type": "Flood",
            "severity": "Critical",
            "people_trapped": 4,
            "location": "Old Bridge",
            "priority_score": 96,
        }
    )
    assert incident_id is not None

    record = database.get_incident_by_id(incident_id)
    assert record["disaster_type"] == "Flood"
    assert record["severity"] == "Critical"
    assert record["location"] == "Old Bridge"


def test_get_all_incidents_returns_list():
    database.insert_incident({"disaster_type": "Fire", "severity": "High"})
    database.insert_incident({"disaster_type": "Cyclone", "severity": "Medium"})

    all_incidents = database.get_all_incidents()
    assert len(all_incidents) == 2


def test_search_incidents_by_location():
    database.insert_incident({"disaster_type": "Flood", "location": "Riverside"})
    database.insert_incident({"disaster_type": "Fire", "location": "Downtown"})

    results = database.search_incidents("Riverside")
    assert len(results) == 1
    assert results[0]["location"] == "Riverside"


def test_insert_report_links_to_incident():
    incident_id = database.insert_incident({"disaster_type": "Flood"})
    report_id = database.insert_report(incident_id, "text", "direct_text", "raw report text")
    assert report_id is not None
