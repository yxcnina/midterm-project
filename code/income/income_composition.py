import pandas as pd

from income_intakes import GROUPS, finish_figure, prepare_grouped_sample
from income_sample import FIGURE_DIR, SPECIES, TABLE_DIR

AGE_ORDER=[
    "<6 months", "6 to <12 months", "1 to <3 years", "3 to <7 years",
    "7+ years", "Recorded as 0 years", "Not recorded",
]


def group_age(age):
    if pd.isna(age) or str(age).strip() == "":
        return "Not recorded"

    text=str(age).strip().lower()
    parts=text.split()

    if len(parts) != 2:
        raise ValueError(f"Unexpected intake age: {age!r}")

    number=float(parts[0])
    unit=parts[1].rstrip("s")

    months_per_unit = {
        "year": 12,
        "month": 1,
        "week": 84 / 365.25,
        "day": 12 / 365.25,
    }

    if unit not in months_per_unit or not 0 <= number < float("inf"):
        raise ValueError(f"Unexpected intake age: {age!r}")

    if unit=="year" and number == 0:
        return "Recorded as 0 years"

    months=number * months_per_unit[unit]

    if months < 6:
        return "<6 months"
    if months < 12:
        return "6 to <12 months"
    if months < 36:
        return "1 to <3 years"
    if months < 84:
        return "3 to <7 years"

    return "7+ years"


def species_composition(sample):
    rows=[]
    for group in GROUPS:
        subset=sample[sample["income_group"].eq(group)]
        for animal in SPECIES:
            count=int(subset["Animal Type"].eq(animal).sum())
            rows.append(
                {
                    "income_group": group, "animal_type": animal,
                    "count": count, "denominator": len(subset),
                    "percent": count / len(subset) * 100 if len(subset) else None,
                }
            )
    table=pd.DataFrame(rows)
    if table["count"].sum() != len(sample):
        raise ValueError("Species counts do not add up to the analysis sample.")
    return table


def age_composition(sample):
    prepared=sample.copy()
    prepared["age_group"] = prepared["Age upon Intake"].apply(group_age)
    rows=[]
    for group in GROUPS:
        for animal in SPECIES:
            subset=prepared[
                prepared["income_group"].eq(group)
                & prepared["Animal Type"].eq(animal)
            ]
            for age in AGE_ORDER:
                count=int(subset["age_group"].eq(age).sum())
                rows.append(
                    {
                        "income_group": group, "animal_type": animal,
                        "age_group": age, "count": count,
                        "denominator": len(subset),
                        "percent": count / len(subset) * 100 if len(subset) else None,
                    }
                )
    table=pd.DataFrame(rows)
    if table["count"].sum() != len(sample):
        raise ValueError("Age counts do not add up to the analysis sample.")
    return table


def plot_species(table):
    values=table.pivot(index="income_group", columns="animal_type", values="percent")
    values=values.reindex(index=GROUPS, columns=SPECIES)
    totals=table.groupby("income_group")["count"].sum()
    ax=values.plot(kind="bar", stacked=True, figsize=(8.5, 5.5), rot=0)
    ax.set_title("Species Composition of AAC Stray Intakes, 2024")
    ax.set_xlabel("Income group")
    ax.set_ylabel("Share of eligible intake events (%)")
    ax.set_ylim(0, 100)
    ax.set_xticklabels([f"{g}\nn={totals[g]:,}" for g in GROUPS])
    ax.legend(title="Animal type", bbox_to_anchor=(1.02, 1), loc="upper left")
    for bars in ax.containers:
        ax.bar_label(bars, fmt="%.1f%%", label_type="center", fontsize=10)
    finish_figure(
        ax, FIGURE_DIR / "02_income_species_composition.png",
        "Denominator: all eligible Stray cat/dog intakes in each income group.\n"
        "An outcome record is not required. "
        "The same tract income groups are used throughout.",
    )


def plot_ages(table):
    for animal in SPECIES:
        subset=table[table["animal_type"].eq(animal)]
        values=subset.pivot(
            index="income_group", columns="age_group", values="percent"
        )
        values=values.reindex(index=GROUPS, columns=AGE_ORDER)
        values=values.loc[:, values.fillna(0).sum().gt(0)]
        totals=subset.groupby("income_group")["count"].sum()
        ax=values.plot(kind="bar", stacked=True, figsize=(10, 5.8), rot=0)
        ax.set_title(f"Age Composition of Stray {animal} Intakes, 2024")
        ax.set_xlabel("Income group")
        ax.set_ylabel(f"Share of eligible {animal.lower()} intake events (%)")
        ax.set_ylim(0, 100)
        ax.set_xticklabels([f"{g}\nn={totals[g]:,}" for g in GROUPS])
        ax.legend(
            title="Recorded intake age", bbox_to_anchor=(1.02, 1), loc="upper left"
        )
        finish_figure(
            ax, FIGURE_DIR / f"a1_income_age_{animal.lower()}.png",
            f"Denominator: all eligible {animal.lower()} intakes in each income group, "
            "including unknown age.\n"
            "'0 years' is kept separate, not treated as newborn; "
            "zero-count categories remain in the CSV.",
        )


def main():
    sample, _, _ = prepare_grouped_sample()
    species=species_composition(sample)
    ages=age_composition(sample)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    species.to_csv(TABLE_DIR / "income_species_composition.csv", index=False)
    ages.to_csv(TABLE_DIR / "income_age_composition.csv", index=False)
    plot_species(species)
    plot_ages(ages)
    print("\nRQ2: within-group species percentages")
    print(species.round(2).to_string(index=False))
    print("Age composition tables and separate Cat/Dog charts saved.")


if __name__ == "__main__":
    main()
