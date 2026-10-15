

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "processed"
TABLE_DIR = PROJECT_ROOT / "artifacts" / "weather_analysis" / "tables"
FIGURE_DIR = (
    PROJECT_ROOT
    / "artifacts"
    / "weather_analysis"
    / "figures"
    / "05_intake_type"
)

INTAKE_TYPES = [
    "Stray",
    "Owner Surrender",
    "Public Assist",
    "Abandoned",
    "Wildlife",
    "Euthanasia Request",
]


def load_data():
    """Load 2024 cleaned intake events and processed daily weather."""

    intake_df = pd.read_csv(
        DATA_DIR / "aac_intakes_clean.csv",
        parse_dates=["Intake Date"],
    )

    weather_df = pd.read_csv(
        DATA_DIR / "austin_weather_2024.csv",
        parse_dates=["date"],
    )

    return intake_df, weather_df


def prepare_data(intake_df, weather_df):
    """Match intake events to daily precipitation classifications."""

    assert len(intake_df) == 11815
    assert intake_df["Intake Date"].notna().all()
    assert intake_df["Intake Type"].notna().all()
    assert set(intake_df["Intake Type"]) == set(INTAKE_TYPES)

    assert len(weather_df) == 366
    assert weather_df["date"].is_unique
    assert weather_df["wet_day"].notna().all()
    assert set(weather_df["wet_day"].unique()) == {0, 1}

    merged_df = intake_df.merge(
        weather_df[
            ["date", "wet_day", "hot_day", "freezing_day", "temp_min_c"]
], 
        left_on="Intake Date",
        right_on="date",
        how="left",
        validate="many_to_one",
        indicator=True,
    )

    assert len(merged_df) == 11815
    assert (merged_df["_merge"] == "both").all()
    assert merged_df["wet_day"].notna().all()

    dry_events = (merged_df["wet_day"] == 0).sum()
    wet_events = (merged_df["wet_day"] == 1).sum()

    assert dry_events == 9543
    assert wet_events == 2272

    print("\n=== Q5 Data Validation ===")
    print(f"Total intake events: {len(merged_df)}")
    print(f"Dry-day intake events: {dry_events}")
    print(f"Wet-day intake events: {wet_events}")
    print(f"Intake types: {merged_df['Intake Type'].nunique()}")
    print("All events successfully matched to weather.")

    return merged_df


def analyze_composition(merged_df):
    """Calculate intake type counts and shares by rainfall category."""

    counts = (
        merged_df
        .groupby(["wet_day", "Intake Type"])
        .size()
        .unstack(fill_value=0)
        .reindex(index=[0, 1], columns=INTAKE_TYPES, fill_value=0)
    )

    totals = counts.sum(axis=1)

    percentages = counts.div(totals, axis=0) * 100

    rows = []

    for wet_day in [0, 1]:
        for intake_type in INTAKE_TYPES:
            rows.append({
                "weather": "Dry" if wet_day == 0 else "Wet",
                "wet_day": wet_day,
                "intake_type": intake_type,
                "intake_events": int(counts.loc[wet_day, intake_type]),
                "total_group_events": int(totals.loc[wet_day]),
                "proportion_pct": round(
                    percentages.loc[wet_day, intake_type], 4
                ),
            })

    summary = pd.DataFrame(rows)

    differences = pd.DataFrame({
        "intake_type": INTAKE_TYPES,
        "dry_events": [int(counts.loc[0, t]) for t in INTAKE_TYPES],
        "wet_events": [int(counts.loc[1, t]) for t in INTAKE_TYPES],
        "dry_proportion_pct": [
            round(percentages.loc[0, t], 4) for t in INTAKE_TYPES
        ],
        "wet_proportion_pct": [
            round(percentages.loc[1, t], 4) for t in INTAKE_TYPES
        ],
        "wet_minus_dry_pp": [
            round(
                percentages.loc[1, t] - percentages.loc[0, t],
                4,
            )
            for t in INTAKE_TYPES
        ],
    })

    
    assert int(counts.to_numpy().sum()) == 11815
    assert int(counts.loc[0].sum()) == 9543
    assert int(counts.loc[1].sum()) == 2272

    
    assert counts.loc[0, "Stray"] == 6575
    assert counts.loc[1, "Stray"] == 1636

    assert abs(percentages.loc[0].sum() - 100) < 1e-9
    assert abs(percentages.loc[1].sum() - 100) < 1e-9

    return summary, differences, percentages


def save_tables(summary, differences):
    """Save complete summary and percentage-point differences."""

    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    summary_path = TABLE_DIR / "q5_intake_type_composition.csv"
    difference_path = TABLE_DIR / "q5_intake_type_differences.csv"

    summary.to_csv(summary_path, index=False)
    differences.to_csv(difference_path, index=False)

    print(f"\nQ5 summary saved to: {summary_path}")
    print(f"Q5 differences saved to: {difference_path}")


def plot_composition(percentages):
    """Create a 100% stacked bar chart of intake type composition."""

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    colors = [
        "#547AA5",
        "#83B8A6",
        "#E2AD72",
        "#B681A8",
        "#8E9C65",
        "#A0A0A0",
    ]

    fig, ax = plt.subplots(figsize=(9, 6))

    bottom = [0.0, 0.0]

    for intake_type, color in zip(INTAKE_TYPES, colors):
        values = percentages[intake_type].to_numpy()

        bars = ax.bar(
            ["Dry Days", "Wet Days"],
            values,
            bottom=bottom,
            label=intake_type,
            color=color,
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

        bottom = [b + v for b, v in zip(bottom, values)]

    ax.set_title(
        "Animal Intake Type Composition: Dry vs. Wet Days (2024)"
    )
    ax.set_ylabel("Percentage of Intake Events (%)")
    ax.set_ylim(0, 100)

    ax.legend(
        title="Intake Type",
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
    )

    fig.tight_layout()

    output_path = FIGURE_DIR / "q5_intake_type_composition.png"

    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"Q5 composition figure saved to: {output_path}")


def plot_differences(differences):
    """Plot wet-minus-dry differences in percentage points."""

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    plot_df = differences.sort_values("wet_minus_dry_pp")

    fig, ax = plt.subplots(figsize=(9, 5))

    values = plot_df["wet_minus_dry_pp"]

    colors = [
        "#83B8A6" if value >= 0 else "#547AA5"
        for value in values
    ]

    bars = ax.barh(
        plot_df["intake_type"],
        values,
        color=colors,
    )

    ax.axvline(0, color="black", linewidth=1)

    ax.set_title(
        "Wet Minus Dry Intake Type Shares (2024)"
    )
    ax.set_xlabel("Difference in Percentage Points (Wet - Dry)")

    for bar, value in zip(bars, values):
        ax.annotate(
            f"{value:+.2f} pp",
            xy=(
                value,
                bar.get_y() + bar.get_height() / 2,
            ),
            xytext=(5 if value >= 0 else -5, 0),
            textcoords="offset points",
            ha="left" if value >= 0 else "right",
            va="center",
            fontsize=10,
        )

    margin = max(0.5, values.abs().max() * 0.25)
    ax.set_xlim(values.min() - margin, values.max() + margin)

    ax.grid(axis="x", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)

    fig.tight_layout()

    output_path = FIGURE_DIR / "q5_intake_type_differences.png"

    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"Q5 difference figure saved to: {output_path}")


def analyze_temperature_composition(merged_df, indicator, name):
    """Calculate intake type composition for a temperature classification."""

    counts = (
        merged_df
        .groupby([indicator, "Intake Type"])
        .size()
        .unstack(fill_value=0)
        .reindex(index=[0, 1], columns=INTAKE_TYPES, fill_value=0)
    )

    totals = counts.sum(axis=1)
    percentages = counts.div(totals, axis=0) * 100

    summary_rows = []

    for group in [0, 1]:
        for intake_type in INTAKE_TYPES:
            summary_rows.append({
                "weather_group": group,
                "intake_type": intake_type,
                "intake_events": int(counts.loc[group, intake_type]),
                "total_group_events": int(totals.loc[group]),
                "proportion_pct": round(
                    percentages.loc[group, intake_type], 4
                ),
            })

    summary = pd.DataFrame(summary_rows)

    differences = pd.DataFrame({
        "intake_type": INTAKE_TYPES,
        "reference_pct": percentages.loc[0].to_numpy(),
        "exposed_pct": percentages.loc[1].to_numpy(),
    })

    differences["difference_pp"] = (
        differences["exposed_pct"]
        - differences["reference_pct"]
    )

    differences = differences.round(4)

    assert int(totals.sum()) == 11815
    assert (totals > 0).all()
    assert abs(percentages.loc[0].sum() - 100) < 1e-9
    assert abs(percentages.loc[1].sum() - 100) < 1e-9
    assert abs(differences["difference_pp"].sum()) < 0.01

    print(f"\n=== {name}: Group Counts ===")
    print(totals.to_string())

    print(f"\n=== {name}: Intake Type Composition ===")
    print(summary.to_string(index=False))

    print(f"\n=== {name}: Percentage-Point Differences ===")
    print(differences.to_string(index=False))

    return summary, differences, percentages


def save_temperature_results(
    summary, differences, percentages, prefix, title, labels
):
    """Save temperature composition tables and two comparison figures."""

    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    figure_dir = (
        PROJECT_ROOT
        / "artifacts"
        / "weather_analysis"
        / "figures"
        / "05_intake_type"
    )
    figure_dir.mkdir(parents=True, exist_ok=True)

    summary_path = TABLE_DIR / f"{prefix}_composition.csv"
    difference_path = TABLE_DIR / f"{prefix}_differences.csv"

    summary.to_csv(summary_path, index=False)
    differences.to_csv(difference_path, index=False)

    colors = [
        "#547AA5",
        "#83B8A6",
        "#E2AD72",
        "#B681A8",
        "#8E9C65",
        "#A0A0A0",
    ]

    
    fig, ax = plt.subplots(figsize=(9, 6))
    bottom = [0.0, 0.0]

    for intake_type, color in zip(INTAKE_TYPES, colors):
        values = percentages[intake_type].to_numpy()

        bars = ax.bar(
            labels,
            values,
            bottom=bottom,
            label=intake_type,
            color=color,
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

        bottom = [b + v for b, v in zip(bottom, values)]

    ax.set_title(f"{title}: Intake Type Composition (2024)")
    ax.set_ylabel("Percentage of Intake Events (%)")
    ax.set_ylim(0, 100)
    ax.legend(
        title="Intake Type",
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
    )

    fig.tight_layout()

    composition_path = figure_dir / f"{prefix}_composition.png"
    fig.savefig(composition_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    
    plot_df = differences.sort_values("difference_pp")

    fig, ax = plt.subplots(figsize=(9, 5))

    values = plot_df["difference_pp"]

    bar_colors = [
        "#83B8A6" if value >= 0 else "#547AA5"
        for value in values
    ]

    bars = ax.barh(
        plot_df["intake_type"],
        values,
        color=bar_colors,
    )

    ax.axvline(0, color="black", linewidth=1)
    ax.set_title(f"{title}: Intake Share Differences (2024)")
    ax.set_xlabel(
        f"Difference in Percentage Points ({labels[1]} - {labels[0]})"
    )

    for bar, value in zip(bars, values):
        ax.annotate(
            f"{value:+.2f} pp",
            xy=(value, bar.get_y() + bar.get_height() / 2),
            xytext=(5 if value >= 0 else -5, 0),
            textcoords="offset points",
            ha="left" if value >= 0 else "right",
            va="center",
            fontsize=10,
        )

    margin = max(0.5, values.abs().max() * 0.25)
    ax.set_xlim(values.min() - margin, values.max() + margin)
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)

    fig.tight_layout()

    difference_figure_path = figure_dir / f"{prefix}_differences.png"
    fig.savefig(difference_figure_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"\nSaved: {summary_path}")
    print(f"Saved: {difference_path}")
    print(f"Saved: {composition_path}")
    print(f"Saved: {difference_figure_path}")


def main():
    intake_df, weather_df = load_data()

    merged_df = prepare_data(intake_df, weather_df)

    summary, differences, percentages = analyze_composition(merged_df)

    print("\n=== Q5: Intake Type Composition ===")
    print(summary.to_string(index=False))

    print("\n=== Q5: Wet Minus Dry Differences ===")
    print(differences.to_string(index=False))

    save_tables(summary, differences)
    plot_composition(percentages)
    plot_differences(differences)


    hot_summary, hot_diff, hot_pct = analyze_temperature_composition(
        merged_df,
        "hot_day",
        "Q5b: Extreme Heat",
    )

    save_temperature_results(
        hot_summary,
        hot_diff,
        hot_pct,
        "q5b_heat",
        "Extreme Heat",
        ["Non-Hot Days", "Hot Days"],
    )

    merged_df["cold_day"] = (
        merged_df["temp_min_c"] <= 5
    ).astype(int)

    cold_summary, cold_diff, cold_pct = analyze_temperature_composition(
        merged_df,
        "cold_day",
        "Q5c: Cold Weather (TMIN <= 5 C)",
    )

    save_temperature_results(
        cold_summary,
        cold_diff,
        cold_pct,
        "q5c_cold",
        "Cold Weather",
        ["Non-Cold Days", "Cold Days"],
    )

    freezing_summary, freezing_diff, freezing_pct = (
        analyze_temperature_composition(
            merged_df,
            "freezing_day",
            "Q5c Sensitivity: Freezing Weather",
        )
    )

    save_temperature_results(
        freezing_summary,
        freezing_diff,
        freezing_pct,
        "q5c_freezing_sensitivity",
        "Freezing Weather",
        ["Non-Freezing Days", "Freezing Days"],
    )



if __name__ == "__main__":
    main()
