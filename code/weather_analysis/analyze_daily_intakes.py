
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



def analyze_wet_vs_dry(daily_df):
    """Compare daily intake counts between wet and dry days."""

    recorded_days = daily_df.dropna(
        subset=["intake_count"]
    ).copy()

    summary = recorded_days.groupby("wet_day")["intake_count"].agg(
        days="count",
        total_intakes="sum",
        mean_daily_intakes="mean",
        median_daily_intakes="median",
        std_daily_intakes="std",
    )

    print("\n--- Q1: Wet vs. Dry Days ---")
    print(summary.round(2).to_string())

    wet_mean = summary.loc[1, "mean_daily_intakes"]
    dry_mean = summary.loc[0, "mean_daily_intakes"]

    print(f"\nWet minus Dry mean difference: {wet_mean - dry_mean:.2f}")
    print(f"Total recorded days: {len(recorded_days)}")

    return summary


def check_missing_day_sensitivity(daily_df):
    """Check results when missing intake counts are treated as zero."""

    zero_filled = daily_df.copy()
    zero_filled["intake_count"] = zero_filled["intake_count"].fillna(0)

    sensitivity = zero_filled.groupby("wet_day")["intake_count"].agg(
        days="count",
        total_intakes="sum",
        mean_daily_intakes="mean",
    )

    print("\n--- Sensitivity Check: Missing Day as Zero ---")
    print(sensitivity.round(2).to_string())

    wet_mean = sensitivity.loc[1, "mean_daily_intakes"]
    dry_mean = sensitivity.loc[0, "mean_daily_intakes"]

    print(
        f"\nWet minus Dry mean difference (zero-filled): "
        f"{wet_mean - dry_mean:.2f}"
    )

    return sensitivity



def plot_wet_vs_dry(summary):
    """Create and save a bar chart of average daily intake counts."""

    
    labels = ["Dry Days", "Wet Days"]
    means = [
        summary.loc[0, "mean_daily_intakes"],
        summary.loc[1, "mean_daily_intakes"],
    ]

    fig, ax = plt.subplots(figsize=(7, 5))

    bars = ax.bar(
        labels,
        means,
        color=["#547AA5", "#83B8A6"],
        width=0.55,
    )

    ax.set_title(
        "Average Daily Animal Intakes: Dry vs. Wet Days (2024)"
    )
    ax.set_ylabel("Average Daily Intake Count")
    ax.set_ylim(0, max(means) * 1.2)

    for bar, mean in zip(bars, means):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            f"{mean:.2f}",
            ha="center",
            va="bottom",
        )

    ax.text(
        0.5,
        -0.15,
        "Main analysis: 365 recorded intake days; Dec 25 excluded.",
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
        / "01_daily_intakes"
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "wet_vs_dry_daily_intakes.png"

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(f"\nFigure saved to: {output_path}")

    return output_path


def save_q1_summary(summary):
    """Save the wet-versus-dry descriptive statistics as a CSV."""

    output_dir = (
        PROJECT_ROOT
        / "artifacts"
        / "weather_analysis"
        / "tables"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "q1_daily_intakes_summary.csv"

    output_df = summary.reset_index().copy()
    output_df["weather_condition"] = output_df["wet_day"].map(
        {0: "Dry", 1: "Wet"}
    )

    output_df = output_df[
        [
            "weather_condition",
            "wet_day",
            "days",
            "total_intakes",
            "mean_daily_intakes",
            "median_daily_intakes",
            "std_daily_intakes",
        ]
    ]

    output_df.to_csv(output_path, index=False)

    print(f"\nSummary table saved to: {output_path}")

    return output_path


def plot_intake_boxplot(daily_df):
    """Plot daily intake count distributions for dry and wet days."""

    
    recorded_days = daily_df.dropna(
        subset=["intake_count"]
    ).copy()

    
    dry_counts = recorded_days.loc[
        recorded_days["wet_day"] == 0,
        "intake_count"
    ]

    wet_counts = recorded_days.loc[
        recorded_days["wet_day"] == 1,
        "intake_count"
    ]

    
    assert len(dry_counts) == 293
    assert len(wet_counts) == 72

    
    fig, ax = plt.subplots(figsize=(8, 5))

    box = ax.boxplot(
        [dry_counts, wet_counts],
        tick_labels=["Dry Days", "Wet Days"],
        patch_artist=True,
        showmeans=True,
        meanprops={
            "marker": "D",
            "markerfacecolor": "white",
            "markeredgecolor": "black"
        },
        medianprops={
            "color": "black",
            "linewidth": 2
        }
    )

    
    colors = ["#547AA5", "#83B8A6"]

    for patch, color in zip(box["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    
    ax.set_title(
        "Daily Animal Intake Distribution: Dry vs. Wet Days (2024)"
    )
    ax.set_ylabel("Daily Intake Count")
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)

    
    ax.plot([], [], "D", color="black", label="Mean")
    ax.plot([], [], "-", color="black", label="Median")
    ax.legend(loc="upper right")

    fig.text(
        0.5,
        0.01,
        "293 dry days and 72 wet days; December 25 excluded.",
        ha="center",
        fontsize=9
    )

    fig.tight_layout(rect=[0, 0.05, 1, 1])

    
    output_dir = (
        PROJECT_ROOT
        / "artifacts"
        / "weather_analysis"
        / "figures"
        / "01_daily_intakes"
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "wet_vs_dry_daily_intakes_boxplot.png"

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)

    print(f"\nQ1 boxplot saved to: {output_path}")

    return output_path


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
     
    summary = analyze_wet_vs_dry(daily_df)

    check_missing_day_sensitivity(daily_df)

    plot_wet_vs_dry(summary)
    plot_intake_boxplot(daily_df)
    save_q1_summary(summary) 



if __name__ == "__main__": 
    main() 
