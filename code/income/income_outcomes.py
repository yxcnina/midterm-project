import pandas as pd

from income_composition import group_age
from income_intakes import GROUPS, finish_figure, prepare_grouped_sample
from income_sample import (
    DATA_DIR, FIGURE_DIR, KEYS, SPECIES, TABLE_DIR, check_event_keys,
)

OUTCOME_ORDER=[
    "Adoption", "Return to Owner", "Transfer", "Rto-Adopt",
    "Euthanasia", "Died", "Disposal", "Missing", "Lost",
]
PLOT_ORDER=["Adoption", "Return to Owner", "Transfer", "Rto-Adopt", "Other recorded"]
STATUS_ORDER=[
    "usable", "no_episode_row", "no_recorded_outcome_time",
    "invalid_outcome_time", "outcome_before_intake", "outside_2024_window",
    "missing_outcome_type",
]


def match_outcomes(sample, episodes):
    check_event_keys(sample)
    check_event_keys(episodes)
    matched=sample.merge(
        episodes[KEYS + ["Outcome_DateTime", "Outcome Type"]],
        on=KEYS, how="left", validate="one_to_one", indicator=True,
    )
    if len(matched) != len(sample):
        raise ValueError("Outcome matching changed the intake sample size.")
    matched["Outcome Type"] = matched["Outcome Type"].fillna("").str.strip()
    raw_time=matched["Outcome_DateTime"].fillna("").str.strip()
    outcome_time=pd.to_datetime(
        raw_time, format="%Y-%m-%d %H:%M:%S", errors="coerce"
    )
    intake_time=pd.to_datetime(
        matched["Intake Date"] + " " + matched["Intake Time"],
        format="%Y-%m-%d %H:%M:%S",
    )
    matched["episode_row_matched"] = matched["_merge"].eq("both")
    matched["has_outcome_time"] = outcome_time.notna()
    status=pd.Series("usable", index=matched.index)
    status.loc[matched["Outcome Type"].eq("")] = "missing_outcome_type"
    status.loc[outcome_time.ge(pd.Timestamp("2025-01-01"))] = "outside_2024_window"
    status.loc[outcome_time.lt(intake_time)] = "outcome_before_intake"
    status.loc[outcome_time.isna() & raw_time.ne("")] = "invalid_outcome_time"
    status.loc[raw_time.eq("")] = "no_recorded_outcome_time"
    status.loc[~matched["episode_row_matched"]] = "no_episode_row"
    matched["outcome_status"]=status
    matched["usable_outcome"]=status.eq("usable")
    matched["intake_month"]=matched["Intake Date"].str[:7]
    matched["age_group"]=matched["Age upon Intake"].apply(group_age)
    return matched.drop(columns="_merge")


def group_subsets(events, columns):
    by=columns[0] if len(columns) == 1 else columns
    for labels, subset in events.groupby(by, observed=True, sort=True):
        if len(columns)==1:
            labels=(labels,)
        yield dict(zip(columns, labels)), subset


def coverage_table(events, columns):
    rows = []
    for labels, subset in group_subsets(events, columns):
        usable=int(subset["usable_outcome"].sum())
        row=dict(labels)
        row.update(
            {
                "intake_events": len(subset),
                "episode_rows_matched": int(subset["episode_row_matched"].sum()),
                "with_outcome_time": int(subset["has_outcome_time"].sum()),
                "usable_outcomes": usable,
                "coverage_pct": usable / len(subset) * 100,
            }
        )
        for status in STATUS_ORDER:
            row[f"status_{status}"]=int(subset["outcome_status"].eq(status).sum())
        if sum(row[f"status_{s}"] for s in STATUS_ORDER) != len(subset):
            raise ValueError("Outcome-status counts do not add up.")
        rows.append(row)
    return pd.DataFrame(rows)


def outcome_composition(events, columns, category="Outcome Type", order=None):
    usable=events[events["usable_outcome"]]
    categories=list(order or OUTCOME_ORDER)
    extras=sorted(set(usable[category]) - set(categories))
    categories += extras
    rows=[]
    for labels, subset in group_subsets(events, columns):
        valid = subset[subset["usable_outcome"]]
        counts = valid[category].value_counts()
        for outcome in categories:
            count = int(counts.get(outcome, 0))
            row = dict(labels)
            row.update(
                {
                    "outcome": outcome, "count": count,
                    "denominator": len(valid),
                    "percent": count / len(valid) * 100 if len(valid) else None,
                }
            )
            rows.append(row)
    table=pd.DataFrame(rows)
    if table["count"].sum() != len(usable):
        raise ValueError("Outcome counts do not add up to usable outcomes.")
    return table


def plot_outcome_composition(table):
    values=table.pivot(index="income_group", columns="outcome", values="percent")
    values=values.reindex(index=GROUPS, columns=PLOT_ORDER)
    totals=table.groupby("income_group", observed=True)["count"].sum()
    ax = values.plot(kind="bar", stacked=True, figsize=(10, 5.8), rot=0)
    ax.set_title("Recorded Outcomes of AAC Stray Cat/Dog Intakes, 2024")
    ax.set_xlabel("Income group")
    ax.set_ylabel("Share of usable matched outcomes (%)")
    ax.set_ylim(0, 100)
    ax.set_xticklabels([f"{g}\nn={totals[g]:,} outcomes" for g in GROUPS])
    ax.legend(title="Recorded outcome", bbox_to_anchor=(1.02, 1), loc="upper left")
    finish_figure(
        ax, FIGURE_DIR / "03_income_recorded_outcomes.png",
        "Denominator: matched events with a usable 2024 outcome time "
        "and category, not all intakes.\n"
        "Other recorded = remaining explicit categories; "
        "unpaired events are excluded, not failures.",
    )


def plot_rto(rto):
    values=rto.pivot(index="income_group", columns="Animal Type", values="percent")
    values=values.reindex(index=GROUPS, columns=SPECIES)
    denominators=rto.pivot(
        index="income_group", columns="Animal Type", values="denominator"
    ).reindex(index=GROUPS, columns=SPECIES)
    ax = values.plot(kind="bar", figsize=(8.5, 5.6), rot=0)
    ax.set_title("Return-to-Owner Share by Income and Species, 2024")
    ax.set_xlabel("Income group")
    ax.set_ylabel("RTO among usable matched outcomes (%)")
    ax.set_ylim(0, max(5, values.max().max() * 1.5))
    ax.legend(title="Animal type")
    for animal, bars in zip(SPECIES, ax.containers):
        labels=[]
        for group in GROUPS:
            percent=values.loc[group, animal]
            n=denominators.loc[group, animal]
            label=f"{percent:.1f}%\nn={int(n):,}" if pd.notna(percent) else "n=0"
            labels.append(label)
        ax.bar_label(bars, labels=labels, padding=3, fontsize=9)
    finish_figure(
        ax, FIGURE_DIR / "04_income_rto_by_species.png",
        "n = usable matched outcomes within each income group and species.\n"
        "Return to Owner only; Rto-Adopt is separate. "
        "These are not final RTO probabilities.",
    )


def main():
    sample, _, _ = prepare_grouped_sample()
    episodes = pd.read_csv(
        DATA_DIR / "aac_intake_outcomes_with_income_2024.csv",
        dtype=str, keep_default_na=False,
    )
    events=match_outcomes(sample, episodes)
    if not events["usable_outcome"].any():
        raise ValueError("No usable outcomes were found; check the input episodes.")
    coverage=coverage_table(events, ["income_group"])
    by_species=coverage_table(events, ["income_group", "Animal Type"])
    by_month=coverage_table(events, ["income_group", "intake_month"])
    composition=outcome_composition(events, ["income_group"])
    species=outcome_composition(events, ["income_group", "Animal Type"])
    age=outcome_composition(events, ["income_group", "Animal Type", "age_group"])
    events["plot_outcome"] = events["Outcome Type"].where(
        events["Outcome Type"].isin(PLOT_ORDER[:-1]), "Other recorded"
    )
    plot_table=outcome_composition(
        events, ["income_group"], category="plot_outcome", order=PLOT_ORDER
    )
    rto=species[species["outcome"].eq("Return to Owner")].copy()
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    tables={
        "income_outcome_coverage.csv": coverage,
        "income_outcome_coverage_by_species.csv": by_species,
        "income_outcome_coverage_by_month.csv": by_month,
        "income_outcome_composition.csv": composition,
        "income_outcomes_by_species.csv": species,
        "income_outcomes_by_species_age.csv": age,
        "income_outcome_plot_summary.csv": plot_table,
        "income_rto_by_species.csv": rto,
    }
    for filename, table in tables.items():
        table.to_csv(TABLE_DIR / filename, index=False)
    plot_outcome_composition(plot_table)
    plot_rto(rto)
    print("\nRQ3: recorded outcome coverage")
    shown=coverage[
        ["income_group", "intake_events", "usable_outcomes", "coverage_pct"]
    ]
    print(shown.round(2).to_string(index=False))
    print("\nRTO among usable outcomes (not among all intakes)")
    print(rto.round(2).to_string(index=False))


if __name__ == "__main__":
    main()