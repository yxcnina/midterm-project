"""Compare adoption shares within 2024 cat and dog outcome-record groups."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

AGE_ORDER = [
    "<6 months",
    "6 to <12 months",
    "1 to <3 years",
    "3 to <7 years",
    "7+ years",
    "Recorded as 0 years",
    "Not recorded",
]
SEX_ORDER = ["Female", "Male", "Unknown", "Not recorded"]


def group_age(age):
    """Return an approximate age-group label from a recorded age string."""
    if age.strip() == "":
        return "Not recorded"

    number, unit = age.lower().split()
    number = float(number)
    unit = unit.rstrip("s")
    # A rounded zero-year label does not establish an exact age.
    if unit == "year" and number == 0:
        return "Recorded as 0 years"

    months_per_unit = {
        "year": 12,
        "month": 1,
        "week": 84 / 365.25,
        "day": 12 / 365.25,
    }
    months = number * months_per_unit[unit]
    if months < 6:
        return "<6 months"
    elif months < 12:
        return "6 to <12 months"
    elif months < 36:
        return "1 to <3 years"
    elif months < 84:
        return "3 to <7 years"
    else:
        return "7+ years"


def read_outcomes(source):
    """Read an outcome CSV path and return cat/dog rows with descriptive groups."""
    outcomes = pd.read_csv(source, dtype=str, keep_default_na=False)
    dates = pd.to_datetime(outcomes["Outcome Date"], format="%Y-%m-%d")
    if not dates.dt.year.eq(2024).all():
        raise ValueError("This analysis expects the cleaned 2024 outcome file.")

    pets = outcomes[outcomes["Animal Type"].isin(["Cat", "Dog"])].copy()
    sex_map = {
        "Intact Female": "Female",
        "Spayed Female": "Female",
        "Intact Male": "Male",
        "Neutered Male": "Male",
        "Unknown": "Unknown",
        "": "Not recorded",
    }
    pets["Age group"] = pets["Age upon Outcome"].apply(group_age)
    pets["Sex"] = pets["Sex upon Outcome"].map(sex_map)
    if pets["Sex"].isna().any():
        raise ValueError("An unexpected sex label needs to be checked.")
    pets["Sex/status label"] = pets["Sex upon Outcome"].replace("", "Not recorded")
    pets["Breed label"] = pets["Breed"].replace("", "Not recorded")
    pets["Color label"] = pets["Color"].replace("", "Not recorded")
    pets["Adoption"] = pets["Outcome Type"].eq("Adoption")
    return pets


def summarize_traits(pets):
    """Return group sizes and adoption counts/shares from prepared outcome rows."""
    features = {
        "age": "Age group",
        "sex": "Sex",
        "breed": "Breed label",
        "color": "Color label",
        "sex_status": "Sex/status label",
    }
    tables = []
    for animal in ["Cat", "Dog"]:
        subset = pets[pets["Animal Type"] == animal]
        if subset.empty:
            raise ValueError(f"No {animal} outcome records found.")
        for feature, column in features.items():
            summary = subset.groupby(column)["Adoption"].agg(
                outcome_records="size",
                adoption_records="sum",
            )
            summary = summary.reset_index().rename(columns={column: "category"})
            summary["animal_type"] = animal
            summary["feature"] = feature
            summary["adoption_share_percent"] = (
                summary["adoption_records"] / summary["outcome_records"] * 100
            )
            summary = summary.sort_values(
                ["outcome_records", "category"], ascending=[False, True]
            )
            summary["shown_in_chart"] = feature in ["age", "sex"]
            if feature in ["breed", "color"]:
                # Choose common labels before comparing their adoption shares.
                summary.loc[summary.head(5).index, "shown_in_chart"] = True
            assert summary["outcome_records"].sum() == len(subset)
            assert summary["adoption_records"].sum() == subset["Adoption"].sum()
            tables.append(summary)

    combined = pd.concat(tables, ignore_index=True)
    return combined[
        [
            "animal_type",
            "feature",
            "category",
            "outcome_records",
            "adoption_records",
            "adoption_share_percent",
            "shown_in_chart",
        ]
    ]


def plot_comparison(summary, feature, figures_folder):
    """Save one PNG dot plot for a feature in the summary; return None."""
    titles = {
        "age": "Recorded age at outcome",
        "sex": "Recorded sex at outcome",
        "breed": "Five most common recorded breed labels",
        "color": "Five most common recorded color labels",
    }
    selected = summary[(summary["feature"] == feature) & summary["shown_in_chart"]]
    fig, axes = plt.subplots(1, 2, figsize=(13, 6), sharex=True)
    colors = {"Cat": "tab:blue", "Dog": "tab:orange"}
    for animal, ax in zip(["Cat", "Dog"], axes):
        table = selected[selected["animal_type"] == animal].copy()
        if feature in ["age", "sex"]:
            order = AGE_ORDER if feature == "age" else SEX_ORDER
            table = table.set_index("category").reindex(order)
            table = table.dropna(subset=["outcome_records"]).reset_index()
        labels = [
            f"{row.category}\n(n = {row.outcome_records:,.0f})"
            for row in table.itertuples()
        ]
        positions = range(len(table))
        ax.scatter(table["adoption_share_percent"], positions, color=colors[animal])
        ax.set_yticks(list(positions), labels=labels)
        ax.invert_yaxis()
        ax.set_xlim(-3, 103)
        ax.set_xticks([0, 25, 50, 75, 100])
        ax.set_ylim(len(table) - 0.5, -0.5)
        ax.grid(axis="x", linestyle=":", alpha=0.4)
        ax.set_axisbelow(True)
        ax.set_title(f"{animal}s")
        ax.set_xlabel("Adoption share of group outcome records (%)")
        for position, share in enumerate(table["adoption_share_percent"]):
            ax.annotate(
                f"{share:.1f}%",
                (share, position),
                xytext=(-6 if share > 90 else 6, 0),
                textcoords="offset points",
                ha="right" if share > 90 else "left",
                va="center",
                fontsize=9,
            )

    fig.suptitle(f"AAC adoption shares, 2024: {titles[feature]}", fontsize=13)
    note = "n = all outcome records in the group. Unadjusted descriptive comparisons."
    if feature in ["breed", "color"]:
        note += "\nLabels selected by outcome frequency, not adoption share."
    else:
        note += (
            "\nAge and sex are measured at outcome; these are not intake-cohort rates."
        )
    fig.text(0.5, 0.02, note, ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0.09, 1, 0.95))
    fig.savefig(figures_folder / f"adoption_by_{feature}.png", dpi=150)
    plt.close(fig)


def main():
    """Read project data, save the trait table and four charts, and return None."""
    project = Path(__file__).resolve().parents[2]
    source = project / "data/processed/aac_outcomes_clean.csv"
    output = project / "artifacts/basic_analysis"
    figures_folder = output / "figures/05_trait_comparisons"
    tables_folder = output / "tables/05_trait_comparisons"
    figures_folder.mkdir(parents=True, exist_ok=True)
    tables_folder.mkdir(parents=True, exist_ok=True)

    pets = read_outcomes(source)
    summary = summarize_traits(pets)
    summary.to_csv(
        tables_folder / "adoption_by_trait.csv",
        index=False,
        float_format="%.6f",
    )
    for feature in ["age", "sex", "breed", "color"]:
        plot_comparison(summary, feature, figures_folder)
    print(summary[summary["shown_in_chart"]].to_string(index=False))
    print(f"Trait comparisons saved in {figures_folder}")


if __name__ == "__main__":
    main()
