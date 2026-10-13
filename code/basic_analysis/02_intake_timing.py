"""Describe monthly cat and dog intake records in 2024."""

import calendar
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ANIMALS = ["Cat", "Dog"]
AGE_GROUPS = [
    "<6 months",
    "6 months or older",
    "Recorded as 0 years",
    "Not recorded",
]
MONTHS = list(range(1, 13))
MONTH_LABELS = [calendar.month_abbr[month] for month in MONTHS]


def group_age(age):
    """Convert a recorded age string to a broad age group for monthly counts."""
    if not age.strip():
        return "Not recorded"

    number, unit = age.lower().split()
    number = float(number)
    unit = unit.rstrip("s")
    if number < 0:
        raise ValueError("Recorded ages cannot be negative.")
    # Zero years has insufficient precision to identify young kittens.
    if unit == "year" and number == 0:
        return "Recorded as 0 years"

    months_per_unit = {
        "year": 12,
        "month": 1,
        "week": 84 / 365.25,
        "day": 12 / 365.25,
    }
    months = number * months_per_unit[unit]
    return "<6 months" if months < 6 else "6 months or older"


def read_intakes(source):
    """Read a CSV path and return 2024 cat/dog records with month and age group."""
    intakes = pd.read_csv(source, dtype=str, keep_default_na=False)
    dates = pd.to_datetime(intakes["Intake Date"], format="%Y-%m-%d")
    if not dates.dt.year.eq(2024).all():
        raise ValueError("This analysis expects the cleaned 2024 intake file.")

    intakes["month"] = dates.dt.month
    pets = intakes.loc[intakes["Animal Type"].isin(ANIMALS)].copy()
    if set(pets["Animal Type"].unique()) != set(ANIMALS):
        raise ValueError("Both cat and dog intake records are needed.")
    pets["age_group"] = pets["Age upon Intake"].apply(group_age)
    return pets


def summarize_months(pets):
    """Return monthly species and cat-age tables from prepared intake records."""
    species_index = pd.MultiIndex.from_product(
        [ANIMALS, MONTHS], names=["animal_type", "month"]
    )
    species_counts = pets.groupby(["Animal Type", "month"]).size()
    species_table = species_counts.reindex(species_index, fill_value=0)
    species_table = species_table.reset_index(name="count")
    totals = pets["Animal Type"].value_counts()
    species_table["denominator"] = species_table["animal_type"].map(totals)
    species_table["percent"] = (
        species_table["count"] / species_table["denominator"] * 100
    )

    cats = pets.loc[pets["Animal Type"] == "Cat"]
    age_index = pd.MultiIndex.from_product(
        [MONTHS, AGE_GROUPS], names=["month", "age_group"]
    )
    age_counts = cats.groupby(["month", "age_group"]).size()
    age_table = age_counts.reindex(age_index, fill_value=0)
    age_table = age_table.reset_index(name="count")
    monthly_totals = cats.groupby("month").size().reindex(MONTHS, fill_value=0)
    age_table["denominator"] = age_table["month"].map(monthly_totals)
    age_table["percent"] = (
        age_table["count"] / age_table["denominator"].replace(0, float("nan")) * 100
    )
    if species_table["count"].sum() != len(pets):
        raise ValueError("Monthly species counts do not match the input records.")
    if age_table["count"].sum() != len(cats):
        raise ValueError("Monthly age counts do not match the cat records.")
    return species_table, age_table


def plot_monthly_intakes(table, destination):
    """Save a two-panel PNG from the monthly species table; return None."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
    colors = ["tab:blue", "tab:orange"]
    for animal, color, ax in zip(ANIMALS, colors, axes):
        rows = table.loc[table["animal_type"] == animal]
        ax.bar(rows["month"], rows["count"], color=color)
        ax.set_xticks(MONTHS, MONTH_LABELS, rotation=45)
        ax.set_xlabel("Month")
        total = rows["count"].sum()
        ax.set_title(f"{animal}s (n = {total:,})")
        ax.set_ylim(bottom=0)
    axes[0].set_ylabel("Intake records")
    fig.suptitle("AAC monthly cat and dog intakes, 2024")
    fig.text(
        0.5,
        0.015,
        "Counts represent intake events, not unique animals.",
        ha="center",
        fontsize=9,
    )
    fig.tight_layout(rect=[0, 0.05, 1, 0.97])
    fig.savefig(destination, dpi=150)
    plt.close(fig)


def plot_cat_ages(table, destination):
    """Save a stacked PNG from monthly cat-age counts; return None."""
    counts = table.pivot(index="month", columns="age_group", values="count")
    counts = counts.reindex(index=MONTHS, columns=AGE_GROUPS)
    if counts["Not recorded"].sum() == 0:
        counts = counts.drop(columns="Not recorded")
    ax = counts.plot(
        kind="bar",
        stacked=True,
        figsize=(10, 5.5),
        color=["tab:blue", "tab:orange", "gray", "lightgray"],
    )
    ax.set_title("AAC monthly cat intakes by recorded age, 2024")
    ax.set_xticklabels(MONTH_LABELS, rotation=0)
    ax.set_xlabel("Month")
    ax.set_ylabel("Intake records")
    ax.legend(title="Age at intake", loc="upper left", bbox_to_anchor=(1.01, 1))
    fig = ax.get_figure()
    fig.text(
        0.5,
        0.02,
        'Counts are intake events. "0 years" is kept separate because age is unclear.',
        ha="center",
        fontsize=9,
    )
    fig.tight_layout(rect=[0, 0.05, 1, 1])
    fig.savefig(destination, dpi=150)
    plt.close(fig)


def main():
    """Read project data and save two timing tables and PNGs; return None."""
    project = Path(__file__).resolve().parents[2]
    output = project / "artifacts/basic_analysis"
    figures = output / "figures/02_intake_timing"
    tables = output / "tables/02_intake_timing"
    figures.mkdir(parents=True, exist_ok=True)
    tables.mkdir(parents=True, exist_ok=True)

    pets = read_intakes(project / "data/processed/aac_intakes_clean.csv")
    species_table, age_table = summarize_months(pets)
    species_table.to_csv(
        tables / "monthly_intakes.csv", index=False, float_format="%.6f"
    )
    age_table.to_csv(tables / "monthly_cat_ages.csv", index=False, float_format="%.6f")
    plot_monthly_intakes(species_table, figures / "monthly_intakes.png")
    plot_cat_ages(age_table, figures / "monthly_cat_ages.png")
    print(f"Timing charts saved in {figures}")


if __name__ == "__main__":
    main()
