"""Summarize 2024 cat and dog intakes with age, sex, and breed charts."""

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


def group_age(age):
    """Return an approximate age-group label from a recorded age string."""
    if age.strip() == "":
        return "Not recorded"

    number, unit = age.lower().split()
    number = float(number)
    unit = unit.rstrip("s")

    # "0 years" does not give enough precision to assign an age group.
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


def read_intakes(source):
    """Read an intake CSV path; return all records and prepared cat/dog records."""
    intakes = pd.read_csv(source, dtype=str, keep_default_na=False)
    dates = pd.to_datetime(intakes["Intake Date"], format="%Y-%m-%d")
    if not dates.dt.year.eq(2024).all():
        raise ValueError("This analysis expects the cleaned 2024 intake file.")

    is_cat_or_dog = intakes["Animal Type"].isin(["Cat", "Dog"])
    pets = intakes.loc[is_cat_or_dog].copy()
    pets["Age group"] = pets["Age upon Intake"].apply(group_age)

    sex_map = {
        "Intact Female": "Female",
        "Spayed Female": "Female",
        "Intact Male": "Male",
        "Neutered Male": "Male",
        "Unknown": "Unknown",
        "": "Not recorded",
    }
    status_map = {
        "Intact Female": "Intact",
        "Intact Male": "Intact",
        "Spayed Female": "Spayed or neutered",
        "Neutered Male": "Spayed or neutered",
        "Unknown": "Unknown",
        "": "Not recorded",
    }
    pets["Sex"] = pets["Sex upon Intake"].map(sex_map)
    pets["Sterilization"] = pets["Sex upon Intake"].map(status_map)
    missing_status = pets[["Sex", "Sterilization"]].isna()
    if missing_status.to_numpy().any():
        raise ValueError("An unexpected sex/status label needs to be checked.")

    pets["Breed label"] = pets["Breed"].replace("", "Not recorded")
    return intakes, pets


def summarize(data, column, animal, feature, order=None):
    """Return category counts and percentages for a column in a DataFrame.

    Animal and feature label the output; order optionally sets category order.
    Percentages use every row in data as the denominator.
    """
    counts = data[column].value_counts()
    if order is not None:
        counts = counts.reindex(order, fill_value=0)

    counts = counts.rename_axis("category")
    table = counts.reset_index(name="count")
    table["animal_type"] = animal
    table["feature"] = feature
    table["denominator"] = len(data)
    table["percent"] = table["count"] / table["denominator"] * 100
    assert table["count"].sum() == len(data)

    return table[
        ["animal_type", "feature", "category", "count", "denominator", "percent"]
    ]


def plot_age_distribution(summary, figures_folder):
    """Save a PNG age chart from the summary and return the age-percentage table."""
    age_table = summary[summary["feature"] == "age"]
    age_percent = age_table.pivot(
        index="category",
        columns="animal_type",
        values="percent",
    )
    age_percent = age_percent.reindex(index=AGE_ORDER, columns=["Cat", "Dog"])
    if age_percent.loc["Not recorded"].sum() == 0:
        age_percent = age_percent.drop("Not recorded")

    ax = age_percent.plot(kind="bar", figsize=(9, 5), rot=0)
    ax.set_title("AAC intake age distribution, 2024")
    ax.set_xlabel("Recorded age at intake")
    ax.set_ylabel("Intake records (%)")

    labels = []
    for label in age_percent.index:
        label = label.replace(" months", "\nmonths")
        label = label.replace(" years", "\nyears")
        labels.append(label)
    ax.set_xticklabels(labels)
    ax.legend(title="Animal type")

    plt.tight_layout()
    plt.savefig(figures_folder / "age_distribution.png", dpi=150)
    plt.close()
    return age_percent


def plot_sex_distribution(summary, figures_folder):
    """Save a PNG sex chart from the summary; return no value."""
    sex_table = summary[summary["feature"] == "sex"]
    sex_percent = sex_table.pivot(
        index="category",
        columns="animal_type",
        values="percent",
    )
    sex_percent = sex_percent.reindex(
        index=["Female", "Male", "Unknown", "Not recorded"],
        columns=["Cat", "Dog"],
    )
    if sex_percent.loc["Not recorded"].sum() == 0:
        sex_percent = sex_percent.drop("Not recorded")

    ax = sex_percent.plot(kind="bar", figsize=(8, 4.5), rot=0)
    ax.set_title("AAC sex at intake, 2024")
    ax.set_xlabel("Recorded sex")
    ax.set_ylabel("Intake records (%)")
    ax.legend(title="Animal type")

    plt.tight_layout()
    plt.savefig(figures_folder / "sex_distribution.png", dpi=150)
    plt.close()


def plot_breed_distribution(summary, figures_folder):
    """Save a PNG of the top five breed labels and the remainder; return None."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharex=True)
    colors = {"Cat": "tab:blue", "Dog": "tab:orange"}

    for animal, ax in zip(["Cat", "Dog"], axes):
        breed_table = summary[
            (summary["animal_type"] == animal) & (summary["feature"] == "breed")
        ]
        top_breeds = breed_table.nlargest(5, "count")
        denominator = int(breed_table["denominator"].iloc[0])
        remaining_count = denominator - top_breeds["count"].sum()
        other_labels = pd.DataFrame(
            {
                "category": ["Other recorded labels"],
                "percent": [remaining_count / denominator * 100],
            }
        )
        displayed_breeds = pd.concat(
            [top_breeds[["category", "percent"]], other_labels],
            ignore_index=True,
        )
        bar_colors = [colors[animal]] * len(top_breeds) + ["lightgray"]
        bars = ax.barh(
            displayed_breeds["category"],
            displayed_breeds["percent"],
            color=bar_colors,
        )
        ax.invert_yaxis()
        ax.set_xlim(0, 100)
        ax.set_xticks([0, 25, 50, 75, 100])
        ax.set_xlabel("Intake records (%)")
        ax.set_title(f"{animal}s (n = {denominator:,})")
        ax.bar_label(bars, fmt="%.1f%%", padding=3, fontsize=9)

    fig.suptitle("AAC recorded breed labels, 2024: top 5 and all other labels")
    fig.tight_layout()
    fig.savefig(figures_folder / "breed_distribution.png", dpi=150)
    plt.close(fig)


def main():
    """Read project data, save the summary and three charts, and return None."""
    project = Path(__file__).resolve().parents[2]
    source = project / "data/processed/aac_intakes_clean.csv"
    output = project / "artifacts/basic_analysis"
    theme = Path(__file__).stem
    figures_folder = output / "figures" / theme
    tables_folder = output / "tables" / theme

    intakes, pets = read_intakes(source)
    tables = [summarize(intakes, "Animal Type", "All animals", "animal_type")]

    for animal in ["Cat", "Dog"]:
        subset = pets[pets["Animal Type"] == animal]
        if subset.empty:
            raise ValueError(f"No {animal} records found.")

        tables.append(summarize(subset, "Age group", animal, "age", AGE_ORDER))
        tables.append(
            summarize(
                subset,
                "Sex",
                animal,
                "sex",
                ["Female", "Male", "Unknown", "Not recorded"],
            )
        )
        tables.append(
            summarize(
                subset,
                "Sterilization",
                animal,
                "sterilization",
                ["Intact", "Spayed or neutered", "Unknown", "Not recorded"],
            )
        )
        tables.append(summarize(subset, "Breed label", animal, "breed"))

    summary = pd.concat(tables, ignore_index=True)
    figures_folder.mkdir(parents=True, exist_ok=True)
    tables_folder.mkdir(parents=True, exist_ok=True)
    summary.to_csv(
        tables_folder / "intake_profile.csv",
        index=False,
        float_format="%.6f",
    )
    age_percent = plot_age_distribution(summary, figures_folder)
    plot_sex_distribution(summary, figures_folder)
    plot_breed_distribution(summary, figures_folder)

    print("Age distribution (% of each species' intake records):")
    rounded_ages = age_percent.round(1)
    print(rounded_ages.to_string())
    print(f"Three figures and the summary table saved in {output}")


if __name__ == "__main__":
    main()
