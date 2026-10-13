"""Summarize the types of cat and dog outcome records at AAC in 2024."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def read_outcomes(source):
    """Read a CSV path and return the complete 2024 cat and dog outcome rows."""
    outcomes = pd.read_csv(source, dtype=str, keep_default_na=False)
    dates = pd.to_datetime(outcomes["Outcome Date"], format="%Y-%m-%d")
    if not dates.dt.year.eq(2024).all():
        raise ValueError("This analysis expects the cleaned 2024 outcome file.")

    pets = outcomes[outcomes["Animal Type"].isin(["Cat", "Dog"])].copy()
    pets["Outcome Type"] = pets["Outcome Type"].replace("", "Not recorded")
    return pets


def summarize_outcomes(pets):
    """Return counts and within-species percentages from cat/dog outcome rows."""
    counts = pd.crosstab(pets["Animal Type"], pets["Outcome Type"])
    counts = counts.reindex(index=["Cat", "Dog"], fill_value=0)
    category_order = counts.sum().sort_values(ascending=False).index
    counts = counts.reindex(columns=category_order)
    totals = counts.sum(axis=1)
    if totals.eq(0).any():
        raise ValueError("Both cats and dogs must have outcome records.")

    summary = counts.reset_index().melt(
        id_vars="Animal Type",
        var_name="outcome_type",
        value_name="count",
    )
    summary = summary.rename(columns={"Animal Type": "animal_type"})
    summary["denominator"] = summary["animal_type"].map(totals)
    summary["percent"] = summary["count"] / summary["denominator"] * 100
    assert summary["count"].sum() == len(pets)
    return summary


def plot_outcomes(summary, figures_folder):
    """Save a PNG stacked chart from the outcome summary; return None."""
    order = summary["outcome_type"].drop_duplicates()
    percentages = summary.pivot(
        index="animal_type",
        columns="outcome_type",
        values="percent",
    )
    percentages = percentages.reindex(index=["Cat", "Dog"], columns=order)
    totals = summary.groupby("animal_type")["count"].sum()
    ax = percentages.plot(
        kind="barh",
        stacked=True,
        figsize=(10, 5),
        colormap="tab10",
        width=0.55,
    )
    ax.invert_yaxis()
    ax.set_yticklabels(
        [f"{animal}s (n = {totals[animal]:,})" for animal in percentages.index]
    )
    ax.set_xlim(0, 100)
    ax.set_xlabel("Outcome records (%)")
    ax.set_ylabel("")
    ax.set_title("AAC recorded outcomes, 2024")
    for bars in ax.containers:
        labels = [
            f"{bar.get_width():.1f}%" if bar.get_width() >= 5 else "" for bar in bars
        ]
        ax.bar_label(bars, labels=labels, label_type="center", fontsize=10)
    ax.legend(
        title="Recorded outcome type",
        bbox_to_anchor=(0.5, -0.2),
        loc="upper center",
        ncol=3,
        fontsize=9,
    )
    ax.figure.text(
        0.5,
        0.015,
        "All outcome types are retained. Small shares are listed in the CSV table.",
        ha="center",
        fontsize=9,
    )
    ax.figure.tight_layout(rect=(0, 0.045, 1, 1))
    ax.figure.savefig(figures_folder / "outcome_distribution.png", dpi=150)
    plt.close(ax.figure)


def main():
    """Read project data, save the outcome table and chart, and return None."""
    project = Path(__file__).resolve().parents[2]
    source = project / "data/processed/aac_outcomes_clean.csv"
    output = project / "artifacts/basic_analysis"
    figures_folder = output / "figures/04_outcome_profile"
    tables_folder = output / "tables/04_outcome_profile"
    figures_folder.mkdir(parents=True, exist_ok=True)
    tables_folder.mkdir(parents=True, exist_ok=True)

    pets = read_outcomes(source)
    summary = summarize_outcomes(pets)
    summary.to_csv(
        tables_folder / "outcome_distribution.csv",
        index=False,
        float_format="%.6f",
    )
    plot_outcomes(summary, figures_folder)
    print(summary.to_string(index=False))
    print(f"Outcome profile saved in {figures_folder}")


if __name__ == "__main__":
    main()
