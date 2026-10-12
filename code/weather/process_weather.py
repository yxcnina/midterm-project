
import json
from pathlib import Path

import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def load_noaa_data():
    """Load and standardize NOAA daily weather data."""

    file_path = RAW_DATA_DIR / "noaa_austin_2024.json"

    with open(file_path, "r", encoding="utf-8") as file:
        raw_data = json.load(file)

    df = pd.DataFrame(raw_data)

    df = df[["DATE", "TMAX", "TMIN", "PRCP"]].copy()

    df = df.rename(columns={
        "DATE": "date",
        "TMAX": "temp_max_c",
        "TMIN": "temp_min_c",
        "PRCP": "precipitation_mm",
    })

    df["date"] = pd.to_datetime(df["date"])

    for column in [
        "temp_max_c",
        "temp_min_c",
        "precipitation_mm",
    ]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.sort_values("date").reset_index(drop=True)

    return df


def load_open_meteo_data():
    """Load and standardize Open-Meteo daily weather data."""

    file_path = RAW_DATA_DIR / "open_meteo_austin_2024.json"

    with open(file_path, "r", encoding="utf-8") as file:
        raw_data = json.load(file)

    daily = raw_data["daily"]

    df = pd.DataFrame({
        "date": daily["time"],
        "humidity_mean_pct": daily["relative_humidity_2m_mean"],
        "cloud_cover_mean_pct": daily["cloud_cover_mean"],
        "wind_speed_max_kmh": daily["wind_speed_10m_max"],
    })

    df["date"] = pd.to_datetime(df["date"])

    for column in [
        "humidity_mean_pct",
        "cloud_cover_mean_pct",
        "wind_speed_max_kmh",
    ]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.sort_values("date").reset_index(drop=True)

    return df


def merge_weather_data(noaa_df, open_meteo_df):
    """Merge NOAA and Open-Meteo data by date."""

    merged_df = pd.merge(
        noaa_df,
        open_meteo_df,
        on="date",
        how="inner",
        validate="one_to_one",
    )

    merged_df = merged_df.sort_values("date").reset_index(drop=True)

    return merged_df


def create_weather_indicators(df):
    """Create binary indicators for hot, freezing, and wet days."""

    df = df.copy()

    df["hot_day"] = (df["temp_max_c"] >= 35).astype(int)

    df["freezing_day"] = (df["temp_min_c"] <= 0).astype(int)

    df["wet_day"] = (df["precipitation_mm"] > 0).astype(int)

    return df


def validate_weather_data(df):
    """Validate dates, weather values, and binary indicators."""

    expected_dates = pd.date_range(
        start="2024-01-01",
        end="2024-12-31",
        freq="D",
    )

    actual_dates = pd.DatetimeIndex(df["date"])

    assert len(df) == 366, "Expected exactly 366 rows."
    assert df["date"].is_unique, "Duplicate dates detected."
    assert actual_dates.equals(expected_dates), "Dates do not match 2024 calendar."
    assert not df.isna().any().any(), "Missing values detected."

    assert (df["temp_max_c"] >= df["temp_min_c"]).all(), (
        "Maximum temperature is lower than minimum temperature."
    )

    assert (df["precipitation_mm"] >= 0).all(), (
        "Negative precipitation detected."
    )

    assert df["humidity_mean_pct"].between(0, 100).all(), (
        "Humidity outside 0-100% range."
    )

    assert df["cloud_cover_mean_pct"].between(0, 100).all(), (
        "Cloud cover outside 0-100% range."
    )

    assert (df["wind_speed_max_kmh"] >= 0).all(), (
        "Negative wind speed detected."
    )

    assert df["hot_day"].equals(
        (df["temp_max_c"] >= 35).astype(int)
    ), "Hot day indicator is inconsistent."

    assert df["freezing_day"].equals(
        (df["temp_min_c"] <= 0).astype(int)
    ), "Freezing day indicator is inconsistent."

    assert df["wet_day"].equals(
        (df["precipitation_mm"] > 0).astype(int)
    ), "Wet day indicator is inconsistent."

    print("\n--- Comprehensive Validation ---")
    print("2024 date coverage: PASS")
    print("Duplicate dates: PASS")
    print("Missing values: PASS")
    print("Temperature consistency: PASS")
    print("Precipitation values: PASS")
    print("Humidity range: PASS")
    print("Cloud cover range: PASS")
    print("Wind speed values: PASS")
    print("Binary weather indicators: PASS")
    print("All comprehensive validation checks passed.")


def save_weather_data(df):
    """Save the validated daily weather dataset as a CSV file."""

    output_dir = PROJECT_ROOT / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "austin_weather_2024.csv"

    df.to_csv(
        output_path,
        index=False,
        date_format="%Y-%m-%d",
    )

    print("\n--- Weather Data Export ---")
    print(f"Saved to: {output_path}")

    return output_path 


def main():
    noaa_df = load_noaa_data()
    open_meteo_df = load_open_meteo_data()

    merged_df = merge_weather_data(noaa_df, open_meteo_df)

    weather_df = create_weather_indicators(merged_df)

    validate_weather_data(weather_df) 

    save_weather_data(weather_df) 

    print("--- Weather Data with Indicators ---")
    print(weather_df.head().to_string(index=False))

    print("\n--- Data Validation ---")
    print(f"Total rows: {len(weather_df)}")
    print(f"Total columns: {len(weather_df.columns)}")
    print(f"Duplicate dates: {weather_df['date'].duplicated().sum()}")

    print("\nMissing values by column:")
    print(weather_df.isna().sum())

    print("\n--- Weather Indicator Frequencies ---")
    print(f"Hot days (TMAX >= 35 C): {weather_df['hot_day'].sum()}")
    print(f"Freezing days (TMIN <= 0 C): {weather_df['freezing_day'].sum()}")
    print(f"Wet days (PRCP > 0 mm): {weather_df['wet_day'].sum()}")


if __name__ == "__main__":
    main()
