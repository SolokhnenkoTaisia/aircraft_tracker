from pathlib import Path
from typing import Any

from aircraft_tracker.aircraft import Aircraft
from aircraft_tracker.api import AircraftAPI, APIError
from aircraft_tracker.storage import JSONSaver, StorageError


def convert_to_aircraft(
    states: list[list[Any]],
) -> list[Aircraft]:
    """Convert OpenSky state vectors into Aircraft objects."""
    aircraft_list = []

    for state in states:
        if len(state) < 10:
            continue

        icao24 = state[0]
        callsign = state[1]
        origin_country = state[2]
        velocity = state[9]
        baro_altitude = state[7]

        if not isinstance(icao24, str):
            continue

        if not isinstance(origin_country, str):
            continue

        if velocity is not None and not isinstance(velocity, (int, float)):
            continue

        if baro_altitude is not None and not isinstance(baro_altitude, (int, float)):
            continue

        try:
            aircraft = Aircraft(
                icao24=icao24,
                callsign=(
                    callsign.strip() or None if isinstance(callsign, str) else None
                ),
                origin_country=origin_country,
                velocity=velocity,
                baro_altitude=baro_altitude,
            )
        except ValueError:
            continue

        aircraft_list.append(aircraft)

    return aircraft_list


def get_top_aircraft(
    aircraft_list: list[Aircraft],
    count: int,
) -> list[Aircraft]:
    """Return top aircraft by altitude in descending order."""
    if count < 1:
        raise ValueError("Count must be a positive number.")

    aircraft_with_altitude = [
        aircraft for aircraft in aircraft_list if aircraft.baro_altitude is not None
    ]

    sorted_aircraft = sorted(
        aircraft_with_altitude,
        key=lambda aircraft: (
            aircraft.baro_altitude
            if aircraft.baro_altitude is not None
            else float("-inf")
        ),
        reverse=True,
    )

    return sorted_aircraft[:count]


def filter_by_country(
    aircraft_list: list[Aircraft],
    country: str,
) -> list[Aircraft]:
    """Filter aircraft by registration country."""
    if not country.strip():
        raise ValueError("Country cannot be empty.")

    return [
        aircraft
        for aircraft in aircraft_list
        if aircraft.origin_country.casefold() == country.casefold()
    ]


def print_aircraft(aircraft_list: list[Aircraft]) -> None:
    """Print aircraft information in a readable format."""
    if not aircraft_list:
        print("Самолёты не найдены.")
        return

    for aircraft in aircraft_list:
        callsign = aircraft.callsign or "Неизвестно"
        velocity = (
            f"{aircraft.velocity:.1f} м/с"
            if aircraft.velocity is not None
            else "Неизвестно"
        )
        altitude = (
            f"{aircraft.baro_altitude:.1f} м"
            if aircraft.baro_altitude is not None
            else "Неизвестно"
        )

        print(
            f"Позывной: {callsign}\n"
            f"ICAO24: {aircraft.icao24}\n"
            f"Страна: {aircraft.origin_country}\n"
            f"Скорость: {velocity}\n"
            f"Высота: {altitude}\n"
            f"{'-' * 30}"
        )


def run_console() -> None:
    """Run the aircraft tracking console application."""
    print("=== Aircraft Tracker ===")

    country = input("Введите страну для поиска самолётов: ").strip()

    if not country:
        print("Название страны не может быть пустым.")
        return

    try:
        api = AircraftAPI()

        print("Получаем границы страны...")
        bounds = api.get_country_bounds(country)

        print("Получаем данные о самолётах...")
        states = api.get_aircraft(bounds)

        aircraft_list = convert_to_aircraft(states)

        if not aircraft_list:
            print("Самолёты не найдены.")
            return

        storage_path = Path(__file__).resolve().parents[2] / "data" / "aircraft.json"
        storage = JSONSaver(storage_path)

        existing_aircraft = storage.get_aircraft()
        existing_ids = {aircraft.icao24 for aircraft in existing_aircraft}

        saved_count = 0

        for aircraft in aircraft_list:
            if aircraft.icao24 not in existing_ids:
                storage.add_aircraft(aircraft)
                existing_ids.add(aircraft.icao24)
                saved_count += 1

        print(f"Найдено самолётов: {len(aircraft_list)}")
        print(f"Новых самолётов сохранено: {saved_count}")

        count = int(input("Сколько самолётов показать (топ по высоте)? "))

        top_aircraft = get_top_aircraft(aircraft_list, count)

        print("\n=== Самолёты с наибольшей высотой ===")
        print_aircraft(top_aircraft)

        registration_country = input(
            "\nВведите страну регистрации для фильтрации: "
        ).strip()

        filtered_aircraft = filter_by_country(
            aircraft_list,
            registration_country,
        )

        print(f"\n=== Самолёты, зарегистрированные в " f"{registration_country} ===")
        print_aircraft(filtered_aircraft)

    except (APIError, StorageError, ValueError) as error:
        print(f"Ошибка: {error}")


if __name__ == "__main__":
    run_console()
