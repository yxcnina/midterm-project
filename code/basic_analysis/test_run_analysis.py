"""Check that invalid inputs stop Basic Analysis before any theme runs."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

import run_analysis as runner


class InputCheckTests(unittest.TestCase):
    """Use small event tables and leave the repository data untouched."""

    def setUp(self):
        """Create valid inputs with repeated animal IDs but distinct events."""
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.project = Path(self.temporary.name)
        self.data = self.project / "data" / "processed"
        self.data.mkdir(parents=True)
        self.intakes = pd.DataFrame([
            {
                "Animal ID": "A01" if i != 1 else "A02",
                "Intake Date": "2024-01-02", "Intake Time": f"0{i}:00:00",
                "Intake Type": "Stray", "Animal Type": animal,
                "Age upon Intake": "2 years", "Sex upon Intake": "Unknown",
                "Breed": "Mix", "Intake Condition": "Normal",
                "Found Location": location,
            }
            for i, (animal, location) in enumerate([
                ("Cat", "123 Main St in Austin (TX)"),
                ("Dog", "456 Main St in Austin (TX)"),
                ("Cat", "7201 Levander Loop in Austin (TX)"),
            ])
        ])
        self.outcomes = pd.DataFrame([
            {
                "Animal ID": "A01", "Outcome Date": "2024-01-03",
                "Animal Type": animal, "Age upon Outcome": "2 years",
                "Sex upon Outcome": "Unknown", "Breed": "Mix",
                "Color": "Black", "Outcome Type": outcome,
            }
            for animal, outcome in [("Cat", ""), ("Dog", "Adoption")]
        ])
        self.locations = self.intakes.assign(
            longitude=-97.7, latitude=30.3, location_precision="street_address_interpolated"
        )
        self.write_inputs()
        self.output = self.project / "artifacts" / "basic_analysis" / "existing.csv"
        self.output.parent.mkdir(parents=True)
        self.output.write_bytes(b"previous results\n")

    def write_inputs(self):
        """Restore the three CSV fixtures for each independent failure case."""
        for name, frame in [
            ("aac_intakes_clean.csv", self.intakes),
            ("aac_outcomes_clean.csv", self.outcomes),
            ("aac_intakes_clean_geocoded.csv", self.locations),
        ]:
            frame.to_csv(self.data / name, index=False)

    def run_cli(self, arguments):
        """Run the entry point against fixtures and capture launches and errors."""
        error = StringIO()
        with patch.object(runner, "PROJECT_ROOT", self.project), \
                patch.object(runner.subprocess, "run") as launch, \
                redirect_stdout(StringIO()), redirect_stderr(error):
            result = runner.main(arguments)
        return result, launch, error.getvalue()

    def assert_stops(self, expected_message):
        """Verify rejection happens before launching or replacing any result."""
        result, launch, error = self.run_cli([])
        self.assertEqual(result, 1)
        launch.assert_not_called()
        self.assertIn(expected_message, error)
        self.assertEqual(self.output.read_bytes(), b"previous results\n")

    def test_check_only_preserves_files_and_counts_events(self):
        """Repeated IDs and blank outcomes remain valid event-level inputs."""
        before = {p: p.read_bytes() for p in self.project.rglob("*") if p.is_file()}
        counts = runner.check_inputs(self.data)
        self.assertEqual(counts, {
            "intake_records": 3, "outcome_records": 2, "geocoded_records": 3,
        })
        result, launch, error = self.run_cli(["--check-only"])
        self.assertEqual((result, error), (0, ""))
        launch.assert_not_called()
        after = {p: p.read_bytes() for p in self.project.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_missing_files_and_columns_stop_before_first_theme(self):
        """Even a missing late-theme input must stop all output generation."""
        for filename in runner.REQUIRED_COLUMNS:
            with self.subTest(filename=filename):
                path = self.data / filename
                path.unlink()
                self.assert_stops(f"Missing input file: {path}")
                self.write_inputs()
                frame = pd.read_csv(path).drop(columns=["Animal Type"])
                frame.to_csv(path, index=False)
                self.assert_stops(f"{filename} is missing columns: Animal Type")
                self.write_inputs()

    def test_dates_and_species_are_checked_in_both_full_tables(self):
        """Reject wrong years, unparseable dates, and missing cat/dog groups."""
        for filename, date_column in [
            ("aac_intakes_clean.csv", "Intake Date"),
            ("aac_outcomes_clean.csv", "Outcome Date"),
        ]:
            for value in ["2023-01-02", "not a date", ""]:
                with self.subTest(filename=filename, date=value):
                    path = self.data / filename
                    frame = pd.read_csv(path, keep_default_na=False)
                    frame.loc[0, date_column] = value
                    frame.to_csv(path, index=False)
                    self.assert_stops(filename)
                    self.write_inputs()
            path = self.data / filename
            frame = pd.read_csv(path, keep_default_na=False)
            frame.loc[:, "Animal Type"] = "Cat"
            frame.to_csv(path, index=False)
            self.assert_stops(filename)
            self.write_inputs()

    def test_geocoded_events_must_match_the_full_table(self):
        """Reject duplicate, absent, conflicting, and invalid-coordinate events."""
        path = self.data / "aac_intakes_clean_geocoded.csv"
        cases = [
            ("Animal ID", "missing", "absent from the full intake file"),
            ("Found Location", "different address", "disagree on Found Location"),
            ("latitude", "91", "invalid coordinates"),
            ("longitude", "nan", "Unable to parse"),
        ]
        for column, value, message in cases:
            with self.subTest(column=column):
                frame = self.locations.astype(str).copy()
                frame.loc[0, column] = value
                frame.to_csv(path, index=False)
                self.assert_stops(message)
                self.write_inputs()
        for filename in ["aac_intakes_clean.csv", path.name]:
            source = self.data / filename
            frame = pd.read_csv(source, keep_default_na=False)
            pd.concat([frame, frame.iloc[[0]]]).to_csv(source, index=False)
            self.assert_stops("event keys must be unique")
            self.write_inputs()

    def test_missing_shelter_reference_stops_before_writing(self):
        """The map reference is checked without saving the coverage tables."""
        self.locations.iloc[:2].to_csv(
            self.data / "aac_intakes_clean_geocoded.csv", index=False
        )
        self.assert_stops("shelter reference geocode")

    def test_maps_need_both_species_away_from_the_shelter(self):
        """A valid geocoded subset can still be too small for the paired maps."""
        self.locations.loc[self.locations["Animal Type"].eq("Cat")].to_csv(
            self.data / "aac_intakes_clean_geocoded.csv", index=False
        )
        self.assert_stops("maps need Dog records away from the shelter")

    def test_runner_stops_after_a_theme_failure(self):
        """A failed subprocess must prevent every later theme from running."""
        with patch.object(runner, "PROJECT_ROOT", self.project), \
                patch.object(runner.subprocess, "run") as launch, \
                redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            launch.side_effect = [None, subprocess.CalledProcessError(7, "theme")]
            self.assertEqual(runner.main([]), 7)
        self.assertEqual(launch.call_count, 2)
        for call in launch.call_args_list:
            self.assertEqual(call.args[0][0], runner.sys.executable)
            self.assertTrue(call.kwargs["check"])


if __name__ == "__main__":
    unittest.main()
