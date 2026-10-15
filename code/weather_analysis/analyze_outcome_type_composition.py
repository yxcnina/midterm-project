
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "artifacts" / "weather_analysis"
TABLE_DIR = OUTPUT_DIR / "tables"
FIGURE_DIR = OUTPUT_DIR / "figures" / "07_outcome_type"

OUTCOME_TYPES = [
    "Adoption",
    "Transfer",
    "Return to Owner",
    "Euthanasia",
    "Died",
    "Rto-Adopt",
    "Disposal",
    "Missing",
    "Lost",
]

DISPLAY_TYPES = [
    "Adoption",
    "Transfer",
    "Return to Owner",
    "Euthanasia",
    "Died",
    "Other Outcomes",
]

OTHER_TYPES = [
    "Rto-Adopt",
    "Disposal",
    "Missing",
    "Lost",
]

COLORS = [
    "#547AA5",
    "#83B8A6",
    "#E4AB70",
    "#B789AB",
    "#96A369",
    "#999999",
]


def load_data():
    """Load outcome events and daily weather observations."""
    outcomes = pd.read_csv(
        DATA_DIR / "aac_outcomes_clean.csv",
        parse_dates=["Outcome Date"],
    )
    weather = pd.read_csv(
        DATA_DIR / "austin_weather_2024.csv",
        parse_dates=["date"],
    )

    return outcomes, weather


def prepare_data(outcomes, weather):
    """Match valid outcome events to daily weather data."""

    print("\n=== Q7 Data Validation ===")
    print("Original outcome events:", len(outcomes))

    assert len(outcomes) == 11822
    assert weather["date"].is_unique

    missing_count = outcomes["Outcome Type"].isna().sum()
    print("Missing outcome types:", missing_count)

    assert missing_count == 10

    valid = outcomes.dropna(
        subset=["Outcome Type"]
    ).copy()

    assert set(valid["Outcome Type"].unique()) == set(
        OUTCOME_TYPES
    )

    print("Valid outcome events:", len(valid))
    print(
        "Number of outcome categories:",
        valid["Outcome Type"].nunique(),
    )

    valid["outcome_date"] = valid[
        "Outcome Date"
    ].dt.normalize()

    weather_columns = [
        "date",
        "precipitation_mm",
        "temp_max_c",
        "temp_min_c",
    ]

    merged = valid.merge(
        weather[weather_columns],
        left_on="outcome_date",
        right_on="date",
        how="left",
        validate="many_to_one",
        indicator=True,
    )

    unmatched = (merged["_merge"] != "both").sum()

    print("Unmatched outcome events:", unmatched)

    assert unmatched == 0
    assert len(merged) == len(valid)
    assert merged[
        ["precipitation_mm", "temp_max_c", "temp_min_c"]
    ].notna().all().all()

    merged["wet_day"] = (
        merged["precipitation_mm"] > 0
    ).astype(int)

    merged["hot_day"] = (
        merged["temp_max_c"] >= 35
    ).astype(int)

    merged["cold_day"] = (
        merged["temp_min_c"] <= 5
    ).astype(int)

    merged["freezing_day"] = (
        merged["temp_min_c"] <= 0
    ).astype(int)

    merged["display_type"] = merged["Outcome Type"].where(
        ~merged["Outcome Type"].isin(OTHER_TYPES),
        "Other Outcomes",
    )

    print(
        "All valid outcome events successfully matched to weather."
    )

    return merged


def calculate_composition(df, column, labels):
    """Calculate all nine outcome type shares."""

    group_totals = df.groupby(column).size()

    assert set(group_totals.index) == {0, 1}

    counts = pd.crosstab(
        df[column],
        df["Outcome Type"],
    ).reindex(
        index=[0, 1],
        columns=OUTCOME_TYPES,
        fill_value=0,
    )

    assert counts.to_numpy().sum() == len(df)

    rows = []

    for group_value in [0, 1]:
        total = int(group_totals.loc[group_value])

        for outcome_type in OUTCOME_TYPES:
            count = int(
                counts.loc[group_value, outcome_type]
            )

            rows.append({
                "weather_group": labels[group_value],
                "outcome_type": outcome_type,
                "outcome_events": count,
                "total_group_events": total,
                "proportion_pct": count / total * 100,
            })

    composition = pd.DataFrame(rows)

    percentage_sums = composition.groupby(
        "weather_group"
    )["proportion_pct"].sum()

    assert np.allclose(
        percentage_sums.to_numpy(),
        100,
    )

    return composition, group_totals


def calculate_differences(composition, labels):
    """Calculate exposed minus reference percentage points."""

    pivot = composition.pivot(
        index="outcome_type",
        columns="weather_group",
        values="proportion_pct",
    ).reindex(OUTCOME_TYPES)

    differences = pd.DataFrame({
        "outcome_type": OUTCOME_TYPES,
        "reference_pct": pivot[
            labels[0]
        ].to_numpy(),
        "exposed_pct": pivot[
            labels[1]
        ].to_numpy(),
    })

    differences["difference_pp"] = (
        differences["exposed_pct"]
        - differences["reference_pct"]
    )

    assert abs(
        differences["difference_pp"].sum()
    ) < 1e-8

    return differences


def calculate_display_composition(df, column):
    """Combine rare outcome types for readable figures."""

    counts = pd.crosstab(
        df[column],
        df["display_type"],
    ).reindex(
        index=[0, 1],
        columns=DISPLAY_TYPES,
        fill_value=0,
    )

    shares = counts.div(
        counts.sum(axis=1),
        axis=0,
    ) * 100

    assert np.allclose(
        shares.sum(axis=1).to_numpy(),
        100,
    )

    return shares


def plot_composition(shares, labels, title, output_path):
    """Plot a 100% stacked bar chart."""

    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(2)
    bottom = np.zeros(2)

    for outcome_type, color in zip(
        DISPLAY_TYPES, COLORS
    ):
        values = shares[
            outcome_type
        ].to_numpy()

        bars = ax.bar(
            x,
            values,
            bottom=bottom,
            color=color,
            width=0.55,
            label=outcome_type,
        )

        for bar, value, base in zip(
            bars, values, bottom
        ):
            if value >= 4:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    base + value / 2,
                    f"{value:.1f}%",
                    ha="center",
                    va="center",
                    fontsize=10,
                )

        bottom += values

    ax.set_xticks(x, [
        labels[0],
        labels[1],
    ])
    ax.set_ylim(0, 100)
    ax.set_ylabel("Percentage of Outcome Events (%)")
    ax.set_title(title)
    ax.legend(
        title="Outcome Type",
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
    )

    fig.tight_layout()
    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)


def plot_differences(
    df, labels, title, output_path
):
    """Plot percentage-point changes for all nine types."""

    values = df["difference_pp"].to_numpy()
    names = df["outcome_type"].tolist()

    fig, ax = plt.subplots(figsize=(10, 6))

    y = np.arange(len(names))

    colors = [
        "#83B8A6" if value >= 0 else "#547AA5"
        for value in values
    ]

    ax.barh(
        y,
        values,
        color=colors,
        height=0.7,
    )

    ax.set_yticks(y, names)
    ax.invert_yaxis()
    ax.axvline(0, color="black", linewidth=1)

    ax.set_title(title)
    ax.set_xlabel(
        "Difference in Percentage Points "
        f"({labels[1]} - {labels[0]})"
    )

    max_abs = max(
        np.max(np.abs(values)),
        0.1,
    )
    padding = max_abs * 0.22

    ax.set_xlim(
        -max_abs - padding,
        max_abs + padding,
    )

    for i, value in enumerate(values):
        offset = max_abs * 0.03

        ax.text(
            value + (
                offset if value >= 0 else -offset
            ),
            i,
            f"{value:+.2f} pp",
            ha="left" if value >= 0 else "right",
            va="center",
            fontsize=9,
        )

    ax.grid(
        axis="x",
        linestyle="--",
        alpha=0.25,
    )
    ax.set_axisbelow(True)

    fig.tight_layout()
    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)


def analyze_group(
    df,
    column,
    labels,
    prefix,
    description,
):
    """Generate tables and figures for one weather comparison."""

    print(f"\n=== {description} ===")

    composition, totals = calculate_composition(
        df,
        column,
        labels,
    )

    differences = calculate_differences(
        composition,
        labels,
    )

    shares = calculate_display_composition(
        df,
        column,
    )

    print("\nGroup totals:")
    for value in [0, 1]:
        print(
            f"{labels[value]}: "
            f"{totals.loc[value]:,} events"
        )

    print("\nOutcome type proportions:")
    print(
        composition.to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}",
        )
    )

    print("\nPercentage-point differences:")
    print(
        differences.to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}",
        )
    )

    TABLE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    FIGURE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    composition_path = (
        TABLE_DIR / f"{prefix}_composition.csv"
    )
    differences_path = (
        TABLE_DIR / f"{prefix}_differences.csv"
    )

    composition.to_csv(
        composition_path,
        index=False,
    )

    differences.to_csv(
        differences_path,
        index=False,
    )

    composition_figure = (
        FIGURE_DIR / f"{prefix}_composition.png"
    )

    differences_figure = (
        FIGURE_DIR / f"{prefix}_differences.png"
    )

    plot_composition(
        shares,
        labels,
        f"{description}: Outcome Type Composition (2024)",
        composition_figure,
    )

    plot_differences(
        differences,
        labels,
        f"{description}: Outcome Share Differences (2024)",
        differences_figure,
    )

    print("\nSaved outputs:")
    print(composition_path)
    print(differences_path)
    print(composition_figure)
    print(differences_figure)


def main():
    outcomes, weather = load_data()
    df = prepare_data(outcomes, weather)

    analyses = [
        (
            "wet_day",
            ["Dry Days", "Wet Days"],
            "q7a_rainfall",
            "Q7a Rainfall",
        ),
        (
            "hot_day",
            ["Non-Hot Days", "Hot Days"],
            "q7b_heat",
            "Q7b Extreme Heat",
        ),
        (
            "cold_day",
            ["Non-Cold Days", "Cold Days"],
            "q7c_cold",
            "Q7c Cold Weather",
        ),
        (
            "freezing_day",
            ["Non-Freezing Days", "Freezing Days"],
            "q7c_freezing_sensitivity",
            "Q7c Freezing Sensitivity",
        ),
    ]

    for column, labels, prefix, description in analyses:
        analyze_group(
            df,
            column,
            labels,
            prefix,
            description,
        )

    print("\n=== Q7 Complete ===")
    print("Four weather comparisons completed.")
    print("Eight CSV tables and eight PNG figures generated.")


if __name__ == "__main__":
    main()
