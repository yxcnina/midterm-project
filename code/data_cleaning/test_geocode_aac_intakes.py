import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

import geocode_aac_intakes as geocoder

LOCATION = "123 Main St in Austin (TX)"
SECOND_LOCATION = "456 Main St in Austin (TX)"


def cached_entry():
    return {
        "query": "123 Main St, Austin, TX",
        "retrieved_at_utc": "2026-10-15T00:00:00+00:00",
        "response": {
            "address": "123 Main St, Austin, TX",
            "score": 100,
            "location": {"x": -97.7, "y": 30.3},
            "attributes": {
                "Status": "M", "Addr_type": "StreetAddress", "ResultID": 0,
            },
        },
    }


def write_input(path, locations):
    frame = pd.DataFrame({
        "Animal ID": [f"A{index:03d}" for index in range(len(locations))],
        "DateTime": ["2024-05-11 12:52:00"] * len(locations),
        "Found Location": locations,
        "Intake Date": ["2024-05-11"] * len(locations),
        "Intake Time": ["12:52:00"] * len(locations),
        "Source Note": ["001"] * len(locations),
    })
    frame.to_csv(path, index=False)
    return frame


class GeocoderTests(unittest.TestCase):
    def test_complete_cache_replays_and_preserves_source_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            input_path, output_path, cache_path = (
                folder / "input.csv", folder / "output.csv", folder / "cache.json"
            )
            summary_path = folder / "summary.csv"
            source = write_input(input_path, [LOCATION, LOCATION, "Austin (TX)"])
            cache_path.write_text(json.dumps({LOCATION: cached_entry()}))
            original_input = input_path.read_bytes()
            original_cache = cache_path.read_bytes()
            with patch.object(geocoder, "request_batch") as request:
                counts = geocoder.run(
                    input_path, output_path, cache_path,
                    summary_path=summary_path, offline=True,
                )
            request.assert_not_called()
            result = pd.read_csv(output_path, dtype=str, keep_default_na=False)
            pd.testing.assert_frame_equal(result[source.columns], source.iloc[:2])
            self.assertEqual(
                result.columns.tolist(), [*source.columns, *geocoder.GEO_FIELDS]
            )
            self.assertEqual(counts["successfully_located_records"], 2)
            self.assertEqual(counts["unsuccessfully_located_records"], 1)
            self.assertEqual(input_path.read_bytes(), original_input)
            self.assertEqual(cache_path.read_bytes(), original_cache)
            summary = pd.read_csv(summary_path).set_index("reason")
            self.assertEqual(summary.loc["accepted", "count"], 2)
            self.assertEqual(
                summary.loc["vague_city_county_or_jurisdiction", "count"], 1
            )
            self.assertEqual(summary["count"].sum(), len(source))
            self.assertAlmostEqual(summary["share_of_all_intakes"].sum(), 1.0)
            self.assertAlmostEqual(summary.loc["accepted", "share_of_all_intakes"], 2 / 3)

    def test_missing_cached_location_preserves_files_without_network(self):
        for existing_cache in (True, False):
            with self.subTest(existing_cache=existing_cache):
                with tempfile.TemporaryDirectory() as directory:
                    folder = Path(directory)
                    input_path, output_path, cache_path = (
                        folder / "input.csv", folder / "output.csv",
                        folder / "cache.json",
                    )
                    summary_path = folder / "summary.csv"
                    write_input(input_path, [LOCATION, SECOND_LOCATION])
                    output_path.write_bytes(b"previous output\n")
                    original_cache = None
                    if existing_cache:
                        cache_path.write_text(json.dumps({LOCATION: cached_entry()}))
                        original_cache = cache_path.read_bytes()
                        summary_path.write_bytes(b"previous summary\n")
                    with patch.object(geocoder, "request_batch") as request:
                        with self.assertRaisesRegex(ValueError, "--offline.*missing"):
                            geocoder.run(
                                input_path, output_path, cache_path,
                                summary_path=summary_path, offline=True,
                            )
                    request.assert_not_called()
                    self.assertEqual(output_path.read_bytes(), b"previous output\n")
                    if existing_cache:
                        self.assertEqual(cache_path.read_bytes(), original_cache)
                        self.assertEqual(summary_path.read_bytes(), b"previous summary\n")
                    else:
                        self.assertFalse(cache_path.exists())
                        self.assertFalse(summary_path.exists())
                    self.assertFalse(output_path.with_suffix(".csv.tmp").exists())
                    self.assertFalse(cache_path.with_suffix(".tmp").exists())
                    self.assertFalse(summary_path.with_suffix(".csv.tmp").exists())

    def test_summary_path_conflicts_preserve_existing_files(self):
        for conflict in ("input", "output", "cache", "output_tmp", "cache_tmp", "summary_tmp"):
            with self.subTest(conflict=conflict):
                with tempfile.TemporaryDirectory() as directory:
                    folder = Path(directory)
                    input_path = folder / "input.csv"
                    output_path = folder / "output.csv"
                    cache_path = folder / "cache.json"
                    summary_path = {
                        "input": input_path,
                        "output": output_path,
                        "cache": cache_path,
                        "output_tmp": output_path.with_suffix(".csv.tmp"),
                        "cache_tmp": cache_path.with_suffix(".tmp"),
                        "summary_tmp": folder / "report.csv",
                    }[conflict]
                    if conflict == "summary_tmp":
                        output_path = summary_path.with_suffix(".csv.tmp")
                    write_input(input_path, [LOCATION])
                    output_path.write_bytes(b"previous output\n")
                    cache_path.write_text(json.dumps({LOCATION: cached_entry()}))
                    before = {
                        path: path.read_bytes()
                        for path in (input_path, output_path, cache_path)
                    }
                    with patch.object(geocoder, "request_batch") as request:
                        with self.assertRaisesRegex(ValueError, "paths must differ"):
                            geocoder.run(
                                input_path, output_path, cache_path,
                                summary_path=summary_path, offline=True,
                            )
                    request.assert_not_called()
                    for path, contents in before.items():
                        self.assertEqual(path.read_bytes(), contents)

    def test_invalid_batch_metadata_is_rejected(self):
        cases = [(3857, [0, 1]), (4326, [0]), (4326, [0, 0]), (4326, [0, 2])]
        for wkid, result_ids in cases:
            with self.subTest(wkid=wkid, result_ids=result_ids):
                response = {
                    "spatialReference": {"wkid": wkid},
                    "locations": [
                        {"attributes": {"ResultID": value}}
                        for value in result_ids
                    ],
                }
                with patch.object(geocoder, "http_json", return_value=response):
                    with self.assertRaises(RuntimeError):
                        geocoder.request_batch([LOCATION, SECOND_LOCATION])

    def test_invalid_match_values_are_rejected(self):
        changes = [
            ("location", "x", -120), ("location", "y", float("nan")),
            ("attributes", "Status", "U"), (None, "score", 94.9),
            (None, "score", float("nan")),
        ]
        for section, field, value in changes:
            with self.subTest(section=section, field=field, value=value):
                entry = cached_entry()
                target = entry["response"]
                if section:
                    target = target[section]
                target[field] = value
                self.assertIsNone(geocoder.validate_result(LOCATION, entry))

    def test_primary_reason_follows_validation_order(self):
        entry = cached_entry()
        candidate = entry["response"]
        candidate["attributes"]["Status"] = "U"
        candidate["score"] = 94
        candidate["location"]["x"] = -120
        candidate["address"] = "124 Different St, Austin, TX"
        self.assertEqual(
            geocoder.assess_result(LOCATION, entry)[1], "geocoder_status_not_matched"
        )
        candidate["attributes"]["Status"] = "M"
        self.assertEqual(
            geocoder.assess_result(LOCATION, entry)[1], "score_outside_accepted_range"
        )
        candidate["score"] = 100
        self.assertEqual(
            geocoder.assess_result(LOCATION, entry)[1], "invalid_or_out_of_area_coordinates"
        )
        candidate["location"]["x"] = -97.7
        self.assertEqual(geocoder.assess_result(LOCATION, entry)[1], "house_number_mismatch")
        candidate["address"] = "123 Different St, Austin, TX"
        self.assertEqual(geocoder.assess_result(LOCATION, entry)[1], "street_name_mismatch")
        candidate["address"] = "123 Main St, Austin, TX"
        self.assertEqual(geocoder.assess_result(LOCATION, entry)[1], "accepted")


if __name__ == "__main__":
    unittest.main()
