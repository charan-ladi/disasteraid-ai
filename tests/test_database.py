"""Unit tests for database.py and utils/db.py"""

import os
import pytest
import database
from utils import db as utils_db


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    """Point the DBs at a temp file for each test, and initialize them."""
    db_file = tmp_path / "test.db"
    db_file_utils = tmp_path / "test_utils.db"
    monkeypatch.setattr(database, "DB_PATH", str(db_file))
    monkeypatch.setattr(utils_db, "DB_PATH", str(db_file_utils))
    database.init_db()
    utils_db.init_db()
    yield
    if os.path.exists(db_file):
        os.remove(db_file)
    if os.path.exists(db_file_utils):
        os.remove(db_file_utils)


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
    report_id = database.insert_report(
        incident_id, "text", "direct_text", "raw report text"
    )
    assert report_id is not None


def test_utils_db_operations(tmp_path):
    record = {
        "disaster_type": "Earthquake",
        "severity": "High",
        "people_trapped": 5,
        "children": 2,
        "elderly": 1,
        "injuries": True,
        "medical_help": True,
        "food_needed": False,
        "water_needed": True,
        "location": "Downtown",
        "priority_score": 85,
        "status": "Immediate Rescue",
        "engine": "rule_based",
    }
    incident_id = utils_db.save_incident(
        record, source_type="text", source_file="test.txt", raw_text="some raw text"
    )
    assert incident_id is not None

    fetched = utils_db.get_incident(incident_id)
    assert fetched is not None
    assert fetched["disaster_type"] == "Earthquake"
    assert fetched["people_trapped"] == 5

    all_records = utils_db.get_all_incidents()
    assert len(all_records) == 1
    assert all_records[0]["incident_id"] == incident_id

    # test order_by validation
    all_records_invalid_order = utils_db.get_all_incidents(order_by="invalid_column")
    assert len(all_records_invalid_order) == 1

    # export json and csv
    json_path = tmp_path / "export.json"
    csv_path = tmp_path / "export.csv"
    utils_db.export_json(str(json_path))
    utils_db.export_csv(str(csv_path))

    assert json_path.exists()
    assert csv_path.exists()

    utils_db.delete_incident(incident_id)
    assert utils_db.get_incident(incident_id) is None

    # Test export CSV when database is empty
    empty_csv_path = tmp_path / "empty_export.csv"
    utils_db.export_csv(str(empty_csv_path))
    assert empty_csv_path.exists()
