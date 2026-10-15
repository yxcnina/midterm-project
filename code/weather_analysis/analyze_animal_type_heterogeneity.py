
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd 


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

OUTPUT_DIR = PROJECT_ROOT / "artifacts" / "weather_analysis"
TABLE_DIR = OUTPUT_DIR / "tables"
FIGURE_DIR = OUTPUT_DIR / "figures" / "04_animal_type"


def load_data():
    """Load cleaned animal intake records and daily weather data."""

    intake_path = PROCESSED_DATA_DIR / "aac_intakes_clean.csv"
    weather_path = PROCESSED_DATA_DIR / "austin_weather_2024.csv"

    intake_df = pd.read_csv(
        intake_path,
        parse_dates=["Intake Date"]
    )

    weather_df = pd.read_csv(
        weather_path,
        parse_dates=["date"]
    )

    return intake_df, weather_df


def prepare_daily_animal_counts(intake_df, weather_df):
    """Count dog and cat intake events on each recorded intake day."""

    
    animal_df = intake_df.loc[
        intake_df["Animal Type"].isin(["Dog", "Cat"])
    ].copy()

    
    daily_counts = (
        animal_df
        .groupby(["Intake Date", "Animal Type"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
        .rename(columns={"Intake Date": "date"})
    )

    
    daily_df = weather_df[
        ["date", "wet_day"]
    ].merge(
        daily_counts,
        on="date",
        how="left",
        validate="one_to_one"
    )

    
    recorded_dates = intake_df["Intake Date"].drop_duplicates()

    daily_df = daily_df.loc[
        daily_df["date"].isin(recorded_dates)
    ].copy()

    
    daily_df[["Dog", "Cat"]] = (
        daily_df[["Dog", "Cat"]].fillna(0).astype(int)
    )

    
    assert len(daily_df) == 365
    assert daily_df["date"].is_unique

    assert daily_df["Dog"].sum() == 5188
    assert daily_df["Cat"].sum() == 6046

    assert (daily_df["wet_day"] == 0).sum() == 293
    assert (daily_df["wet_day"] == 1).sum() == 72

    return daily_df


def analyze_daily_counts(daily_df):
    """Summarize daily dog and cat intakes by wet/dry weather."""

    long_df = daily_df.melt(
        id_vars=["date", "wet_day"],
        value_vars=["Dog", "Cat"],
        var_name="animal_type",
        value_name="daily_intakes"
    )

    summary = (
        long_df
        .groupby(["animal_type", "wet_day"])
        .agg(
            days=("date", "count"),
            total_intakes=("daily_intakes", "sum"),
            mean_daily_intakes=("daily_intakes", "mean"),
            median_daily_intakes=("daily_intakes", "median"),
            std_daily_intakes=("daily_intakes", "std")
        )
        .reset_index()
    )

    summary["mean_daily_intakes"] = (
        summary["mean_daily_intakes"].round(2)
    )

    summary["std_daily_intakes"] = (
        summary["std_daily_intakes"].round(2)
    )

    return summary


def plot_daily_counts(summary):
    """Plot average daily dog and cat intakes on dry and wet days."""

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    pivot = summary.pivot(
        index="animal_type",
        columns="wet_day",
        values="mean_daily_intakes"
    )

    pivot = pivot.reindex(["Dog", "Cat"])

    ax = pivot.rename(
        columns={0: "Dry Days", 1: "Wet Days"}
    ).plot(
        kind="bar",
        figsize=(8, 5),
        color=["#547AA5", "#83B8A6"],
        width=0.7,
        rot=0
    )

    ax.set_title(
        "Average Daily Dog and Cat Intakes: Dry vs. Wet Days (2024)"
    )
    ax.set_xlabel("Animal Type")
    ax.set_ylabel("Average Daily Intake Count")
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)

    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f", padding=3)

    fig = ax.get_figure()
    fig.tight_layout()

    output_path = FIGURE_DIR / "q4a_daily_intakes_by_animal_type.png"

    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"\nQ4a figure saved to: {output_path}")


def save_summary(summary):
    """Save Q4a summary statistics to CSV."""

    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    output_path = TABLE_DIR / "q4a_daily_intakes_by_animal_type.csv"

    summary.to_csv(output_path, index=False)

    print(f"Q4a summary saved to: {output_path}")



def analyze_stray_proportions(intake_df, weather_df):
    """Compare stray intake proportions by animal type and rainfall."""

    animal_df = intake_df.loc[
        intake_df["Animal Type"].isin(["Dog", "Cat"])
    ].copy()

    weather_dates = weather_df[
        ["date", "wet_day"]
    ].copy()

    merged_df = animal_df.merge(
        weather_dates,
        left_on="Intake Date",
        right_on="date",
        how="left",
        validate="many_to_one",
        indicator=True
    )

    # Validate that all dog/cat intake events match weather dates.
    assert (merged_df["_merge"] == "both").all()
    assert merged_df["wet_day"].notna().all()
    assert len(merged_df) == 11234

    merged_df["is_stray"] = (
        merged_df["Intake Type"] == "Stray"
    ).astype(int)

    summary = (
        merged_df
        .groupby(["Animal Type", "wet_day"])
        .agg(
            total_intakes=("is_stray", "size"),
            stray_intakes=("is_stray", "sum")
        )
        .reset_index()
    )

    summary["non_stray_intakes"] = (
        summary["total_intakes"] - summary["stray_intakes"]
    )

    summary["stray_proportion_pct"] = (
        summary["stray_intakes"]
        / summary["total_intakes"]
        * 100
    ).round(2)

    return summary


def save_and_plot_stray_proportions(summary):
    """Save Q4b summary and chart."""

    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    table_path = TABLE_DIR / "q4b_stray_proportions_by_animal_type.csv"
    summary.to_csv(table_path, index=False)

    pivot = summary.pivot(
        index="Animal Type",
        columns="wet_day",
        values="stray_proportion_pct"
    )

    pivot = pivot.reindex(["Dog", "Cat"])

    ax = pivot.rename(
        columns={0: "Dry Days", 1: "Wet Days"}
    ).plot(
        kind="bar",
        figsize=(8, 5),
        color=["#547AA5", "#83B8A6"],
        width=0.7,
        rot=0
    )

    ax.set_title(
        "Stray Intake Proportions by Animal Type and Rainfall (2024)"
    )
    ax.set_xlabel("Animal Type")
    ax.set_ylabel("Stray Intake Proportion (%)")
    ax.set_ylim(0, 100)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)

    for container in ax.containers:
        ax.bar_label(
            container,
            fmt="%.2f%%",
            padding=3
        )

    fig = ax.get_figure()
    fig.tight_layout()

    figure_path = FIGURE_DIR / "q4b_stray_proportions_by_animal_type.png"

    fig.savefig(figure_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"\nQ4b summary saved to: {table_path}")
    print(f"Q4b figure saved to: {figure_path}")



def analyze_adoption_proportions(outcome_df, weather_df):
    """Compare adoption outcome proportions by animal type and heat."""

    animal_df = outcome_df.loc[
        outcome_df["Animal Type"].isin(["Dog", "Cat"])
    ].copy()

    weather_dates = weather_df[
        ["date", "hot_day"]
    ].copy()

    merged_df = animal_df.merge(
        weather_dates,
        left_on="Outcome Date",
        right_on="date",
        how="left",
        validate="many_to_one",
        indicator=True
    )

    
    assert len(merged_df) == 11244
    assert (merged_df["_merge"] == "both").all()
    assert merged_df["hot_day"].notna().all()

    
    valid_df = merged_df.dropna(
        subset=["Outcome Type"]
    ).copy()

    
    valid_df["is_adoption"] = (
        valid_df["Outcome Type"] == "Adoption"
    ).astype(int)

    
    summary = (
        valid_df
        .groupby(["Animal Type", "hot_day"])
        .agg(
            total_outcomes=("is_adoption", "size"),
            adoption_outcomes=("is_adoption", "sum")
        )
        .reset_index()
    )

    summary["non_adoption_outcomes"] = (
        summary["total_outcomes"]
        - summary["adoption_outcomes"]
    )

    summary["adoption_proportion_pct"] = (
        summary["adoption_outcomes"]
        / summary["total_outcomes"]
        * 100
    ).round(2)

    assert summary["total_outcomes"].sum() == len(valid_df)

    print(
        f"\nDog/Cat outcome events: {len(animal_df)}"
    )
    print(
        f"Excluded missing outcome types: "
        f"{len(animal_df) - len(valid_df)}"
    )
    print(
        f"Valid Dog/Cat outcome events: {len(valid_df)}"
    )

    return summary


def save_and_plot_adoption_proportions(summary):
    """Save Q4c adoption summary and grouped bar chart."""

    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    table_path = (
        TABLE_DIR / "q4c_adoption_proportions_by_animal_type.csv"
    )

    summary.to_csv(table_path, index=False)

    pivot = summary.pivot(
        index="Animal Type",
        columns="hot_day",
        values="adoption_proportion_pct"
    )

    pivot = pivot.reindex(["Dog", "Cat"])

    ax = pivot.rename(
        columns={0: "Non-Hot Days", 1: "Hot Days"}
    ).plot(
        kind="bar",
        figsize=(8, 5),
        color=["#547AA5", "#D98C6A"],
        width=0.7,
        rot=0
    )

    ax.set_title(
        "Adoption Outcome Proportions by Animal Type and Heat (2024)"
    )
    ax.set_xlabel("Animal Type")
    ax.set_ylabel("Adoption Outcome Proportion (%)")
    ax.set_ylim(0, 100)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)

    
    for container in ax.containers:
        ax.bar_label(
            container,
            fmt="%.2f%%",
            padding=3
        )

    fig = ax.get_figure()
    fig.tight_layout()

    figure_path = (
        FIGURE_DIR / "q4c_adoption_proportions_by_animal_type.png"
    )

    fig.savefig(
        figure_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)

    print(f"\nQ4c summary saved to: {table_path}")
    print(f"Q4c figure saved to: {figure_path}")


def main():
    intake_df, weather_df = load_data()

    daily_df = prepare_daily_animal_counts(
        intake_df,
        weather_df
    )

    summary = analyze_daily_counts(daily_df)

    print("\n=== Q4a: Daily Intake Counts by Animal Type ===")
    print(summary.to_string(index=False))

    plot_daily_counts(summary)
    save_summary(summary)

    
    stray_summary = analyze_stray_proportions(
        intake_df,
        weather_df
    )

    print("\n=== Q4b: Stray Intake Proportions by Animal Type ===")
    print(stray_summary.to_string(index=False))

    save_and_plot_stray_proportions(stray_summary)

    
    outcome_path = (
        PROCESSED_DATA_DIR / "aac_outcomes_clean.csv"
    )

    outcome_df = pd.read_csv(
        outcome_path,
        parse_dates=["Outcome Date"]
    )

    adoption_summary = analyze_adoption_proportions(
        outcome_df,
        weather_df
    )

    print("\n=== Q4c: Adoption Proportions by Animal Type ===")
    print(adoption_summary.to_string(index=False))

    save_and_plot_adoption_proportions(adoption_summary)


if __name__ == "__main__":
    main()
