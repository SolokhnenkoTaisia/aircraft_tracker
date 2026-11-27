import pytest

from aircraft_tracker.aircraft import Aircraft
from aircraft_tracker.console import (
    convert_to_aircraft,
    filter_by_country,
    get_top_aircraft,
    print_aircraft,
    run_console,
)


def create_aircraft(
    icao24: str,
    country: str,
    altitude: float | None,
) -> Aircraft:
    return Aircraft(
        icao24=icao24,
        callsign="TEST123",
        origin_country=country,
        velocity=250.0,
        baro_altitude=altitude,
    )


def test_convert_to_aircraft():
    states = [
        [
            "abc123",
            "TEST123 ",
            "United States",
            123,
            123,
            None,
            None,
            10000.0,
            False,
            250.0,
        ]
    ]

    result = convert_to_aircraft(states)

    assert len(result) == 1
    assert result[0].icao24 == "abc123"
    assert result[0].callsign == "TEST123"
    assert result[0].baro_altitude == 10000.0


def test_convert_to_aircraft_invalid_state():
    states = [
        ["abc123", "TEST123"],
        [123, "TEST123", "USA", None, None, None, None, 10000, False, 250],
    ]

    assert convert_to_aircraft(states) == []


def test_get_top_aircraft():
    aircraft = [
        create_aircraft("abc123", "USA", 5000),
        create_aircraft("def456", "Germany", 12000),
        create_aircraft("ghi789", "France", 8000),
        create_aircraft("jkl012", "Japan", None),
    ]

    result = get_top_aircraft(aircraft, 2)

    assert len(result) == 2
    assert result[0].icao24 == "def456"
    assert result[1].icao24 == "ghi789"


def test_get_top_aircraft_invalid_count():
    with pytest.raises(ValueError):
        get_top_aircraft([], 0)


def test_filter_by_country():
    aircraft = [
        create_aircraft("abc123", "USA", 5000),
        create_aircraft("def456", "Germany", 12000),
        create_aircraft("ghi789", "USA", 8000),
    ]

    result = filter_by_country(aircraft, "usa")

    assert len(result) == 2
    assert all(item.origin_country == "USA" for item in result)


def test_filter_by_country_empty():
    with pytest.raises(ValueError):
        filter_by_country([], "   ")


def test_print_aircraft(capsys):
    aircraft = [
        create_aircraft("abc123", "USA", 10000),
    ]

    print_aircraft(aircraft)

    output = capsys.readouterr().out

    assert "abc123" in output
    assert "USA" in output
    assert "10000.0 м" in output


def test_print_aircraft_empty(capsys):
    print_aircraft([])

    output = capsys.readouterr().out

    assert "Самолёты не найдены." in output


def test_run_console(monkeypatch, capsys):
    from aircraft_tracker import console

    states = [
        [
            "abc123",
            "TEST1",
            "USA",
            123,
            123,
            None,
            None,
            10000.0,
            False,
            250.0,
        ],
        [
            "def456",
            "TEST2",
            "Germany",
            123,
            123,
            None,
            None,
            8000.0,
            False,
            230.0,
        ],
    ]

    class FakeAPI:
        def get_country_bounds(self, country):
            return (0.0, 1.0, 0.0, 1.0)

        def get_aircraft(self, bounds):
            return states

    class FakeStorage:
        def __init__(self, file_path):
            self.aircraft = []

        def get_aircraft(self):
            return self.aircraft

        def add_aircraft(self, aircraft):
            self.aircraft.append(aircraft)

    monkeypatch.setattr(console, "AircraftAPI", FakeAPI)
    monkeypatch.setattr(console, "JSONSaver", FakeStorage)

    answers = iter(["USA", "1", "USA"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    run_console()

    output = capsys.readouterr().out

    assert "Найдено самолётов: 2" in output
    assert "Новых самолётов сохранено: 2" in output
    assert "abc123" in output
    assert "Самолёты, зарегистрированные в USA" in output
