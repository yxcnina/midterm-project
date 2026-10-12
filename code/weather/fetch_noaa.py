import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen


# NOAA API configuration
BASE_URL = "https://www.ncei.noaa.gov/access/services/data/v1"

PARAMS = {
    "dataset": "daily-summaries",
    "stations": "USW00013958",
    "startDate": "2024-01-01",
    "endDate": "2024-12-31",
    "dataTypes": "TMAX,TMIN,PRCP",
    "units": "metric",
    "format": "json",
}


def fetch_noaa_data():
    """Retrieve daily weather observations from NOAA."""

    url = BASE_URL + "?" + urlencode(PARAMS)

    print("Requesting NOAA weather data...")

    with urlopen(url, timeout=60) as response:
        data = json.load(response)

    if not isinstance(data, list) or not data:
        raise ValueError("NOAA returned no usable daily records.")

    return data


def save_noaa_data(data):
    """Save the downloaded observations as a JSON file."""

    project_root = Path(__file__).resolve().parents[2]
    output_path = project_root / "data" / "raw" / "noaa_austin_2024.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    print(f"Saved {len(data)} NOAA records.")
    print(f"File location: {output_path}")


def validate_noaa_data(data):
    """Check NOAA dates, completeness, and weather variables."""

    from datetime import date, timedelta

    dates = [record.get("DATE") for record in data]

    start = date(2024, 1, 1)
    end = date(2024, 12, 31)

    expected_dates = set()
    current = start

    while current <= end:
        expected_dates.add(current.isoformat())
        current += timedelta(days=1)

    actual_dates = set(dates)

    missing_dates = sorted(expected_dates - actual_dates)
    extra_dates = sorted(actual_dates - expected_dates)
    duplicate_count = len(dates) - len(actual_dates)

    print("\n--- NOAA Data Validation ---")
    print(f"Total records: {len(data)}")
    print(f"Unique dates: {len(actual_dates)}")
    print(f"Missing dates: {missing_dates}")
    print(f"Extra dates: {extra_dates}")
    print(f"Duplicate dates: {duplicate_count}")

    for variable in ["TMAX", "TMIN", "PRCP"]:
        missing = sum(
            1 for record in data
            if record.get(variable) in (None, "")
        )
        print(f"Missing {variable}: {missing}")


def main():
    data = fetch_noaa_data()
    validate_noaa_data(data)
    save_noaa_data(data) 


if __name__ == "__main__":
    main()



