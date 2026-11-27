import pytest
import requests

from aircraft_tracker.api import AircraftAPI, APIError


@pytest.fixture
def api() -> AircraftAPI:
    return AircraftAPI()


def test_get_country_bounds_success(
    api: AircraftAPI, monkeypatch: pytest.MonkeyPatch
) -> None:
    def mock_get(*args: object, **kwargs: object) -> requests.Response:
        response = requests.Response()
        response.status_code = 200
        response._content = b'[{"boundingbox": ["40.0", "60.0", "20.0", "50.0"]}]'
        return response

    monkeypatch.setattr(api.session, "get", mock_get)

    result = api.get_country_bounds("Poland")

    assert result == (40.0, 60.0, 20.0, 50.0)


def test_get_country_bounds_empty_country(api: AircraftAPI) -> None:
    with pytest.raises(ValueError):
        api.get_country_bounds("   ")


def test_get_country_bounds_not_found(
    api: AircraftAPI, monkeypatch: pytest.MonkeyPatch
) -> None:
    def mock_get(*args: object, **kwargs: object) -> requests.Response:
        response = requests.Response()
        response.status_code = 200
        response._content = b"[]"
        return response

    monkeypatch.setattr(api.session, "get", mock_get)

    with pytest.raises(APIError):
        api.get_country_bounds("UnknownCountry")


def test_get_country_bounds_invalid_response(
    api: AircraftAPI, monkeypatch: pytest.MonkeyPatch
) -> None:
    def mock_get(*args: object, **kwargs: object) -> requests.Response:
        response = requests.Response()
        response.status_code = 200
        response._content = b'["unexpected"]'
        return response

    monkeypatch.setattr(api.session, "get", mock_get)

    with pytest.raises(APIError):
        api.get_country_bounds("Poland")


def test_get_aircraft_success(
    api: AircraftAPI, monkeypatch: pytest.MonkeyPatch
) -> None:
    def mock_get(*args: object, **kwargs: object) -> requests.Response:
        response = requests.Response()
        response.status_code = 200
        response._content = b'{"states": [["abc123", "ABC123"]]}'
        return response

    monkeypatch.setattr(api.session, "get", mock_get)

    result = api.get_aircraft((40.0, 60.0, 20.0, 50.0))

    assert result == [["abc123", "ABC123"]]


def test_get_aircraft_empty(api: AircraftAPI, monkeypatch: pytest.MonkeyPatch) -> None:
    def mock_get(*args: object, **kwargs: object) -> requests.Response:
        response = requests.Response()
        response.status_code = 200
        response._content = b'{"states": null}'
        return response

    monkeypatch.setattr(api.session, "get", mock_get)

    result = api.get_aircraft((40.0, 60.0, 20.0, 50.0))

    assert result == []
