import pytest

from aircraft_tracker.aircraft import Aircraft


@pytest.fixture
def aircraft_one() -> Aircraft:
    return Aircraft(
        icao24="abc123",
        callsign="AFL123",
        origin_country="Russia",
        velocity=250.0,
        baro_altitude=10000.0,
    )


@pytest.fixture
def aircraft_two() -> Aircraft:
    return Aircraft(
        icao24="def456",
        callsign="S7 456",
        origin_country="Germany",
        velocity=200.0,
        baro_altitude=8000.0,
    )


def test_aircraft_creation(aircraft_one: Aircraft) -> None:
    assert aircraft_one.icao24 == "abc123"
    assert aircraft_one.callsign == "AFL123"
    assert aircraft_one.origin_country == "Russia"
    assert aircraft_one.velocity == 250.0
    assert aircraft_one.baro_altitude == 10000.0


def test_aircraft_empty_icao24() -> None:
    with pytest.raises(ValueError):
        Aircraft("", "AFL123", "Russia", 250.0, 10000.0)


def test_aircraft_empty_country() -> None:
    with pytest.raises(ValueError):
        Aircraft("abc123", "AFL123", " ", 250.0, 10000.0)


def test_aircraft_invalid_velocity() -> None:
    with pytest.raises(ValueError):
        Aircraft("abc123", "AFL123", "Russia", -10.0, 10000.0)


def test_aircraft_invalid_altitude() -> None:
    with pytest.raises(ValueError):
        Aircraft("abc123", "AFL123", "Russia", 250.0, "high")  # type: ignore[arg-type]


def test_compare_speed_greater(aircraft_one: Aircraft, aircraft_two: Aircraft) -> None:
    assert aircraft_one.compare_speed(aircraft_two) == 1


def test_compare_speed_less(aircraft_one: Aircraft, aircraft_two: Aircraft) -> None:
    assert aircraft_two.compare_speed(aircraft_one) == -1


def test_compare_altitude_greater(
    aircraft_one: Aircraft, aircraft_two: Aircraft
) -> None:
    assert aircraft_one.compare_altitude(aircraft_two) == 1


def test_compare_altitude_equal() -> None:
    aircraft_one = Aircraft("abc123", None, "Russia", 250.0, 10000.0)
    aircraft_two = Aircraft("def456", None, "Germany", 200.0, 10000.0)

    assert aircraft_one.compare_altitude(aircraft_two) == 0


def test_compare_speed_unknown() -> None:
    aircraft_one = Aircraft("abc123", None, "Russia", None, 10000.0)
    aircraft_two = Aircraft("def456", None, "Germany", 200.0, 8000.0)

    with pytest.raises(ValueError):
        aircraft_one.compare_speed(aircraft_two)


def test_compare_altitude_unknown() -> None:
    aircraft_one = Aircraft("abc123", None, "Russia", 250.0, None)
    aircraft_two = Aircraft("def456", None, "Germany", 200.0, 8000.0)

    with pytest.raises(ValueError):
        aircraft_one.compare_altitude(aircraft_two)
