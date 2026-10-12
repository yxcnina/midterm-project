import json
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen


# Open-Meteo Historical Weather API configuration
BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

PARAMS = {
    "latitude": 30.3208,
    "longitude": -97.7603,
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "daily": (
        "relative_humidity_2m_mean,"
        "cloud_cover_mean,"
        "wind_speed_10m_max"
    ),
    "wind_speed_unit": "kmh",
    "timezone": "America/Chicago",
}


def fetch_open_meteo_data():
    """Retrieve daily historical weather data from Open-Meteo."""

    url = BASE_URL + "?" + urlencode(PARAMS)

    print("Requesting Open-Meteo weather data...")

    with urlopen(url, timeout=60) as response:
        data = json.load(response)

    if "daily" not in data:
        raise ValueError("Open-Meteo returned no daily data.")

    return data


def validate_open_meteo_data(data):
    """Check dates and daily weather variables."""

    daily = data["daily"]

    dates = daily.get("time", [])

    start = date(2024, 1, 1)
    end = date(2024, 12, 31)

    expected_dates = set()
    current = start

    while current <= end:
        expected_dates.add(current.isoformat())
        current += timedelta(days=1)

    actual_dates = set(dates)

    print("\n--- Open-Meteo Data Validation ---")
    print(f"Total records: {len(dates)}")
    print(f"Unique dates: {len(actual_dates)}")
    print(f"Missing dates: {sorted(expected_dates - actual_dates)}")
    print(f"Extra dates: {sorted(actual_dates - expected_dates)}")
    print(f"Duplicate dates: {len(dates) - len(actual_dates)}")

    variables = [
        "relative_humidity_2m_mean",
        "cloud_cover_mean",
        "wind_speed_10m_max",
    ]

    for variable in variables:
        values = daily.get(variable, [])

        missing = sum(value is None for value in values)

        print(f"{variable}:")
        print(f"  Total values: {len(values)}")
        print(f"  Missing values: {missing}")


def save_open_meteo_data(data):
    """Save the downloaded data as JSON."""

    project_root = Path(__file__).resolve().parents[2]

    output_path = (
        project_root / "data" / "raw" / "open_meteo_austin_2024.json"
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    print(f"\nFile saved to: {output_path}")


def main():
    data = fetch_open_meteo_data()
    validate_open_meteo_data(data)
    save_open_meteo_data(data)


if __name__ == "__main__":
    main() 
