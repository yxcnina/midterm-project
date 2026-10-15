

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "processed"
TABLE_DIR = PROJECT_ROOT / "artifacts" / "weather_analysis" / "tables"
FIGURE_DIR = (
    PROJECT_ROOT / "artifacts" / "weather_analysis"
    / "figures" / "06_intake_condition"
)

MAIN_CONDITIONS = [
    "Normal",
    "Injured",
    "Sick",
    "Neonatal",
    "Medical",
]

PLOT_CONDITIONS = MAIN_CONDITIONS + ["Other Conditions"]

COLORS = [
    "#547AA5",
    "#D98970",
    "#C5A05A",
    "#83B8A6",
    "#A58AB5",
    "#999999",
]


def load_and_prepare_data():
    """Read intake events and match each event to daily weather."""

    intakes = pd.read_csv(
        DATA_DIR / "aac_intakes_clean.csv",
        parse_dates=["Intake Date"],
    )

    weather = pd.read_csv(
        DATA_DIR / "austin_weather_2024.csv",
        parse_dates=["date"],
    )

    assert len(intakes) == 11815
    assert len(weather) == 366
    assert weather["date"].is_unique
    assert intakes["Intake Date"].notna().all()
    assert intakes["Intake Condition"].notna().all()
    assert intakes["Intake Condition"].nunique() == 16

    assert weather[
        ["wet_day", "hot_day", "freezing_day", "temp_min_c"]
    ].notna().all().all()

    merged = intakes.merge(
        weather[
            ["date", "wet_day", "hot_day",
             "freezing_day", "temp_min_c"]
        ],
        left_on="Intake Date",
        right_on="date",
        how="left",
        validate="many_to_one",
        indicator=True,
    )

    assert len(merged) == 11815
    assert (merged["_merge"] == "both").all()

    
    merged["cold_day"] = (
        merged["temp_min_c"] <= 5
    ).astype(int)

    
    merged["condition_plot_group"] = (
        merged["Intake Condition"].where(
            merged["Intake Condition"].isin(MAIN_CONDITIONS),
            "Other Conditions",
        )
    )

    print("\n=== Q6 Data Validation ===")
    print("Total intake events:", len(merged))
    print("Original condition categories:",
          merged["Intake Condition"].nunique())
    print("Missing conditions:",
          merged["Intake Condition"].isna().sum())
    print("All intake events matched to weather.")

    return merged


def calculate_composition(data, indicator, group_labels):
    """Calculate all 16 original condition shares and differences."""

    conditions = sorted(data["Intake Condition"].unique())

    counts = (
        data.groupby([indicator, "Intake Condition"])
        .size()
        .unstack(fill_value=0)
        .reindex(index=[0, 1], columns=conditions, fill_value=0)
    )

    totals = counts.sum(axis=1)
    percentages = counts.div(totals, axis=0) * 100

    summary_rows = []

    for group in [0, 1]:
        for condition in conditions:
            summary_rows.append({
                "weather_group": group_labels[group],
                "intake_condition": condition,
                "events": int(counts.loc[group, condition]),
                "total_group_events": int(totals.loc[group]),
                "proportion_pct": round(
                    percentages.loc[group, condition], 4
                ),
            })

    summary = pd.DataFrame(summary_rows)

    difference_rows = []

    for condition in conditions:
        difference_rows.append({
            "intake_condition": condition,
            "reference_events": int(counts.loc[0, condition]),
            "exposed_events": int(counts.loc[1, condition]),
            "reference_pct": round(
                percentages.loc[0, condition], 4
            ),
            "exposed_pct": round(
                percentages.loc[1, condition], 4
            ),
            "difference_pp": round(
                percentages.loc[1, condition]
                - percentages.loc[0, condition], 4
            ),
        })

    differences = pd.DataFrame(difference_rows)

    assert int(totals.sum()) == 11815
    assert (totals > 0).all()

    for group in [0, 1]:
        assert abs(percentages.loc[group].sum() - 100) < 1e-9

    print("\nGroup totals:")
    print(totals.to_string())

    print("\nCondition proportions:")
    print(summary.to_string(index=False))

    print("\nPercentage-point differences:")
    print(differences.to_string(index=False))

    return summary, differences


def plot_composition(data, indicator, labels, title, prefix):
    """Plot the six display groups in a 100% stacked bar chart."""

    counts = (
        data.groupby([indicator, "condition_plot_group"])
        .size()
        .unstack(fill_value=0)
        .reindex(
            index=[0, 1],
            columns=PLOT_CONDITIONS,
            fill_value=0,
        )
    )

    percentages = counts.div(counts.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(9, 6))
    bottom = [0.0, 0.0]

    for condition, color in zip(PLOT_CONDITIONS, COLORS):
        values = percentages[condition].to_numpy()

        bars = ax.bar(
            labels,
            values,
            bottom=bottom,
            color=color,
            label=condition,
            width=0.55,
        )

        for bar, value, base in zip(bars, values, bottom):
            if value >= 5:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    base + value / 2,
                    f"{value:.1f}%",
                    ha="center",
                    va="center",
                    fontsize=10,
                )

        bottom = [base + value
                  for base, value in zip(bottom, values)]

    ax.set_title(f"{title}: Intake Condition Composition (2024)")
    ax.set_ylabel("Percentage of Intake Events (%)")
    ax.set_ylim(0, 100)
    ax.legend(
        title="Intake Condition",
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
    )

    fig.tight_layout()

    output_path = FIGURE_DIR / f"{prefix}_composition.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"Composition figure saved: {output_path}")


def plot_differences(data, indicator, labels, title, prefix):
    """Plot percentage-point differences for the six display groups."""

    counts = (
        data.groupby([indicator, "condition_plot_group"])
        .size()
        .unstack(fill_value=0)
        .reindex(
            index=[0, 1],
            columns=PLOT_CONDITIONS,
            fill_value=0,
        )
    )

    percentages = counts.div(counts.sum(axis=1), axis=0) * 100

    changes = (
        percentages.loc[1] - percentages.loc[0]
    ).sort_values()

    fig, ax = plt.subplots(figsize=(9, 5))

    bar_colors = [
        "#83B8A6" if value >= 0 else "#547AA5"
        for value in changes
    ]

    bars = ax.barh(
        changes.index,
        changes.values,
        color=bar_colors,
    )

    ax.axvline(0, color="black", linewidth=1)
    ax.set_title(f"{title}: Intake Condition Share Differences (2024)")
    ax.set_xlabel(
        f"Difference in Percentage Points "
        f"({labels[1]} - {labels[0]})"
    )

    for bar, value in zip(bars, changes.values):
        ax.annotate(
            f"{value:+.2f} pp",
            xy=(value, bar.get_y() + bar.get_height() / 2),
            xytext=(5 if value >= 0 else -5, 0),
            textcoords="offset points",
            ha="left" if value >= 0 else "right",
            va="center",
            fontsize=10,
        )

    margin = max(0.5, changes.abs().max() * 0.25)
    ax.set_xlim(changes.min() - margin, changes.max() + margin)
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)

    fig.tight_layout()

    output_path = FIGURE_DIR / f"{prefix}_differences.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"Difference figure saved: {output_path}")


def run_analysis(data, indicator, labels, title, prefix):
    """Run one weather comparison and save all outputs."""

    print(f"\n=== {title} ===")

    summary, differences = calculate_composition(
        data,
        indicator,
        labels,
    )

    summary_path = TABLE_DIR / f"{prefix}_composition.csv"
    differences_path = TABLE_DIR / f"{prefix}_differences.csv"

    summary.to_csv(summary_path, index=False)
    differences.to_csv(differences_path, index=False)

    print(f"Summary saved: {summary_path}")
    print(f"Differences saved: {differences_path}")

    plot_composition(data, indicator, labels, title, prefix)
    plot_differences(data, indicator, labels, title, prefix)


def main():
    """Run rainfall, heat, cold, and freezing comparisons."""

    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    data = load_and_prepare_data()

    analyses = [
        (
            "wet_day",
            ["Dry Days", "Wet Days"],
            "Q6a Rainfall",
            "q6a_rainfall",
        ),
        (
            "hot_day",
            ["Non-Hot Days", "Hot Days"],
            "Q6b Extreme Heat",
            "q6b_heat",
        ),
        (
            "cold_day",
            ["Non-Cold Days", "Cold Days"],
            "Q6c Cold Weather",
            "q6c_cold",
        ),
        (
            "freezing_day",
            ["Non-Freezing Days", "Freezing Days"],
            "Q6c Freezing Sensitivity",
            "q6c_freezing_sensitivity",
        ),
    ]

    for indicator, labels, title, prefix in analyses:
        run_analysis(data, indicator, labels, title, prefix)


if __name__ == "__main__":
    main()
 