
from pathlib import Path

import pandas as pd

import matplotlib.pyplot as plt 



PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


def load_data():
    """Load cleaned outcome events and daily weather data."""

    outcome_path = PROCESSED_DATA_DIR / "aac_outcomes_clean.csv"
    weather_path = PROCESSED_DATA_DIR / "austin_weather_2024.csv"

    outcome_df = pd.read_csv(outcome_path)
    weather_df = pd.read_csv(
        weather_path,
        parse_dates=["date"],
    )

    return outcome_df, weather_df


def inspect_data(outcome_df, weather_df):
    """Inspect outcome categories, date columns, and weather coverage."""

    print("--- Q3: Outcome Dataset ---")
    print(f"Outcome events: {len(outcome_df)}")
    print(f"Weather dates: {len(weather_df)}")

    print("\n--- Outcome Column Names ---")
    print(outcome_df.columns.tolist())

    print("\n--- First 3 Outcome Records ---")
    print(outcome_df.head(3).to_string(index=False))

    print("\n--- Possible Date Columns ---")
    date_columns = [
        column
        for column in outcome_df.columns
        if "date" in column.lower()
    ]
    print(date_columns)

    print("\n--- Possible Outcome Type Columns ---")
    type_columns = [
        column
        for column in outcome_df.columns
        if "outcome" in column.lower()
        and "type" in column.lower()
    ]

    for column in type_columns:
        print(f"\nColumn: {column}")
        print(outcome_df[column].value_counts(dropna=False))

    print("\n--- Hot Day Distribution ---")
    print(weather_df["hot_day"].value_counts(dropna=False))

    print("\n--- Weather Date Checks ---")
    print(f"Duplicate dates: {weather_df['date'].duplicated().sum()}")
    print(f"Missing dates: {weather_df['date'].isna().sum()}")


def prepare_outcome_weather_data(outcome_df, weather_df):
    """Match outcome events to daily weather and validate the records."""

    outcomes = outcome_df.copy()

    outcomes["date"] = pd.to_datetime(
        outcomes["Outcome Date"],
        errors="coerce",
    ).dt.normalize()

    print("\n--- Outcome Date Checks ---")
    print(f"Missing or invalid outcome dates: {outcomes['date'].isna().sum()}")
    print(f"First outcome date: {outcomes['date'].min()}")
    print(f"Last outcome date: {outcomes['date'].max()}")

    
    merged_df = outcomes.merge(
        weather_df[["date", "temp_max_c", "hot_day"]],
        on="date",
        how="left",
        validate="many_to_one",
        indicator=True,
    )

    print("\n--- Weather Matching Checks ---")
    print(merged_df["_merge"].value_counts())

    unmatched = (merged_df["_merge"] != "both").sum()

    print(f"Unmatched outcome events: {unmatched}")
    print(f"Original outcome events: {len(outcome_df)}")
    print(f"Merged outcome events: {len(merged_df)}")

    if unmatched > 0:
        raise ValueError("Some outcome events could not be matched to weather data.")

    if len(merged_df) != len(outcome_df):
        raise ValueError("The merge changed the number of outcome records.")

    
    analysis_df = merged_df.dropna(
        subset=["Outcome Type"]
    ).copy()

    
    analysis_df["is_adoption"] = (
        analysis_df["Outcome Type"] == "Adoption"
    ).astype(int)

    print("\n--- Q3 Analysis Sample ---")
    print(f"Records with missing Outcome Type: {len(merged_df) - len(analysis_df)}")
    print(f"Valid outcome records: {len(analysis_df)}")
    print(f"Adoption events: {analysis_df['is_adoption'].sum()}")
    print(f"Non-adoption events: {(analysis_df['is_adoption'] == 0).sum()}")

    print("\n--- Outcome Events by Weather Category ---")
    print(analysis_df["hot_day"].value_counts().sort_index())

    return analysis_df


def analyze_adoption_proportions(analysis_df):
    """Compare adoption outcome proportions on hot and non-hot days."""

    summary = analysis_df.groupby("hot_day").agg(
        total_outcomes=("is_adoption", "count"),
        adoption_outcomes=("is_adoption", "sum"),
    )

    summary["non_adoption_outcomes"] = (
        summary["total_outcomes"] - summary["adoption_outcomes"]
    )

    summary["adoption_proportion"] = (
        summary["adoption_outcomes"] / summary["total_outcomes"]
    )

    summary["adoption_percentage"] = (
        summary["adoption_proportion"] * 100
    )

    print("\n--- Q3: Adoption Outcome Proportions ---")
    print(summary.round(4).to_string())

    hot_pct = summary.loc[1, "adoption_percentage"]
    nonhot_pct = summary.loc[0, "adoption_percentage"]

    print(
        f"\nHot minus Non-Hot difference: "
        f"{hot_pct - nonhot_pct:.2f} percentage points"
    )

    print(f"Total matched outcome events: {summary['total_outcomes'].sum()}")
    print(f"Total adoption events: {summary['adoption_outcomes'].sum()}")

    return summary


def save_q3_summary(summary):
    """Save Q3 adoption statistics to a CSV file."""

    output_dir = (
        PROJECT_ROOT
        / "artifacts"
        / "weather_analysis"
        / "tables"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "q3_adoption_outcomes_summary.csv"

    output_df = summary.reset_index().copy()

    output_df["weather_condition"] = output_df["hot_day"].map(
        {0: "Non-Hot", 1: "Hot"}
    )

    output_df = output_df[
        [
            "weather_condition",
            "hot_day",
            "total_outcomes",
            "adoption_outcomes",
            "non_adoption_outcomes",
            "adoption_proportion",
            "adoption_percentage",
        ]
    ]

    output_df.to_csv(output_path, index=False)

    print(f"\nQ3 summary table saved to: {output_path}")

    return output_path


def plot_adoption_proportions(summary):
    """Create a bar chart of adoption percentages by weather condition."""

    labels = ["Non-Hot Days", "Hot Days"]

    percentages = [
        summary.loc[0, "adoption_percentage"],
        summary.loc[1, "adoption_percentage"],
    ]

    fig, ax = plt.subplots(figsize=(7, 5))

    bars = ax.bar(
        labels,
        percentages,
        color=["#547AA5", "#83B8A6"],
        width=0.55,
    )

    ax.set_title(
        "Adoption Outcome Proportions: Non-Hot vs. Hot Days (2024)"
    )
    ax.set_ylabel("Adoption Outcomes (% of Valid Outcomes)")
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
        "Event-level analysis: 11,812 outcomes with known Outcome Type.",
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
        / "03_adoption_outcomes"
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "adoption_proportion_hot_vs_nonhot.png"

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(f"\nQ3 figure saved to: {output_path}")

    return output_path


def main():
    outcome_df, weather_df = load_data()

    inspect_data(outcome_df, weather_df)

    analysis_df = prepare_outcome_weather_data(
        outcome_df,
        weather_df,
    )

    summary = analyze_adoption_proportions(analysis_df)

    save_q3_summary(summary)
    plot_adoption_proportions(summary)


if __name__ == "__main__":
    main() 

