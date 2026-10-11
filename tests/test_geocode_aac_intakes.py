"""Offline regression checks for mistakes that could change spatial results.

Run from the repository root with:
    python -m unittest discover -s tests -p 'test_geocode_aac_intakes.py'

Synthetic locator responses are used throughout; no API requests are sent.
"""
from copy import deepcopy
from contextlib import redirect_stdout
import csv
import io
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import aac_geocoder as geocoder
import geocode_aac_intakes as pipeline
from aac_street_validation import street_consistency_reason


class GeocodingBoundaryTests(unittest.TestCase):
    source = "7201 Levander Loop in Austin (TX)"

    def candidate(self, **changes):
        response = {
            "address": "7201 LEVANDER LOOP, AUSTIN, TX, 78702",
            "score": 100,
            "location": {"x": -97.6908, "y": 30.2513},
            "attributes": {
                "Status": "M", "Addr_type": "PointAddress", "ResultID": 0,
                # Some services include projected feet in these attributes.
                "X": 3123123, "Y": 9988998,
            },
        }
        response.update(changes)
        return {
            "query": "7201 Levander Loop, Austin, TX",
            "retrieved_at_utc": "2026-10-10T00:00:00+00:00",
            "response": response,
        }

    def test_non_specific_locations_are_not_submitted_as_addresses(self):
        for text in (
            "Austin (TX)", "Travis (TX)", "Cedar Park (TX)",
            "Outside Jurisdiction", "Unknown", "", "   ",
            "Near 7201 Levander Loop in Austin (TX)",
            "7000 block of Levander Loop in Austin (TX)",
        ):
            with self.subTest(location=text):
                self.assertNotIn(
                    geocoder.classify(text)[0], {"numbered_address", "intersection"}
                )

    def test_travis_county_is_not_misrepresented_as_a_city(self):
        for county in ("Travis", "Travis County"):
            with self.subTest(county=county):
                detail, place, query = geocoder.split_location(
                    f"11309 Jones Rd in {county} (TX)"
                )
                self.assertEqual(detail, "11309 Jones Rd")
                self.assertEqual(place, county)
                self.assertEqual(query, "11309 Jones Rd, TX")

    def test_coordinates_come_from_wgs84_response_not_projected_attributes(self):
        result = geocoder.validate_result(self.source, self.candidate())
        self.assertTrue(result["is_location_valid"])
        self.assertEqual(result["longitude"], -97.6908)
        self.assertEqual(result["latitude"], 30.2513)
        self.assertEqual(result["location_precision"], "address_point")

    def test_score_cutoff_includes_95_but_excludes_lower_scores(self):
        for score, expected in ((94.99, False), (95.0, True)):
            with self.subTest(score=score):
                result = geocoder.validate_result(self.source, self.candidate(score=score))
                self.assertEqual(result["is_location_valid"], expected)

    def test_perfect_score_does_not_override_ambiguous_or_unmatched_status(self):
        for status in ("T", "U"):
            with self.subTest(status=status):
                entry = self.candidate()
                entry["response"]["attributes"]["Status"] = status
                self.assertFalse(geocoder.validate_result(self.source, entry)["is_location_valid"])

    def test_high_score_does_not_make_a_street_or_city_centroid_precise(self):
        for address_type in ("StreetName", "StreetMidBlock", "StreetAddressExt", "Locality"):
            with self.subTest(address_type=address_type):
                entry = self.candidate()
                entry["response"]["attributes"]["Addr_type"] = address_type
                self.assertFalse(geocoder.validate_result(self.source, entry)["is_location_valid"])
        entry = self.candidate()
        entry["response"]["attributes"]["Addr_type"] = "PointAddress"
        self.assertFalse(geocoder.validate_result(
            "Levander Loop and Airport Blvd in Austin (TX)", entry
        )["is_location_valid"])

    def test_house_street_direction_and_route_number_conflicts_are_rejected(self):
        pairs = (
            ("7202 Levander Loop", "7201 LEVANDER LOOP"),
            ("3716 South Congress", "3716 SOUTH"),
            ("9500 S Ih 35", "9500 N IH 35 SVRD SB"),
            ("8312 N Ih 35 Svrd Nb", "8312 N IH 35 SVRD SB"),
            ("1000 E 12th St", "1000 E 11TH ST"),
        )
        for source, target in pairs:
            with self.subTest(source=source, target=target):
                result = geocoder.validate_result(
                    source + " in Austin (TX)",
                    self.candidate(address=target + ", AUSTIN, TX"),
                )
                self.assertFalse(result["is_location_valid"])

    def test_ordinary_aliases_and_reversed_intersection_order_are_accepted(self):
        cases = (
            ("3401 West Parmer Lane", "3401 W PARMER LN", "numbered_address"),
            ("3622 Manchaca Rd Apt148", "3622 MENCHACA RD", "numbered_address"),
            ("West Slaughter Lane And Manchaca Road", "MENCHACA & W SLAUGHTER", "intersection"),
        )
        for source, target, kind in cases:
            with self.subTest(source=source):
                self.assertEqual(street_consistency_reason(source, target, kind), "")

    def test_non_finite_scores_and_coordinates_cannot_be_valid(self):
        for number in (float("nan"), float("inf"), float("-inf")):
            for field in ("score", "x", "y"):
                with self.subTest(number=number, field=field):
                    entry = self.candidate()
                    if field == "score":
                        entry["response"]["score"] = number
                    else:
                        entry["response"]["location"][field] = number
                    result = geocoder.validate_result(self.source, entry)
                    self.assertFalse(result["is_location_valid"])

    def batch_response(self, ids):
        locations = []
        for result_id in ids:
            candidate = deepcopy(self.candidate()["response"])
            candidate["attributes"]["ResultID"] = result_id
            candidate["address"] = f"fixture result {result_id}"
            locations.append(candidate)
        return {"spatialReference": {"wkid": 4326}, "locations": locations}

    def test_missing_batch_result_fails_instead_of_shifting_coordinates(self):
        with patch.object(geocoder, "http_json", return_value=self.batch_response([0])):
            with self.assertRaises(RuntimeError):
                geocoder.request_batch([self.source, "905 Bedford St in Austin (TX)"])

    def test_duplicate_result_ids_fail_even_when_every_request_id_is_present(self):
        # A dict comprehension alone silently overwrites the extra ResultID 0.
        with patch.object(geocoder, "http_json", return_value=self.batch_response([0, 0, 1])):
            with self.assertRaises(RuntimeError):
                geocoder.request_batch([self.source, "905 Bedford St in Austin (TX)"])

    def test_batch_result_ids_control_mapping_and_output_crs_is_requested(self):
        sources = [self.source, "905 Bedford St in Austin (TX)"]
        with patch.object(geocoder, "http_json", return_value=self.batch_response([1, 0])) as request:
            results = geocoder.request_batch(sources)
        self.assertEqual(results[sources[0]]["response"]["address"], "fixture result 0")
        self.assertEqual(results[sources[1]]["response"]["address"], "fixture result 1")
        self.assertEqual(str(request.call_args.args[1]["outSR"]), "4326")
        bad_crs = self.batch_response([0])
        bad_crs["spatialReference"]["wkid"] = 102739
        with patch.object(geocoder, "http_json", return_value=bad_crs):
            with self.assertRaises(RuntimeError):
                geocoder.request_batch([self.source])


class GeocodingPipelineTests(unittest.TestCase):
    columns = ["Animal ID", "DateTime", "Found Location", "Color", "Optional Note"]
    added_columns = [
        "latitude", "longitude", "location_precision",
    ]
    source = "7201 Levander Loop in Austin (TX)"

    def write_input(self, path, rows):
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=self.columns)
            writer.writeheader()
            writer.writerows(rows)

    def event(self, animal_id="00017", date="2024-06-01 10:30:00", location=None):
        return {
            "Animal ID": animal_id, "DateTime": date,
            "Found Location": self.source if location is None else location,
            "Color": "Black/White", "Optional Note": "",
        }

    def write_cache(self, cache):
        """Save one synthetic official response; no park snapshot is needed."""
        cache.mkdir(parents=True, exist_ok=True)
        entry = {
            "query": "7201 Levander Loop, Austin, TX",
            "retrieved_at_utc": "2026-10-10T00:00:00+00:00",
            "response": {
                "address": "7201 LEVANDER LOOP, AUSTIN, TX, 78702",
                "score": 100,
                "location": {"x": -97.6908, "y": 30.2513},
                "attributes": {
                    "Status": "M", "Addr_type": "PointAddress", "City": "Austin",
                },
            },
        }
        (cache / "geocoder_cache.json").write_text(
            json.dumps({self.source: entry}), encoding="utf-8"
        )

    def read_csv(self, path):
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            return reader.fieldnames, list(reader)

    def test_run_preserves_events_with_three_added_columns_and_separate_audit(self):
        with TemporaryDirectory() as directory:
            base = Path(directory)
            source, output, summary = base / "input.csv", base / "output.csv", base / "summary.json"
            cache, audit = base / "cache", base / "audit.csv"
            originals = [
                self.event(),
                self.event("00018", location="Austin (TX)"),
                self.event("00019", date="2024-06-02 10:30:00", location="  " + self.source + "  "),
                self.event(),
            ]
            self.write_input(source, originals)
            self.write_cache(cache)
            original_bytes = source.read_bytes()
            with patch.object(geocoder, "request_batch", side_effect=AssertionError("Unexpected network query")) as request:
                with redirect_stdout(io.StringIO()):
                    counts = pipeline.run(
                        source, output, cache, summary,
                        offline=True, audit_path=audit,
                    )
                request.assert_not_called()
            fieldnames, rows = self.read_csv(output)
            audit_fields, audit_rows = self.read_csv(audit)
            self.assertEqual(fieldnames, [*self.columns, *self.added_columns])
            self.assertEqual(len(rows), 3)
            self.assertNotIn("input_row_id", fieldnames)
            self.assertNotIn("geocode_status", fieldnames)
            self.assertIn("input_row_id", audit_fields)
            self.assertIn("geocode_status", audit_fields)
            self.assertIn("geocode_match_address", audit_fields)
            self.assertEqual([row["input_row_id"] for row in audit_rows], ["1", "3", "4"])
            # Original labels, blanks, spacing and even repeated events survive.
            self.assertEqual([{key: row[key] for key in self.columns} for row in rows],
                             [originals[0], originals[2], originals[3]])
            for row in rows:
                self.assertEqual(float(row["latitude"]), 30.2513)
                self.assertEqual(float(row["longitude"]), -97.6908)
                self.assertEqual(row["location_precision"], "address_point")
            self.assertTrue(
                all(row["geocode_status"] == "M" for row in audit_rows)
            )
            self.assertEqual(source.read_bytes(), original_bytes)
            self.assertEqual(counts["total_records"], 4)
            self.assertEqual(counts["successfully_located_records"], 3)
            self.assertEqual(counts["unsuccessfully_located_records"], 1)
            self.assertEqual(counts["point_records"], len(rows))
            self.assertEqual(counts["bounding_box_records"], 0)
            self.assertEqual(counts["added_output_columns"], self.added_columns)
            self.assertEqual(counts["audit_sha256"], pipeline.file_sha256(audit))
            self.assertEqual(json.loads(summary.read_text(encoding="utf-8")), counts)

    def test_parks_are_excluded_without_requiring_a_park_snapshot(self):
        with TemporaryDirectory() as directory:
            base = Path(directory)
            source, output, summary = base / "input.csv", base / "output.csv", base / "summary.json"
            cache = base / "cache"
            self.write_cache(cache)
            self.write_input(source, [
                self.event(),
                self.event("00018", location="Zilker Park in Austin (TX)"),
            ])
            with patch.object(geocoder, "request_batch", side_effect=AssertionError("Unexpected network query")) as request:
                with redirect_stdout(io.StringIO()):
                    counts = pipeline.run(source, output, cache, summary, offline=True)
                request.assert_not_called()
            fields, rows = self.read_csv(output)
            _, audit_rows = self.read_csv(base / "match_audit.csv")
            self.assertEqual(fields, [*self.columns, *self.added_columns])
            self.assertEqual([row["Animal ID"] for row in rows], ["00017"])
            self.assertEqual([row["input_row_id"] for row in audit_rows], ["1"])
            self.assertFalse((cache / "parks.json").exists())
            self.assertEqual(counts["total_records"], 2)
            self.assertEqual(counts["successfully_located_records"], 1)
            self.assertEqual(counts["unsuccessfully_located_records"], 1)
            self.assertEqual(counts["point_records"], 1)
            self.assertEqual(counts["bounding_box_records"], 0)

    def test_out_of_year_inputs_fail_before_overwriting_existing_outputs(self):
        with TemporaryDirectory() as directory:
            base = Path(directory)
            source, output, summary = base / "input.csv", base / "output.csv", base / "summary.json"
            audit = base / "audit.csv"
            output.write_bytes(b"previous CSV output")
            summary.write_bytes(b"previous summary")
            audit.write_bytes(b"previous audit")
            for invalid_date in ("2023-12-31 23:59:59", "2025-01-01 00:00:00"):
                with self.subTest(date=invalid_date):
                    self.write_input(source, [self.event(), self.event("00018", date=invalid_date)])
                    with patch.object(pipeline, "build_location_lookup") as lookup:
                        with self.assertRaisesRegex(ValueError, "2024"):
                            pipeline.run(
                                source, output, base / "cache", summary,
                                offline=True, audit_path=audit,
                            )
                        lookup.assert_not_called()
                    self.assertEqual(output.read_bytes(), b"previous CSV output")
                    self.assertEqual(summary.read_bytes(), b"previous summary")
                    self.assertEqual(audit.read_bytes(), b"previous audit")

    def test_split_dates_preserve_source_columns_event_order_and_audit_rows(self):
        """The teammate's split schema keeps its order and every source value."""
        columns = [
            "Animal ID", "Intake Date", "Intake Time", "Found Location",
            "Color", "Optional Note",
        ]
        originals = [
            {
                "Animal ID": "00017", "Intake Date": "2024-12-31",
                "Intake Time": "23:59:59", "Found Location": self.source,
                "Color": "Black/White", "Optional Note": "",
            },
            {
                "Animal ID": "00018", "Intake Date": "2024-01-01",
                "Intake Time": "00:00:00", "Found Location": self.source,
                "Color": "Brown", "Optional Note": "  preserve spacing  ",
            },
        ]
        with TemporaryDirectory() as directory:
            base = Path(directory)
            source, output = base / "input.csv", base / "output.csv"
            summary, audit = base / "summary.json", base / "audit.csv"
            cache = base / "cache"
            self.write_cache(cache)
            with source.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=columns)
                writer.writeheader()
                writer.writerows(originals)
            original_bytes = source.read_bytes()
            with patch.object(
                geocoder, "request_batch",
                side_effect=AssertionError("Unexpected network query"),
            ) as request:
                with redirect_stdout(io.StringIO()):
                    counts = pipeline.run(
                        source, output, cache, summary,
                        offline=True, audit_path=audit,
                    )
                request.assert_not_called()
            fields, rows = self.read_csv(output)
            _, audit_rows = self.read_csv(audit)
            self.assertEqual(fields, [*columns, *self.added_columns])
            self.assertNotIn("DateTime", fields)
            self.assertEqual(
                [{key: row[key] for key in columns} for row in rows],
                originals,
            )
            self.assertEqual(
                [row["input_row_id"] for row in audit_rows], ["1", "2"]
            )
            for row in rows:
                self.assertEqual(float(row["latitude"]), 30.2513)
                self.assertEqual(float(row["longitude"]), -97.6908)
            self.assertEqual(source.read_bytes(), original_bytes)
            self.assertEqual(counts["total_records"], 2)
            self.assertEqual(counts["successfully_located_records"], 2)
            self.assertEqual(counts["unsuccessfully_located_records"], 0)

    def test_invalid_split_dates_fail_before_lookup_or_output_replacement(self):
        """Bad split timestamps never alter previous results or query a locator."""
        columns = [
            "Animal ID", "Intake Date", "Intake Time", "Found Location",
        ]
        valid = {
            "Animal ID": "00017", "Intake Date": "2024-06-01",
            "Intake Time": "10:30:00", "Found Location": self.source,
        }
        cases = [
            ("previous year", "Intake Date", "2023-12-31", None),
            ("following year", "Intake Date", "2025-01-01", None),
            ("invalid date", "Intake Date", "2024-02-30", None),
            ("invalid time", "Intake Time", "25:61:00", None),
            ("empty date", "Intake Date", "", None),
            ("empty time", "Intake Time", "", None),
            ("missing date column", None, None, "Intake Date"),
            ("missing time column", None, None, "Intake Time"),
        ]
        with TemporaryDirectory() as directory:
            base = Path(directory)
            source, output = base / "input.csv", base / "output.csv"
            summary, audit = base / "summary.json", base / "audit.csv"
            previous = {
                output: b"previous CSV output",
                summary: b"previous summary",
                audit: b"previous audit",
            }
            for path, contents in previous.items():
                path.write_bytes(contents)
            for label, field, value, missing_column in cases:
                with self.subTest(case=label):
                    invalid = {**valid, "Animal ID": "00018"}
                    if field is not None:
                        invalid[field] = value
                    fields = [key for key in columns if key != missing_column]
                    with source.open("w", encoding="utf-8", newline="") as handle:
                        writer = csv.DictWriter(handle, fieldnames=fields)
                        writer.writeheader()
                        writer.writerows(
                            {key: row[key] for key in fields}
                            for row in (valid, invalid)
                        )
                    original_bytes = source.read_bytes()
                    with patch.object(pipeline, "build_location_lookup") as lookup:
                        with self.assertRaises(ValueError):
                            pipeline.run(
                                source, output, base / "cache", summary,
                                offline=True, audit_path=audit,
                            )
                        lookup.assert_not_called()
                    self.assertEqual(source.read_bytes(), original_bytes)
                    self.assertEqual(
                        {path: path.read_bytes() for path in previous}, previous
                    )

    def test_offline_missing_locator_cache_does_not_create_false_failure_counts(self):
        with TemporaryDirectory() as directory:
            base = Path(directory)
            source, output, summary = base / "input.csv", base / "output.csv", base / "summary.json"
            cache = base / "cache"
            cache.mkdir()
            audit = base / "audit.csv"
            self.write_input(source, [self.event()])
            output.write_bytes(b"previous CSV output")
            summary.write_bytes(b"previous summary")
            audit.write_bytes(b"previous audit")
            with patch.object(geocoder, "request_batch", side_effect=AssertionError("Unexpected network query")) as request:
                for cache_exists in (False, True):
                    if cache_exists:
                        (cache / "geocoder_cache.json").write_text("{}", encoding="utf-8")
                    with self.assertRaisesRegex(RuntimeError, "Offline cache is missing"):
                        pipeline.run(
                            source, output, cache, summary,
                            offline=True, audit_path=audit,
                        )
                request.assert_not_called()
            self.assertEqual(output.read_bytes(), b"previous CSV output")
            self.assertEqual(summary.read_bytes(), b"previous summary")
            self.assertEqual(audit.read_bytes(), b"previous audit")

    def test_input_output_summary_and_audit_path_collisions_never_overwrite(self):
        pairs = (
            ("input", "output"), ("input", "summary"), ("input", "audit"),
            ("output", "summary"), ("output", "audit"), ("summary", "audit"),
        )
        with TemporaryDirectory() as directory:
            base = Path(directory)
            originals = {
                "input": base / "input.csv", "output": base / "output.csv",
                "summary": base / "summary.json", "audit": base / "audit.csv",
            }
            self.write_input(originals["input"], [self.event()])
            for name in ("output", "summary", "audit"):
                originals[name].write_text(f"previous {name}", encoding="utf-8")
            before = {path: path.read_bytes() for path in originals.values()}
            for first, second in pairs:
                with self.subTest(first=first, second=second):
                    paths = dict(originals)
                    # Lexically different paths still point to the same file.
                    paths[second] = base / "alias" / ".." / paths[first].name
                    with patch.object(pipeline, "build_location_lookup") as lookup:
                        with self.assertRaises(ValueError):
                            pipeline.run(
                                paths["input"], paths["output"], base / "cache",
                                paths["summary"], offline=True, audit_path=paths["audit"],
                            )
                        lookup.assert_not_called()
                    self.assertEqual(
                        {path: path.read_bytes() for path in before}, before
                    )


if __name__ == "__main__":
    unittest.main()
