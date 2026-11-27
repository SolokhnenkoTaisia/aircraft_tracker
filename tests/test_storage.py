import json

import pytest

from aircraft_tracker.aircraft import Aircraft
from aircraft_tracker.storage import JSONSaver, StorageError


@pytest.fixture
def storage(tmp_path):
    """Create a temporary JSON storage."""
    return JSONSaver(tmp_path / "aircraft.json")


@pytest.fixture
def aircraft_one():
    return Aircraft("abc123", "ABC123", "Russia", 250.0, 10000.0)


@pytest.fixture
def aircraft_two():
    return Aircraft("def456", "DEF456", "Germany", 200.0, 8000.0)


def test_add_aircraft(storage, aircraft_one):
    storage.add_aircraft(aircraft_one)

    result = storage.get_aircraft()

    assert len(result) == 1
    assert result[0].icao24 == "abc123"


def test_get_aircraft_empty(storage):
    assert storage.get_aircraft() == []


def test_get_aircraft_by_country(storage, aircraft_one, aircraft_two):
    storage.add_aircraft(aircraft_one)
    storage.add_aircraft(aircraft_two)

    result = storage.get_aircraft("russia")

    assert len(result) == 1
    assert result[0].origin_country == "Russia"


def test_get_aircraft_country_case_insensitive(storage, aircraft_one):
    storage.add_aircraft(aircraft_one)

    assert len(storage.get_aircraft("RUSSIA")) == 1


def test_delete_aircraft(storage, aircraft_one):
    storage.add_aircraft(aircraft_one)

    result = storage.delete_aircraft("abc123")

    assert result is True
    assert storage.get_aircraft() == []


def test_delete_nonexistent_aircraft(storage):
    assert storage.delete_aircraft("unknown") is False


def test_duplicate_aircraft(storage, aircraft_one):
    storage.add_aircraft(aircraft_one)

    with pytest.raises(ValueError):
        storage.add_aircraft(aircraft_one)


def test_invalid_json(storage):
    storage._file_path.write_text("{invalid json", encoding="utf-8")

    with pytest.raises(StorageError):
        storage.get_aircraft()


def test_json_must_be_list(storage):
    storage._file_path.write_text('{"aircraft": []}', encoding="utf-8")

    with pytest.raises(StorageError):
        storage.get_aircraft()


def test_json_items_must_be_dicts(storage):
    storage._file_path.write_text("[1, 2, 3]", encoding="utf-8")

    with pytest.raises(StorageError):
        storage.get_aircraft()


def test_saved_data_is_valid_json(storage, aircraft_one):
    storage.add_aircraft(aircraft_one)

    with storage._file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    assert isinstance(data, list)
    assert data[0]["icao24"] == "abc123"
