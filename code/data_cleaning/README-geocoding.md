# AAC intake geocoding

`geocode_aac_intakes.py` matches specific `Found Location` addresses and street intersections to the [City of Austin COA Locator](https://maps.austintexas.gov/arcgis/rest/services/Geocode/COA_Locator/GeocodeServer). It keeps only matches that pass the checks below. The coordinates describe reported intake locations; they are not GPS readings or owner addresses.

The current saved data contain 11,815 intake events. Of these, 7,545 pass the geocoding checks (63.86%) and 4,270 are excluded (36.14%). This is a selected subset. Use all cleaned intake events for non-spatial descriptions.

## Run

Run commands from the repository root after installing `requirements.txt`.

```bash
python code/data_cleaning/geocode_aac_intakes.py
```

The script reuses responses in `.cache/geocoder_cache.json` and requests only missing eligible locations. A fresh run without this local cache needs internet access. The cache is not included in the repository, and new service responses may differ from earlier responses.

To replay a complete local cache without network requests:

```bash
python code/data_cleaning/geocode_aac_intakes.py --offline
```

If any eligible location is missing from the cache, `--offline` stops before writing output, the summary, or the cache. It reports how many locations are missing. The saved processed CSV can be used for Basic Analysis without rerunning the geocoder.

All file paths can be specified. For example, this saves a comparison run separately:

```bash
python code/data_cleaning/geocode_aac_intakes.py --offline --input data/processed/aac_intakes_clean.csv --cache .cache/geocoder_cache.json --output artifacts/geocoding/replayed_intakes.csv --summary artifacts/geocoding/replayed_summary.csv
```

## Outputs

- `data/processed/aac_intakes_clean_geocoded.csv` preserves the original fields of accepted events and adds `latitude`, `longitude`, and `location_precision`.
- [geocoding_summary.csv](../../artifacts/geocoding/geocoding_summary.csv) reports why events were accepted or excluded. `--summary` changes its destination.

The summary has three columns:

| Column | Meaning |
| --- | --- |
| `reason` | `accepted`, or the first reported failed check in the sequence below. |
| `count` | Number of original intake events with this reason. Repeated addresses count once for each event, even though the address is queried only once. |
| `share_of_all_intakes` | `count` divided by all input intake events, expressed from 0 to 1. Multiply by 100 for a percentage. |

Every input event has exactly one reason, so counts sum to the input row count and shares sum to 1 for a nonempty input. Reasons with no events are omitted, except that `accepted` is always included. A primary reason does not mean that the record has no other possible problem.

## Matching checks

The script applies the following checks in order. Adding the summary does not change these acceptance rules.

| Check | Exclusion reason |
| --- | --- |
| The source must identify a numbered address or an intersection. | `missing_location`, `vague_city_county_or_jurisdiction`, `approximate_location_not_resolved`, or `street_only_or_landmark_not_resolved` |
| The service must report a matched result (`Status = M`). | `geocoder_status_not_matched` |
| The score must be finite and between 95 and 100, inclusive. | `score_outside_accepted_range` |
| The returned type must be PointAddress, Subaddress, StreetAddress, or StreetInt. | `unsupported_match_type` |
| A source intersection must match an intersection; a numbered address must match an address. | `address_type_mismatch` |
| Coordinates must be finite WGS84 values within longitude -98.6 to -96.9 and latitude 29.6 to 31.2. | `invalid_or_out_of_area_coordinates` |
| A numbered address must retain its house number. | `house_number_mismatch` |
| Street names, directions, fractions, and street/highway numbers must pass the existing consistency checks. | `street_name_mismatch`, `street_direction_mismatch`, `fractional_street_mismatch`, `street_or_highway_number_mismatch`, or `intersection_street_names_not_resolved` |

A score of 95 is a matching threshold, not a 95% probability that the location is correct. The coordinate bounds are a broad area check, not a city-boundary test.

Each online batch must also return EPSG:4326 and exactly one result for every requested ID. Invalid batch metadata stops the run instead of being counted as ordinary unmatched addresses.

## Offline tests

```bash
python -m unittest discover -s code/data_cleaning -p "test_geocode_aac_intakes.py"
```

The tests use small synthetic inputs. They check repeated-address event counts, preservation of original fields, summary totals, failure-reason order, cache-only replay, batch metadata, and protection of existing files when cache entries are missing or paths overlap. They do not call the live geocoding service.
