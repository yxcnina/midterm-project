
from pathlib import Path

import pandas as pd

import matplotlib.pyplot as plt 


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


def inspect_data(intake_df, weather_df):
    """Check intake categories and weather date matching."""

    print("--- Q2: Intake Type Distribution ---")
    print(intake_df["Intake Type"].value_counts(dropna=False))

    print("\n--- Dataset Sizes ---")
    print(f"Intake events: {len(intake_df)}")
    print(f"Weather dates: {len(weather_df)}")

    print("\n--- Date Matching ---")

    intake_dates = intake_df["Intake Date"].dt.normalize()

    unmatched = ~intake_dates.isin(weather_df["date"])

    print(f"Unmatched intake events: {unmatched.sum()}")
    print(f"Missing intake dates: {intake_dates.isna().sum()}")
    print(f"Duplicate weather dates: {weather_df['date'].duplicated().sum()}")

    assert not unmatched.any(), "Some intake events have no matching weather date."
    assert weather_df["date"].is_unique, "Duplicate weather dates detected."

    print("Date matching validation: PASS")


def analyze_stray_proportions(intake_df, weather_df):
    """Compare stray intake proportions between wet and dry days."""

    daily_weather = weather_df[["date", "wet_day"]].copy()

    
    events = intake_df.copy()
    events["date"] = events["Intake Date"].dt.normalize()

    merged_df = events.merge(
        daily_weather,
        on="date",
        how="left",
        validate="many_to_one",
    )

    
    assert len(merged_df) == len(intake_df), (
        "The number of intake events changed after merging."
    )

    assert merged_df["wet_day"].notna().all(), (
        "Some intake events have missing weather information."
    )


    merged_df["is_stray"] = (
        merged_df["Intake Type"] == "Stray"
    ).astype(int)

    
    summary = merged_df.groupby("wet_day")["is_stray"].agg(
        total_intakes="count",
        stray_intakes="sum",
        stray_proportion="mean",
    )

    summary["stray_percentage"] = (
        summary["stray_proportion"] * 100
    )

    print("\n--- Q2: Stray Intake Proportions ---")
    print(summary.round(4).to_string())

    wet_pct = summary.loc[1, "stray_percentage"]
    dry_pct = summary.loc[0, "stray_percentage"]

    print(
        f"\nWet minus Dry difference: "
        f"{wet_pct - dry_pct:.2f} percentage points"
    )

    print(f"Total matched intake events: {len(merged_df)}")
    print(f"Total stray intake events: {merged_df['is_stray'].sum()}")

    return summary


def save_q2_summary(summary):
    """Save Q2 stray intake descriptive statistics to CSV."""

    output_dir = (
        PROJECT_ROOT
        / "artifacts"
        / "weather_analysis"
        / "tables"
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "q2_stray_intakes_summary.csv"

    output_df = summary.reset_index().copy()

    output_df["weather_condition"] = output_df["wet_day"].map(
        {0: "Dry", 1: "Wet"}
    )

    output_df = output_df[
        [
            "weather_condition",
            "wet_day",
            "total_intakes",
            "stray_intakes",
            "stray_proportion",
            "stray_percentage",
        ]
    ]

    output_df.to_csv(output_path, index=False)

    print(f"\nQ2 summary table saved to: {output_path}")

    return output_path


def plot_stray_proportions(summary):
    """Create and save a bar chart of stray intake percentages."""

    labels = ["Dry Days", "Wet Days"]

    percentages = [
        summary.loc[0, "stray_percentage"],
        summary.loc[1, "stray_percentage"],
    ]

    fig, ax = plt.subplots(figsize=(7, 5))

    bars = ax.bar(
        labels,
        percentages,
        color=["#547AA5", "#83B8A6"],
        width=0.55,
    )

    ax.set_title(
        "Stray Intake Proportions: Dry vs. Wet Days (2024)"
    )

    ax.set_ylabel("Stray Intakes (% of All Intakes)")

    ax.set_ylim(0, 100)

    for bar, percentage in zip(bars, percentages):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            f"{percentage:.2f}%",
            ha="center",
            va="bottom",
        )

    ax.text(
        0.5,
        -0.15,
        "Event-level analysis: 11,815 intake events in 2024.",
        ha="center",
        transform=ax.transAxes,
        fontsize=9,
    )

    fig.tight_layout()

    output_dir = (
        PROJECT_ROOT
        / "artifacts"
        / "weather_analysis"
        / "figures"
        / "02_stray_intakes"
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "stray_proportion_wet_vs_dry.png"

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(f"\nQ2 figure saved to: {output_path}")

    return output_path


def main():
    intake_df, weather_df = load_data()
    inspect_data(intake_df, weather_df)

    summary = analyze_stray_proportions(intake_df, weather_df)

    save_q2_summary(summary) 

    plot_stray_proportions(summary) 


if __name__ == "__main__":
    main()
