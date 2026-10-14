
from pathlib import Path

import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


def load_data():
    """Load cleaned intake events and daily weather data."""

    intake_path = PROCESSED_DATA_DIR / "aac_intakes_clean.csv"
    weather_path = PROCESSED_DATA_DIR / "austin_weather_2024.csv"

    intake_df = pd.read_csv(
        intake_path,
        parse_dates=["Intake Date"],
    )

    weather_df = pd.read_csv(
        weather_path,
        parse_dates=["date"],
    )

    return intake_df, weather_df


def prepare_daily_intake_data(intake_df, weather_df):
    """Aggregate intake events by date and merge with weather."""

    daily_counts = (
        intake_df.groupby("Intake Date")
        .size()
        .reset_index(name="intake_count")
        .rename(columns={"Intake Date": "date"})
    )

    daily_df = weather_df[
        ["date", "precipitation_mm", "wet_day"]
    ].merge(
        daily_counts,
        on="date",
        how="left",
        validate="one_to_one",
    )

    return daily_df


def main():
    intake_df, weather_df = load_data()

    daily_df = prepare_daily_intake_data(intake_df, weather_df)

    print("--- Daily Intake Data ---")
    print(daily_df.head(10).to_string(index=False))

    print("\n--- Data Checks ---")
    print(f"Original intake events: {len(intake_df)}")
    print(f"Total calendar days: {len(daily_df)}")
    print(f"Days with intake records: {daily_df['intake_count'].notna().sum()}")
    print(f"Total counted intake events: {daily_df['intake_count'].sum():.0f}")

    print("\n--- Dates Without Intake Records ---")
    print(
        daily_df.loc[
            daily_df["intake_count"].isna(),
            ["date", "precipitation_mm", "wet_day"],
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
