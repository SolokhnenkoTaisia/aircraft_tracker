import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from aircraft_tracker.aircraft import Aircraft


class StorageError(Exception):
    """Error related to aircraft storage."""


class BaseStorage(ABC):
    """Abstract base class for aircraft storage."""

    @abstractmethod
    def add_aircraft(self, aircraft: Aircraft) -> None:
        """Add an aircraft to storage."""
        pass

    @abstractmethod
    def get_aircraft(self, country: str | None = None) -> list[Aircraft]:
        """Return stored aircraft, optionally filtered by country."""
        pass

    @abstractmethod
    def delete_aircraft(self, icao24: str) -> bool:
        """Delete an aircraft by its ICAO24 code."""
        pass


class JSONSaver(BaseStorage):
    """Store aircraft data in a JSON file."""

    def __init__(self, file_path: str | Path) -> None:
        self._file_path = Path(file_path)

    def _read_data(self) -> list[dict[str, Any]]:
        """Read aircraft data from the JSON file."""
        if not self._file_path.exists():
            return []

        try:
            with self._file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            raise StorageError("Invalid JSON file.") from error
        except OSError as error:
            raise StorageError("Cannot read storage file.") from error

        if not isinstance(data, list):
            raise StorageError("JSON data must be a list.")

        if not all(isinstance(item, dict) for item in data):
            raise StorageError("Invalid aircraft data.")

        required_fields = {
            "icao24",
            "callsign",
            "origin_country",
            "velocity",
            "baro_altitude",
        }

        for item in data:
            if not required_fields.issubset(item):
                raise StorageError("Aircraft data is missing required fields.")

        return data

    def _write_data(self, data: list[dict[str, Any]]) -> None:
        """Write aircraft data to the JSON file."""
        try:
            self._file_path.parent.mkdir(parents=True, exist_ok=True)

            with self._file_path.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        except OSError as error:
            raise StorageError("Cannot write storage file.") from error

    def add_aircraft(self, aircraft: Aircraft) -> None:
        """Add an aircraft to storage."""
        data = self._read_data()

        if any(item.get("icao24") == aircraft.icao24 for item in data):
            raise ValueError("Aircraft already exists.")

        data.append(
            {
                "icao24": aircraft.icao24,
                "callsign": aircraft.callsign,
                "origin_country": aircraft.origin_country,
                "velocity": aircraft.velocity,
                "baro_altitude": aircraft.baro_altitude,
            }
        )

        self._write_data(data)

    def get_aircraft(self, country: str | None = None) -> list[Aircraft]:
        """Return stored aircraft, optionally filtered by country."""
        data = self._read_data()

        try:
            aircraft_list = [
                Aircraft(
                    icao24=item["icao24"],
                    callsign=item["callsign"],
                    origin_country=item["origin_country"],
                    velocity=item["velocity"],
                    baro_altitude=item["baro_altitude"],
                )
                for item in data
            ]
        except (TypeError, ValueError) as error:
            raise StorageError("Invalid aircraft data.") from error

        if country is not None:
            aircraft_list = [
                aircraft
                for aircraft in aircraft_list
                if aircraft.origin_country.casefold() == country.casefold()
            ]

        return aircraft_list

    def delete_aircraft(self, icao24: str) -> bool:
        """Delete an aircraft by its ICAO24 code."""
        data = self._read_data()
        filtered_data = [item for item in data if item.get("icao24") != icao24]

        if len(data) == len(filtered_data):
            return False

        self._write_data(filtered_data)
        return True
