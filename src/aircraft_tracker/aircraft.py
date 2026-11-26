class Aircraft:
    """Class representing an aircraft."""

    def __init__(
        self,
        icao24: str,
        callsign: str | None,
        origin_country: str,
        velocity: float | None,
        baro_altitude: float | None,
    ) -> None:
        if not isinstance(icao24, str) or not icao24.strip():
            raise ValueError("Aircraft ICAO24 code cannot be empty.")

        if callsign is not None and not isinstance(callsign, str):
            raise ValueError("Callsign must be a string or None.")

        if not isinstance(origin_country, str) or not origin_country.strip():
            raise ValueError("Origin country cannot be empty.")

        if velocity is not None:
            if (
                isinstance(velocity, bool)
                or not isinstance(velocity, (int, float))
                or velocity < 0
            ):
                raise ValueError("Velocity must be a non-negative number or None.")

        if baro_altitude is not None:
            if isinstance(baro_altitude, bool) or not isinstance(
                baro_altitude, (int, float)
            ):
                raise ValueError("Altitude must be a number or None.")

        self._icao24 = icao24
        self._callsign = callsign
        self._origin_country = origin_country
        self._velocity = velocity
        self._baro_altitude = baro_altitude

    @property
    def icao24(self) -> str:
        return self._icao24

    @property
    def callsign(self) -> str | None:
        return self._callsign

    @property
    def origin_country(self) -> str:
        return self._origin_country

    @property
    def velocity(self) -> float | None:
        return self._velocity

    @property
    def baro_altitude(self) -> float | None:
        return self._baro_altitude

    def compare_speed(self, other: "Aircraft") -> int:
        """Compare aircraft by speed."""
        if self.velocity is None or other.velocity is None:
            raise ValueError("Cannot compare aircraft with unknown speed.")

        if self.velocity > other.velocity:
            return 1
        if self.velocity < other.velocity:
            return -1
        return 0

    def compare_altitude(self, other: "Aircraft") -> int:
        """Compare aircraft by altitude."""
        if self.baro_altitude is None or other.baro_altitude is None:
            raise ValueError("Cannot compare aircraft with unknown altitude.")

        if self.baro_altitude > other.baro_altitude:
            return 1
        if self.baro_altitude < other.baro_altitude:
            return -1
        return 0
