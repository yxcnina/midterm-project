"""Compare the recorded intake types and conditions of cats and dogs in 2024."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ANIMALS = ["Cat", "Dog"]


def read_intakes(source):
    """Read a CSV path and return 2024 cat/dog intake records with missing labels."""
    intakes = pd.read_csv(source, dtype=str, keep_default_na=False)
    dates = pd.to_datetime(intakes["Intake Date"], format="%Y-%m-%d")
    if not dates.dt.year.eq(2024).all():
        raise ValueError("This analysis expects the cleaned 2024 intake file.")

    pets = intakes.loc[intakes["Animal Type"].isin(ANIMALS)].copy()
    if set(pets["Animal Type"].unique()) != set(ANIMALS):
        raise ValueError("Both cat and dog intake records are needed.")
    for column in ["Intake Type", "Intake Condition"]:
        pets[column] = pets[column].replace(r"^\s*$", "Not recorded", regex=True)
    return pets


def summarize_categories(pets, column):
    """Return all category counts and species-level percentages for a column."""
    order = pets[column].value_counts().index
    index = pd.MultiIndex.from_product(
        [ANIMALS, order], names=["animal_type", "category"]
    )
    counts = pets.groupby(["Animal Type", column]).size()
    table = counts.reindex(index, fill_value=0).reset_index(name="count")
    totals = pets["Animal Type"].value_counts()
    table["denominator"] = table["animal_type"].map(totals)
    table["percent"] = table["count"] / table["denominator"] * 100
    if table["count"].sum() != len(pets):
        raise ValueError("Category counts do not match the input records.")
    return table


def plot_categories(table, title, destination):
    """Save a 100% stacked PNG of category percentages; return None."""
    category_order = table["category"].drop_duplicates().tolist()
    percentages = table.pivot(index="animal_type", columns="category", values="percent")
    percentages = percentages.reindex(index=ANIMALS, columns=category_order)
    colors = list(plt.get_cmap("tab20").colors)
    ax = percentages.plot(
        kind="barh", stacked=True, figsize=(11, 5), color=colors, width=0.55
    )
    ax.invert_yaxis()
    ax.set_title(title)
    ax.set_xlabel("Share of each species' intake records (%)")
    ax.set_ylabel("")
    ax.set_xlim(0, 100)
    totals = table.groupby("animal_type")["count"].sum()
    ax.set_yticklabels([f"{animal}s (n = {totals[animal]:,})" for animal in ANIMALS])
    for container in ax.containers:
        labels = [
            f"{bar.get_width():.1f}%" if bar.get_width() >= 5 else ""
            for bar in container
        ]
        ax.bar_label(container, labels=labels, label_type="center", fontsize=9)
    handles, labels = ax.get_legend_handles_labels()
    ax.get_legend().remove()
    fig = ax.get_figure()
    fig.legend(
        handles,
        labels,
        title="Recorded category",
        loc="lower center",
        bbox_to_anchor=(0.55, 0.07),
        ncol=4,
        fontsize=9,
    )
    fig.text(
        0.5,
        0.015,
        "Intake events, not unique animals. All categories shown; "
        "labels shown at 5% or above.",
        ha="center",
        fontsize=9,
    )
    bottom = 0.40 if len(category_order) > 4 else 0.29
    fig.subplots_adjust(left=0.15, right=0.98, top=0.88, bottom=bottom)
    fig.savefig(destination, dpi=150)
    plt.close(fig)


def main():
    """Read project data and save two context tables and PNGs; return None."""
    project = Path(__file__).resolve().parents[2]
    output = project / "artifacts/basic_analysis"
    figures = output / "figures/03_intake_context"
    tables = output / "tables/03_intake_context"
    figures.mkdir(parents=True, exist_ok=True)
    tables.mkdir(parents=True, exist_ok=True)

    pets = read_intakes(project / "data/processed/aac_intakes_clean.csv")
    for column, name in [
        ("Intake Type", "intake_type"),
        ("Intake Condition", "intake_condition"),
    ]:
        table = summarize_categories(pets, column)
        table.to_csv(tables / f"{name}.csv", index=False, float_format="%.6f")
        plot_categories(table, f"AAC {column.lower()}, 2024", figures / f"{name}.png")
    print(f"Intake context charts saved in {figures}")


if __name__ == "__main__":
    main()
