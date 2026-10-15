import matplotlib.pyplot as plt
import pandas as pd

from income_sample import FIGURE_DIR, SPECIES, TABLE_DIR, build_sample

GROUPS=["Low", "Middle", "High"]


def create_income_groups(sample):
    tracts=sample[["tract_geoid", "median_income"]].drop_duplicates().copy()
    if tracts["tract_geoid"].duplicated().any():
        raise ValueError("A tract has conflicting income values.")
    tracts=tracts.sort_values(["median_income", "tract_geoid"])
    tracts["income_group"], edges = pd.qcut(
        tracts["median_income"], q=3, labels=GROUPS, retbins=True
    )
    counts=tracts["income_group"].value_counts().reindex(GROUPS, fill_value=0)
    if counts.eq(0).any():
        raise ValueError("Three nonempty income groups could not be formed.")

    rows=[]
    for i, group in enumerate(GROUPS):
        selected=tracts[tracts["income_group"].eq(group)]
        rows.append(
            {
                "income_group": group,
                "tract_count": len(selected),
                "lower_cutpoint": edges[i],
                "upper_cutpoint": edges[i + 1],
                "lower_inclusive": i == 0,
                "upper_inclusive": True,
                "observed_min_income": selected["median_income"].min(),
                "observed_max_income": selected["median_income"].max(),
            }
        )
    return tracts, pd.DataFrame(rows)


def prepare_grouped_sample():
    sample, _, _ = build_sample()
    tracts, cutpoints = create_income_groups(sample)
    grouped=sample.merge(
        tracts[["tract_geoid", "income_group"]],
        on="tract_geoid", how="left", validate="many_to_one",
    )
    if len(grouped) != len(sample) or grouped["income_group"].isna().any():
        raise ValueError("Income-group assignment changed or lost events.")
    return grouped, tracts, cutpoints


def summarize_intakes(sample, tracts):
    """Return counts by income group, with Cat, Dog, total and tract counts."""
    counts=pd.crosstab(sample["income_group"], sample["Animal Type"])
    counts=counts.reindex(index=GROUPS, columns=SPECIES, fill_value=0)
    counts.columns.name = None
    counts["total_intakes"] = counts[SPECIES].sum(axis=1)
    counts["tract_count"] = (
        tracts.groupby("income_group", observed=True).size().reindex(GROUPS)
    )
    if counts["total_intakes"].sum() != len(sample):
        raise ValueError("Income-group intake counts do not add up.")
    return counts.reset_index()


def finish_figure(ax, path, note):
    figure=ax.get_figure()
    figure.text(0.01, 0.02, note, ha="left", va="bottom", fontsize=9)
    figure.tight_layout(rect=(0, 0.09, 1, 1))
    figure.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(figure)


def plot_intakes(summary):
    table=summary.set_index("income_group").reindex(GROUPS)
    ax = table[SPECIES].plot(kind="bar", figsize=(8.5, 5.5), rot=0)
    ax.set_title("AAC Stray Cat/Dog Intakes by Tract Income, 2024")
    ax.set_xlabel("Income group among tracts with eligible intake records")
    ax.set_ylabel("Intake events (not unique animals)")
    ax.set_xticklabels(
        [f"{g}\n{int(table.loc[g, 'tract_count'])} observed tracts" for g in GROUPS]
    )
    ax.legend(title="Animal type")
    ax.set_ylim(0, table[SPECIES].max().max() * 1.18)
    for bars in ax.containers:
        ax.bar_label(bars, fmt="%.0f", padding=3, fontsize=9)
    finish_figure(
        ax, FIGURE_DIR / "01_income_intake_counts.png",
        "All matched areas; Stray cats/dogs; shelter-address records excluded.\n"
        "Observed tracts only. Counts are not population-adjusted or causal effects.",
    )


def main():
    sample, tracts, cutpoints = prepare_grouped_sample()
    summary=summarize_intakes(sample, tracts)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    tracts.to_csv(TABLE_DIR / "tract_income_groups.csv", index=False)
    cutpoints.to_csv(TABLE_DIR / "income_group_cutpoints.csv", index=False)
    summary.to_csv(TABLE_DIR / "income_intake_summary.csv", index=False)
    plot_intakes(summary)
    print("\nRQ1: intake counts (not population-adjusted)")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
        