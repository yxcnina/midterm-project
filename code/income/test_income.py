import unittest

import pandas as pd

from income_composition import age_composition, group_age, species_composition
from income_intakes import (
    create_income_groups, prepare_grouped_sample, summarize_intakes,
)
from income_outcomes import coverage_table, match_outcomes, outcome_composition
from income_sample import DATA_DIR, KEYS, build_sample, select_stray_cats_dogs


class IncomeTests(unittest.TestCase):
    def test_stray_selection(self):
        """Keep Stray cats/dogs, but not surrendered cats or Stray birds."""
        data=pd.DataFrame(
            {
                "Intake Type": ["Stray", "Stray", "Owner Surrender", "Stray"],
                "Animal Type": ["Cat", "Dog", "Cat", "Bird"],
            }
        )
        selected=select_stray_cats_dogs(data)
        self.assertEqual(selected.index.tolist(), [0, 1])

    def test_tract_weights_and_ties(self):
        data=pd.DataFrame(
            {
                "tract_geoid": [str(i).zfill(11) for i in range(9)],
                "median_income": [10, 20, 30, 30, 40, 50, 60, 70, 80],
            }
        )
        groups, cuts=create_income_groups(data)
        repeated=pd.concat([data, data.iloc[[0]]] * 3, ignore_index=True)
        again, again_cuts=create_income_groups(repeated)
        pd.testing.assert_frame_equal(cuts, again_cuts)
        self.assertEqual(len(groups), len(again))
        tied=groups.loc[groups["median_income"].eq(30), "income_group"]
        self.assertEqual(tied.nunique(), 1)

    def test_conflicting_tract_income(self):
        data=pd.DataFrame(
            {"tract_geoid": ["00000000001", "00000000001"], "median_income": [10, 20]}
        )
        with self.assertRaises(ValueError):
            create_income_groups(data)

    def test_age_boundaries(self):
        cases={
            "": "Not recorded", "0 years": "Recorded as 0 years",
            "0 months": "<6 months", "5 months": "<6 months",
            "6 months": "6 to <12 months", "1 year": "1 to <3 years",
            "3 years": "3 to <7 years", "7 years": "7+ years",
        }
        for raw, expected in cases.items():
            self.assertEqual(group_age(raw), expected)
        with self.assertRaises(ValueError):
            group_age("not an age")

    def test_outcome_denominators(self):
        sample=pd.DataFrame(
            {
                "Animal ID": [f"A{i}" for i in range(6)],
                "Intake Date": ["2024-01-01"] * 6,
                "Intake Time": ["12:00:00"] * 6,
                "Intake Type": ["Stray"] * 6,
                "Age upon Intake": ["1 year"] * 6,
                "income_group": ["Low"] * 6,
                "Animal Type": ["Dog"] * 6,
            }
        )
        episodes=sample[KEYS].copy()
        episodes["Outcome_DateTime"] = [
            "2024-01-02 12:00:00", "", "2024-01-03 12:00:00",
            "2024-01-03 12:00:00", "2023-12-01 12:00:00", "2024-01-04 12:00:00",
        ]
        episodes["Outcome Type"] = [
            "Return to Owner", "", "Missing", "", "Adoption", "Rto-Adopt",
        ]
        events=match_outcomes(sample, episodes)
        self.assertEqual(int(events["usable_outcome"].sum()), 3)
        table=outcome_composition(events, ["income_group"])
        self.assertEqual(table["count"].sum(), 3)
        missing_count=table.loc[table["outcome"].eq("Missing"), "count"].iloc[0]
        self.assertEqual(int(missing_count), 1)
        rto=table.loc[table["outcome"].eq("Return to Owner")].iloc[0]
        self.assertEqual(rto["count"], 1)
        self.assertAlmostEqual(rto["percent"], 100 / 3)
        coverage=coverage_table(events, ["income_group"])
        self.assertEqual(coverage["intake_events"].iloc[0], 6)
        self.assertEqual(coverage["coverage_pct"].iloc[0], 50)

    def test_actual_sample_and_composition_totals(self):
        sample, flow, coverage=build_sample()
        grouped, tracts, _=prepare_grouped_sample()
        self.assertEqual(len(sample), len(grouped))
        self.assertEqual(flow["records"].iloc[-1], len(sample))
        self.assertEqual(coverage["analysis_intakes"].sum(), len(sample))
        self.assertTrue(sample["Intake Type"].eq("Stray").all())
        shelter=sample["Found Location"].str.contains(
            "7201 Levander", case=False, regex=False
        )
        self.assertFalse(shelter.any())
        self.assertFalse(sample.duplicated(subset=KEYS).any())
        self.assertEqual(tracts["tract_geoid"].nunique(), len(tracts))
        counts=summarize_intakes(grouped, tracts)
        self.assertEqual(counts["total_intakes"].sum(), len(sample))
        species=species_composition(grouped)
        ages=age_composition(grouped)
        self.assertEqual(species["count"].sum(), len(sample))
        self.assertEqual(ages["count"].sum(), len(sample))
        for percent in species.groupby("income_group")["percent"].sum():
            self.assertAlmostEqual(percent, 100)
        for _, subset in ages.groupby(["income_group", "animal_type"]):
            if subset["denominator"].iloc[0] > 0:
                self.assertAlmostEqual(subset["percent"].sum(), 100)

    def test_actual_outcome_coverage(self):
        sample, _, _ = prepare_grouped_sample()
        episodes=pd.read_csv(
            DATA_DIR / "aac_intake_outcomes_with_income_2024.csv",
            dtype=str, keep_default_na=False,
        )
        events = match_outcomes(sample, episodes)
        self.assertEqual(len(events), len(sample))
        coverage = coverage_table(events, ["income_group"])
        table = outcome_composition(events, ["income_group"])
        self.assertEqual(coverage["intake_events"].sum(), len(sample))
        self.assertEqual(coverage["usable_outcomes"].sum(), table["count"].sum())
        for _, subset in table.groupby("income_group", observed=True):
            if subset["denominator"].iloc[0] > 0:
                self.assertAlmostEqual(subset["percent"].sum(), 100)


if __name__ == "__main__":
    unittest.main(verbosity=2)