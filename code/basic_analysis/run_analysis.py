"""Check inputs, then run all six Basic Analysis themes."""

import argparse
import importlib.util
from pathlib import Path
import subprocess
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REQUIRED_COLUMNS = {
    "aac_intakes_clean.csv": {
        "Animal ID", "Intake Date", "Intake Time", "Intake Type",
        "Animal Type", "Age upon Intake", "Sex upon Intake", "Breed",
        "Intake Condition", "Found Location",
    },
    "aac_outcomes_clean.csv": {
        "Outcome Date", "Animal Type", "Age upon Outcome", "Sex upon Outcome",
        "Breed", "Color", "Outcome Type",
    },
    "aac_intakes_clean_geocoded.csv": {
        "Animal ID", "Intake Date", "Intake Time", "Intake Type",
        "Animal Type", "Found Location", "longitude", "latitude",
        "location_precision",
    },
}

SCRIPTS = [
    "01_intake_profile.py",
    "02_intake_timing.py",
    "03_intake_context.py",
    "04_outcome_profile.py",
    "05_trait_comparisons.py",
    "06_intake_locations.py",
]


def load_theme(filename):
    """Load a numbered theme without executing its main function."""
    folder = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location(Path(filename).stem, folder / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_inputs(data_folder):
    """Check required inputs using the themes' readers, without saving outputs."""
    data_folder = Path(data_folder)
    for filename, required in REQUIRED_COLUMNS.items():
        source = data_folder / filename
        if not source.is_file():
            raise ValueError(f"Missing input file: {source}")
        columns = pd.read_csv(source, nrows=0).columns
        missing = sorted(required - set(columns))
        if missing:
            raise ValueError(f"{filename} is missing columns: {', '.join(missing)}")

    # Reuse the same parsing and validation as the individual themes.
    for filename in SCRIPTS[:5]:
        theme = load_theme(filename)
        if hasattr(theme, "read_intakes"):
            source = data_folder / "aac_intakes_clean.csv"
            reader = theme.read_intakes
        else:
            source = data_folder / "aac_outcomes_clean.csv"
            reader = theme.read_outcomes
        try:
            pets = reader(source)
            if filename == "04_outcome_profile.py":
                theme.summarize_outcomes(pets)
            elif filename == "05_trait_comparisons.py":
                theme.summarize_traits(pets)
        except (ValueError, KeyError) as error:
            raise ValueError(f"{source.name} ({filename}): {error}") from error

    locations_theme = load_theme("06_intake_locations.py")
    intakes, locations = locations_theme.read_intakes(data_folder)
    locations_theme.shelter_coordinates(locations)
    for animal in locations_theme.ANIMALS:
        mapped = locations.loc[locations["Animal Type"].eq(animal)]
        if mapped.loc[~locations_theme.shelter_address_mask(mapped)].empty:
            raise ValueError(f"The maps need {animal} records away from the shelter.")
    return {
        "intake_records": len(intakes),
        "outcome_records": len(pd.read_csv(data_folder / "aac_outcomes_clean.csv")),
        "geocoded_records": len(locations),
    }


def main(argv=None):
    """Validate all inputs, optionally stop, or run the themes in order."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-only", action="store_true",
        help="Validate the three input CSVs without writing figures or tables.",
    )
    args = parser.parse_args(argv)
    try:
        counts = check_inputs(PROJECT_ROOT / "data" / "processed")
    except (OSError, ValueError, KeyError) as error:
        print(f"Input check failed: {error}", file=sys.stderr)
        return 1
    print(
        f"Input checks passed: {counts['intake_records']:,} intake records, "
        f"{counts['outcome_records']:,} outcome records, "
        f"{counts['geocoded_records']:,} geocoded records.", flush=True,
    )
    if args.check_only:
        return 0

    folder = Path(__file__).resolve().parent
    for number, filename in enumerate(SCRIPTS, start=1):
        print(f"\n[{number}/{len(SCRIPTS)}] Running {filename}", flush=True)
        try:
            subprocess.run(
                [sys.executable, str(folder / filename)],
                cwd=PROJECT_ROOT,
                check=True,
            )
        except subprocess.CalledProcessError as error:
            print(
                f"Stopped because {filename} failed. "
                "Check its error above before rerunning the analysis.",
                file=sys.stderr,
            )
            return error.returncode

    print("\nFinished: 14 figures and 12 tables in artifacts/basic_analysis/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
