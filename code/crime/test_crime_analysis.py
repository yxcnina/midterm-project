"""Regression tests for the reproducible crime-analysis workflow.

Run from the repository root:
    python -m unittest discover -s code/crime -p 'test_*.py' -v

Tests create small, synthetic CSVs in a temporary directory. They never
read or modify the project's real datasets or generated research figures.
"""

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import pandas as pd

import crime_analysis


class TestCrimeAnalysis(unittest.TestCase):
    """Check district-month data integrity and reproducible output creation."""

    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        workspace = Path(self.temp.name)
        self.monthly_file = workspace / "monthly.csv"
        self.annual_file = workspace / "annual.csv"
        self.output_dir = workspace / "analysis"

        self.monthly = pd.DataFrame(
            [
                {
                    "district": district,
                    "month": month,
                    "crime_count": 90 + 11 * district + 2 * month + (district * month) % 7,
                    "stray_intake_count": 6 + 2 * district + month // 2
                    + (district + 3 * month) % 5,
                }
                for district in range(1, 11)
                for month in range(1, 13)
            ]
        )
        self.annual = self._annual_totals(self.monthly)
        self._save_inputs()

        for name, replacement in (
            ("MONTHLY_FILE", self.monthly_file),
            ("ANNUAL_FILE", self.annual_file),
            ("OUTPUT_DIR", self.output_dir),
        ):
            guard = patch.object(crime_analysis, name, replacement)
            guard.start()
            self.addCleanup(guard.stop)

    @staticmethod
    def _annual_totals(monthly):
        return monthly.groupby("district", as_index=False)[
            ["crime_count", "stray_intake_count"]
        ].sum()

    def _save_inputs(self):
        self.monthly.to_csv(self.monthly_file, index=False)
        self.annual.to_csv(self.annual_file, index=False)

    def test_valid_120_row_panel(self):
        monthly, annual = crime_analysis.load_and_validate()
        self.assertEqual(len(monthly), 120)
        self.assertEqual(len(annual), 10)
        self.assertEqual(int(monthly["crime_count"].sum()),
                         int(annual["crime_count"].sum()))

    def test_missing_district_month_is_rejected(self):
        self.monthly = self.monthly.iloc[:-1].copy()
        self._save_inputs()
        with self.assertRaisesRegex(ValueError, "10 districts x all 12 months"):
            crime_analysis.load_and_validate()

    def test_duplicate_district_month_is_rejected(self):
        self.monthly = pd.concat(
            [self.monthly, self.monthly.iloc[[0]]], ignore_index=True
        )
        self._save_inputs()
        with self.assertRaisesRegex(ValueError, "Repeated geography/month"):
            crime_analysis.load_and_validate()

    def test_negative_counts_are_rejected(self):
        self.monthly.loc[0, "crime_count"] = -1
        self._save_inputs()
        with self.assertRaisesRegex(ValueError, "Counts cannot be negative"):
            crime_analysis.load_and_validate()

    def test_missing_values_are_rejected(self):
        self.monthly.loc[0, "crime_count"] = float("nan")
        self._save_inputs()
        with self.assertRaisesRegex(ValueError, "missing values"):
            crime_analysis.load_and_validate()

    def test_annual_monthly_mismatch_is_rejected(self):
        self.annual.loc[0, "stray_intake_count"] += 1
        self._save_inputs()
        with self.assertRaisesRegex(ValueError, "Annual totals disagree"):
            crime_analysis.load_and_validate()

    def test_missing_input_file_is_rejected(self):
        self.monthly_file.unlink()
        with self.assertRaises(FileNotFoundError):
            crime_analysis.load_and_validate()

    def test_full_workflow_produces_all_six_outputs(self):
        with redirect_stdout(StringIO()):
            crime_analysis.main()
        expected = {
            "annual_district_scatter.png",
            "monthly_daily_averages.png",
            "adjusted_within_district_month.png",
            "crime_monthly_summary.csv",
            "crime_analysis_statistics.csv",
            "crime_regression_results.csv",
        }
        self.assertEqual({p.name for p in self.output_dir.iterdir()}, expected)
        stats = pd.read_csv(self.output_dir / "crime_analysis_statistics.csv")
        models = pd.read_csv(self.output_dir / "crime_regression_results.csv")
        self.assertEqual(len(stats), 4)
        self.assertEqual(len(models), 3)


if __name__ == "__main__":
    unittest.main()
