"""Add three geocoding columns to accepted 2024 AAC intake event rows.

Run from the repository root:
    python src/geocode_aac_intakes.py --offline

The main CSV contains the original columns plus latitude, longitude,
and location_precision. Only accepted address/intersection
points are exported. Match details are saved separately for review.
AI-assisted implementation; see docs/geocoding.md for sources and limitations.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import pandas as pd

from aac_geocoder import (
    MIN_SCORE,
    SERVICE,
    classify,
    geocode_locations,
    split_location,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "aac_intakes_clean.csv"
OUTPUT_PATH = (
    PROJECT_ROOT / "data" / "processed" / "aac_intakes_clean_geocoded.csv"
)
CACHE_DIR = PROJECT_ROOT / "data" / "reference" / "geocoding"
SUMMARY_PATH = PROJECT_ROOT / "reports" / "geocoding" / "summary.json"
AUDIT_PATH = PROJECT_ROOT / "reports" / "geocoding" / "match_audit.csv"

GEO_FIELDS = [
    "latitude",
    "longitude",
    "location_precision",
]
AUDIT_FIELDS = [
    "input_row_id",
    *GEO_FIELDS,
    "geocode_status",
    "geocode_score",
    "geocode_address_type",
    "geocode_match_address",
    "geocode_query",
    "input_city",
    "matched_city",
    "city_label_differs",
    "coordinate_source",
    "geocode_retrieved_at_utc",
    "point_interpretation",
]


def file_sha256(path):
    """Return the SHA-256 string for the contents of a supplied file path."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative_label(path):
    """Return a portable repository path, or the name of an external file."""
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.name


def build_location_lookup(locations, cache_dir, offline=False):
    """Return accepted point metadata keyed by unique input location strings.

    locations supplies reported locations; cache_dir supplies saved responses.
    offline=True requires cached address responses and prevents network access.
    Parks and other locations without an accepted point are omitted.
    """
    unique_locations = sorted(set(locations))
    results = geocode_locations(
        unique_locations, base=cache_dir, offline=offline
    )
    locator_path = cache_dir / "geocoder_cache.json"
    if locator_path.exists():
        cache = json.loads(locator_path.read_text(encoding="utf-8"))
    else:
        cache = {}

    accepted = {}
    for location in unique_locations:
        result = results[location]
        if not result["is_location_valid"]:
            continue

        # Export review metadata for accepted points only, without failure reasons.
        record = {key: result.get(key, "") for key in AUDIT_FIELDS}
        record["point_interpretation"] = (
            "geocoded_reported_address_not_observed_gps"
        )
        input_city = split_location(location)[1]
        attributes = (
            cache.get(location, {})
            .get("response", {})
            .get("attributes", {})
        )
        matched_city = str(attributes.get("City", "") or "")
        record["input_city"] = input_city
        record["matched_city"] = matched_city
        if (
            input_city
            and matched_city
            and input_city.casefold() not in {"travis", "travis county"}
        ):
            record["city_label_differs"] = (
                input_city.casefold() != matched_city.casefold()
            )
        accepted[location] = record
    return accepted


def run(
    input_path,
    output_path,
    cache_dir,
    summary_path,
    offline=False,
    audit_path=None,
):
    """Read cleaned 2024 events, save point outputs, and return count metadata.

    Path arguments select the input, main CSV, address cache, and JSON summary.
    audit_path selects the review CSV; its default is beside summary_path.
    offline=True permits cached responses only. The input file is not modified.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    cache_dir = Path(cache_dir)
    summary_path = Path(summary_path)
    audit_path = (
        Path(audit_path)
        if audit_path is not None
        else summary_path.parent / "match_audit.csv"
    )
    destinations = [output_path, audit_path, summary_path]
    temporary_paths = [
        path.with_suffix(path.suffix + ".tmp") for path in destinations
    ]
    # Include staged paths so a custom filename cannot overwrite the input.
    all_paths = [input_path, *destinations, *temporary_paths]
    if len({path.resolve() for path in all_paths}) != len(all_paths):
        raise ValueError(
            "Input, output, audit, summary, and temporary paths must differ."
        )

    input_hash = file_sha256(input_path)
    # Strings preserve the original IDs, dates, category labels, and blanks.
    intakes = pd.read_csv(input_path, dtype=str, keep_default_na=False)
    required = {"Animal ID", "Found Location"}
    missing = required - set(intakes.columns)
    if missing:
        raise ValueError(f"Input is missing columns: {sorted(missing)}")
    if set(AUDIT_FIELDS) & set(intakes.columns):
        raise ValueError(
            "Use the original cleaned input, not an already geocoded output."
        )
    # Validate the split timestamp without changing the teammate's columns.
    if {"Intake Date", "Intake Time"}.issubset(intakes.columns):
        date_columns = ["Intake Date", "Intake Time"]
        dates = pd.to_datetime(
            intakes["Intake Date"] + " " + intakes["Intake Time"],
            format="%Y-%m-%d %H:%M:%S",
            errors="raise",
        )
    elif "DateTime" in intakes.columns:
        date_columns = ["DateTime"]
        dates = pd.to_datetime(intakes["DateTime"], errors="raise")
    else:
        raise ValueError(
            "Input needs Intake Date and Intake Time, or a DateTime column."
        )
    within_year = (
        (dates >= pd.Timestamp("2024-01-01"))
        & (dates < pd.Timestamp("2025-01-01"))
    )
    if not within_year.all():
        raise ValueError(
            "The input must contain only 2024 intake records with valid dates."
        )

    locations = intakes["Found Location"].str.strip()
    accepted = build_location_lookup(
        locations.tolist(), cache_dir, offline=offline
    )
    records = []
    for row_number, original in enumerate(
        intakes.to_dict(orient="records"), start=1
    ):
        location = original["Found Location"].strip()
        if location in accepted:
            # Repeated locations remain separate intake events in input order.
            records.append(
                {**original, **accepted[location], "input_row_id": row_number}
            )
    original_columns = list(intakes.columns)
    output_columns = [*original_columns, *GEO_FIELDS]
    audit_columns = [*original_columns, *AUDIT_FIELDS]
    output = pd.DataFrame(records, columns=output_columns)
    audit = pd.DataFrame(records, columns=audit_columns)

    candidates = sum(
        classify(value)[0] in {"numbered_address", "intersection"}
        for value in set(locations)
    )
    precision_counts = Counter(
        record["location_precision"] for record in records
    )
    locator_path = cache_dir / "geocoder_cache.json"
    cache_files = (
        {relative_label(locator_path): file_sha256(locator_path)}
        if locator_path.exists()
        else {}
    )
    summary = {
        "input_file": relative_label(input_path),
        "input_sha256": input_hash,
        "output_file": relative_label(output_path),
        "audit_file": relative_label(audit_path),
        "original_columns": original_columns,
        "input_datetime_columns": date_columns,
        "added_output_columns": GEO_FIELDS,
        "output_columns": output_columns,
        "audit_columns": audit_columns,
        "total_records": len(intakes),
        "unique_location_strings": intakes["Found Location"].nunique(),
        "unique_locations_after_trimming": locations.nunique(),
        "unique_address_intersection_candidates": candidates,
        "successfully_located_records": len(output),
        "unsuccessfully_located_records": len(intakes) - len(output),
        "point_records": len(output),
        "bounding_box_records": 0,
        "successfully_located_unique_locations": len(accepted),
        "precision_counts": dict(sorted(precision_counts.items())),
        "city_label_difference_records": sum(
            record["city_label_differs"] is True for record in records
        ),
        "coordinate_system": "WGS84 / EPSG:4326",
        "minimum_locator_score": MIN_SCORE,
        "locator_service": SERVICE,
        "cache_files": cache_files,
        "notes": [
            "Counts refer to cleaned intake event rows, not distinct animals.",
            "Successful means an accepted address/intersection point.",
            "Geocoded addresses are not verified animal GPS observations.",
            "Park ranges and all other records without accepted points "
            "are excluded from both exported CSV files.",
            "The main CSV adds only latitude, longitude, and "
            "location_precision to the unchanged original columns.",
            "Match details are in the audit CSV, with the same accepted "
            "event rows in the same order as the main CSV.",
            "No rejected-row file or rejection-reason column is produced.",
            "Audit input_row_id is a one-based row in this exact input "
            "snapshot, not an official permanent ID.",
            "City-label differences are review flags, not proof of error; "
            "assign communities from coordinates and chosen boundaries.",
            "Locator responses do not reconstruct historical 2024 geography.",
        ],
    }

    # Finish writing every staged file before replacing any published result.
    for destination in destinations:
        destination.parent.mkdir(parents=True, exist_ok=True)
    output_temporary, audit_temporary, summary_temporary = temporary_paths
    try:
        for frame, temporary in (
            (output, output_temporary),
            (audit, audit_temporary),
        ):
            frame.to_csv(
                temporary,
                index=False,
                encoding="utf-8-sig",
                lineterminator="\n",
            )
        summary["output_sha256"] = file_sha256(output_temporary)
        summary["audit_sha256"] = file_sha256(audit_temporary)
        summary_temporary.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        if file_sha256(input_path) != input_hash:
            raise RuntimeError(
                "Input changed during this run; rerun with a fixed input file."
            )
        for temporary, destination in zip(temporary_paths, destinations):
            temporary.replace(destination)
    finally:
        for temporary in temporary_paths:
            temporary.unlink(missing_ok=True)

    print(f"Total records: {len(intakes):,}")
    print(f"Successfully located records: {len(output):,}")
    print(f"Unsuccessfully located records: {len(intakes) - len(output):,}")
    print(f"Point records: {len(output):,}; bounding-box records: 0")
    print(f"Saved CSV: {output_path}")
    print(f"Saved match audit: {audit_path}")
    print(f"Saved summary: {summary_path}")
    return summary


def main():
    """Parse command-line paths/options and run the export; return None."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=INPUT_PATH)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--cache-dir", type=Path, default=CACHE_DIR)
    parser.add_argument("--summary", type=Path, default=SUMMARY_PATH)
    parser.add_argument("--audit", type=Path, default=AUDIT_PATH)
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Require saved official responses; never access the network.",
    )
    args = parser.parse_args()
    run(
        args.input,
        args.output,
        args.cache_dir,
        args.summary,
        offline=args.offline,
        audit_path=args.audit,
    )


if __name__ == "__main__":
    main()
