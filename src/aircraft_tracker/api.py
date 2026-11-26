from abc import ABC, abstractmethod

import requests


class BaseAPI(ABC):
    """Abstract base class for working with aircraft data APIs."""

    @abstractmethod
    def get_country_bounds(self, country: str) -> tuple[float, float, float, float]:
        """Return geographic boundaries of a country."""
        pass

    @abstractmethod
    def get_aircraft(
        self,
        bounds: tuple[float, float, float, float],
    ) -> list[list[object | None]]:
        """Return raw aircraft state vectors within geographic boundaries."""
        pass


class APIError(Exception):
    """Exception raised when an API request fails."""


class AircraftAPI(BaseAPI):
    """Class for retrieving country boundaries and aircraft data."""

    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    OPENSKY_URL = "https://opensky-network.org/api/states/all"

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "AircraftTracker/0.1 (educational project)"}
        )

    def get_country_bounds(self, country: str) -> tuple[float, float, float, float]:
        """Get geographic boundaries of a country using Nominatim."""
        if not country.strip():
            raise ValueError("Country name cannot be empty.")

        params: dict[str, str | int] = {
            "q": country,
            "format": "jsonv2",
            "limit": 1,
        }

        try:
            response = self.session.get(
                self.NOMINATIM_URL,
                params=params,
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as error:
            raise APIError("Nominatim request failed.") from error
        except ValueError as error:
            raise APIError("Nominatim returned invalid JSON.") from error

        if not isinstance(data, list) or not data:
            raise APIError(f"Country '{country}' was not found.")

        boundingbox = data[0].get("boundingbox")

        if not isinstance(boundingbox, list) or len(boundingbox) != 4:
            raise APIError("Invalid country boundaries received.")

        try:
            south = float(boundingbox[0])
            north = float(boundingbox[1])
            west = float(boundingbox[2])
            east = float(boundingbox[3])
        except (TypeError, ValueError) as error:
            raise APIError("Country boundaries contain invalid coordinates.") from error

        return south, north, west, east

    def get_aircraft(
        self,
        bounds: tuple[float, float, float, float],
    ) -> list[list[object | None]]:
        """Get aircraft state vectors from OpenSky."""
        south, north, west, east = bounds

        try:
            response = self.session.get(
                self.OPENSKY_URL,
                params={
                    "lamin": south,
                    "lamax": north,
                    "lomin": west,
                    "lomax": east,
                },
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as error:
            raise APIError("OpenSky request failed.") from error
        except ValueError as error:
            raise APIError("OpenSky returned invalid JSON.") from error

        if not isinstance(data, dict):
            raise APIError("OpenSky returned an unexpected response.")

        states = data.get("states")

        if states is None:
            return []

        if not isinstance(states, list):
            raise APIError("Invalid aircraft data received from OpenSky.")

        return [state for state in states if isinstance(state, list)]
