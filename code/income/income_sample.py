from pathlib import Path

import pandas as pd

PROJECT_ROOT=Path(__file__).resolve().parents[2]
DATA_DIR=PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR=PROJECT_ROOT / "artifacts" / "income"
TABLE_DIR=OUTPUT_DIR / "tables"
FIGURE_DIR=OUTPUT_DIR / "figures"
KEYS=["Animal ID", "Intake Date", "Intake Time", "Intake Type"]
SPECIES=["Cat", "Dog"]


def check_event_keys(events):
    if events[KEYS].isna().any().any() or events[KEYS].eq("").any().any():
        raise ValueError("An intake event has an empty matching key.")
    if events.duplicated(subset=KEYS).any():
        raise ValueError("Duplicate intake event keys found.")


def select_stray_cats_dogs(intakes):
    return intakes[
        intakes["Intake Type"].eq("Stray")
        & intakes["Animal Type"].isin(SPECIES)
    ].copy()


def build_sample():
    intakes=pd.read_csv(
        DATA_DIR / "aac_intakes_with_income_2024.csv",
        dtype=str,
        keep_default_na=False,
    )
    income=pd.read_csv(
        DATA_DIR / "census_tract_income_2024.csv",
        dtype=str,
        keep_default_na=False,
    )
    check_event_keys(intakes)
    dates=pd.to_datetime(intakes["Intake Date"], format="%Y-%m-%d")
    if not dates.dt.year.eq(2024).all():
        raise ValueError("The input must contain only 2024 intake events.")
    if income["tract_geoid"].duplicated().any():
        raise ValueError("Duplicate tract IDs in the income reference table.")
    if not income["tract_geoid"].str.fullmatch(r"\d{11}").all():
        raise ValueError("The income reference must use 11-digit tract IDs.")

    intakes["median_income"] = pd.to_numeric(
        intakes["median_income"], errors="coerce"
    )
    stray=select_stray_cats_dogs(intakes)
    with_tract=stray[stray["tract_geoid"].ne("")].copy()
    if not with_tract["tract_geoid"].str.fullmatch(r"\d{11}").all():
        raise ValueError("An intake record has an invalid tract ID.")
    with_income=with_tract[with_tract["income_status"].eq("numeric")].copy()
    values=with_income["median_income"]
    if (
        values.isna().any()
        or values.lt(0).any()
        or values.isin([float("inf"), float("-inf")]).any()
    ):
        raise ValueError("A numeric-income record has an invalid income value.")

    reference=income[income["income_status"].eq("numeric")].copy()
    reference["median_income"] = pd.to_numeric(reference["median_income"])
    lookup=reference.set_index("tract_geoid")["median_income"]
    expected_income=with_income["tract_geoid"].map(lookup)
    if not with_income["median_income"].eq(expected_income).all():
        raise ValueError("Merged incomes do not agree with the tract reference.")

    shelter=with_income["Found Location"].str.contains(
        "7201 Levander", case=False, na=False, regex=False
    )
    sample=with_income[~shelter].copy()
    if sample.empty:
        raise ValueError("The selected analysis sample is empty.")

    flow=pd.DataFrame(
        {
            "stage": [
                "All intake events",
                "Stray cats and dogs",
                "With Census tract",
                "With numeric income",
                "After shelter exclusion",
            ],
            "records": [
                len(intakes), len(stray), len(with_tract),
                len(with_income), len(sample),
            ],
        }
    )
    rows=[]
    for animal in SPECIES:
        original=stray[stray["Animal Type"].eq(animal)]
        selected=sample[sample["Animal Type"].eq(animal)]
        total=len(original)
        rows.append(
            {
                "animal_type": animal,
                "all_stray_intakes": total,
                "with_tract": int(with_tract["Animal Type"].eq(animal).sum()),
                "with_numeric_income": int(
                    with_income["Animal Type"].eq(animal).sum()
                ),
                "analysis_intakes": len(selected),
                "coverage_pct": len(selected) / total * 100 if total else None,
            }
        )
    return sample, flow, pd.DataFrame(rows)


def main():
    """Save aggregate sample checks and print a short completion summary."""
    sample, flow, coverage = build_sample()
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    flow.to_csv(TABLE_DIR / "sample_flow.csv", index=False)
    coverage.to_csv(TABLE_DIR / "sample_coverage_by_species.csv", index=False)
    print(flow.to_string(index=False))
    print(
        f"Sample ready: {len(sample):,} intake events; "
        f"{sample['tract_geoid'].nunique()} observed tracts.")
if __name__ == "__main__":
    main()