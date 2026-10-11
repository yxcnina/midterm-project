# Geocoding the cleaned 2024 AAC intake data

This workflow adds point coordinates to the reported `Found Location` in the
cleaned Austin Animal Center (AAC) intake table. It preserves the original
columns and values for accepted events, in their original order. It does not
modify the cleaned input or deduplicate intake events.

The main CSV adds exactly three columns. Only accepted address and intersection
points are retained. Park ranges and other records without accepted point
coordinates are excluded. Detailed match information is kept in a separate
audit file so it does not clutter the analysis table.

## Reproduce the result

Use Python 3.10 or later. From the repository root, with the project's virtual
environment activated:

```bash
python -m pip install -r requirements.txt
python src/geocode_aac_intakes.py --offline
```

The saved `data/reference/geocoding/geocoder_cache.json` contains official
locator responses from earlier queries. `--offline` makes no external requests.
Every address/intersection query needed by the chosen input must already be
cached; an incomplete cache raises an error rather than being counted as a
failed location match. No park snapshot is required.

When an updated cleaned 2024 input contains new locations, normal mode requests
only missing address/intersection responses:

```bash
python src/geocode_aac_intakes.py
```

The public locator endpoint does not require an API key at the time it was used.
Service availability can change. Completed download batches are cached, so a
rerun can continue with uncached locations. The main program and its two helper
modules listed below must stay together.

Optional path arguments are `--input`, `--output`, `--cache-dir`, `--summary`,
and `--audit`. Default CLI paths are anchored to the repository, regardless of
the working directory. Input, output, audit, summary, and temporary file paths
must differ. Input must contain `Animal ID`, `Found Location`, and either
the current `Intake Date` / `Intake Time` pair or the older `DateTime` column.
Split timestamps use `YYYY-MM-DD` and `HH:MM:SS`. They are combined only for
validation; both original columns and the input row order remain unchanged.
Invalid timestamps or dates outside 2024 cause an error rather than silent
removal. Do not use a geocoded output as the input.

## Files and output columns

| File | Purpose |
| --- | --- |
| `src/geocode_aac_intakes.py` | Input checks, point-only event export, match audit, and summary |
| `src/aac_geocoder.py` | Classification, official API requests, caching, and match validation |
| `src/aac_street_validation.py` | Street names, direction, house/route numbers, and aliases |
| `data/processed/aac_intakes_clean.csv` | Unchanged cleaned input |
| `data/reference/geocoding/geocoder_cache.json` | Saved official locator responses and timestamps |
| `data/processed/aac_intakes_clean_geocoded.csv` | Accepted events: all original columns plus three new columns |
| `reports/geocoding/match_audit.csv` | The same accepted events with detailed match information |
| `reports/geocoding/summary.json` | Counts, column definitions, service URL, and file hashes |
| `tests/test_geocode_aac_intakes.py` | Offline validation and pipeline tests |

The three new main-table columns are:

| Column | Meaning |
| --- | --- |
| `latitude` | WGS84 latitude in decimal degrees |
| `longitude` | WGS84 longitude in decimal degrees |
| `location_precision` | Address point, subaddress point, interpolated street address, or intersection |

The main table has no `input_row_id`, geometry-type, bounding-box, park, city,
or detailed source fields. Original input columns are retained even when the
cleaned table gains new animal or event features.

The audit CSV retains the original columns and all three new main-table columns.
It also includes `geocode_status`, the official locator match status; accepted
records have `M` (matched). Other audit fields include `input_row_id`, locator
score/type, matched address, submitted query,
source/matched city, city comparison flag, source URL, retrieval timestamp, and
a reminder that these are geocoded reported addresses rather than observed GPS.
It has the same accepted event rows in the same order as the main table.
`input_row_id` is the one-based data-row position in the exact input snapshot,
excluding its header. It is not an official permanent identifier. No park or
bounding-box fields, failed records, or failure-reason fields are exported.

## Method and acceptance rules

1. Read original columns as strings. Trim location whitespace for lookup only.
   Query each distinct location once, then map the accepted results back to
   every original event, including repeated animals and repeated locations.
2. Distinguish numbered addresses, intersections, and vague locations. City-
   or county-only locations, unknown locations, street-only descriptions, and
   approximate descriptions such as blocks or "near" are not accepted.
   `Travis` in the source suffix is treated as a county, not a city.
3. Query the [City of Austin COA Locator](https://maps.austintexas.gov/arcgis/rest/services/Geocode/COA_Locator/GeocodeServer)
   in batches of up to 250 unique locations, requesting `outSR=4326`.
   Match responses to requests by `ResultID`, rejecting missing or duplicate
   responses. This uses the [ArcGIS geocodeAddresses API](https://developers.arcgis.com/rest/geocode/geocode-addresses/).
4. Accept a point only if its status is `M`, score is between 95 and 100,
   and type is `PointAddress`, `Subaddress`, `StreetAddress`, or `StreetInt`.
   Intersections must match as intersections; numbered addresses must match
   as addresses. House numbers and substantive street names, directions, and
   numbered routes must pass consistency checks. Common abbreviations,
   explicit aliases, and limited spelling differences are allowed.
   Coordinates must be finite and inside a broad regional screening box:
   longitude -98.6 to -96.9 and latitude 29.6 to 31.2.
   This box is not the Austin city boundary.
5. Use `response.location.x` as longitude and `response.location.y` as
   latitude. Do not use `attributes.X/Y`, which may be projected coordinates.
   There is no park-name fallback, park-boundary lookup, or centroid conversion.
6. Export only accepted point records to the main CSV and audit CSV.
   Report total, successfully located, and unsuccessfully located event counts.
   Here, "unsuccessfully located" means excluded under the point-only rules,
   including locations for which only a park range might have been available.
   It does not mean that locating them by any other method is impossible.

The existing locator cache began with responses retrieved on October 8, 2026;
later queries may have different dates. The audit records each accepted
response's retrieval timestamp. Saved responses do not reconstruct the road
network as it existed in 2024. Summary hashes identify the exact input, output,
audit, and cache snapshots used.

Git keeps CSV and JSON files with LF line endings on Windows and Linux so that
the committed data hashes can be checked consistently after downloading.

## Results and community analysis

Read the counts for the current input from `reports/geocoding/summary.json`
after a successful run. The summary also lists output columns and counts by
`location_precision`. Static counts from older input versions are omitted
here so they are not mistaken for results from a newly uploaded cleaned table.
All successful rows are points; `bounding_box_records` is always zero.

| `location_precision` | Interpretation |
| --- | --- |
| `address_point` | Locator address point |
| `subaddress_point` | Locator subaddress point |
| `street_address_interpolated` | Estimated position along a street address range |
| `street_intersection` | Reported intersection |

Counts refer to intake events, not distinct animals. A successful match passes
these rules; it does not establish an animal's observed GPS position. The
locator score is a similarity score, not a probability or error radius.
Every accepted address has not been manually verified.

- Use the point coordinates with the chosen community boundary dataset for
  spatial assignment. Interpolated addresses and intersections have different
  spatial precision from address points; consider this when using small areas.
- `city_label_differs` in the audit flags source and matched city differences.
  These can reflect postal/administrative naming or a mismatch and merit review.
  The flag does not itself establish an error.
- Excluded events may differ systematically from accepted events. Before
  studying crime rates, compare geocoding coverage by intake type, animal type,
  and other available features. Use the full cleaned input for descriptive
  analyses that do not require coordinates.
- These coordinates represent reported intake locations. This script does not
  geocode outcomes or identify adoption destinations. Outcomes require a
  separate, explicit linkage to intake events before attributing them to
  intake-origin communities.

## Validation and provenance

Run the tests without network access:

```bash
python -m unittest discover -s tests -p test_geocode_aac_intakes.py -v
```

Tests cover coarse and ambiguous matches, score thresholds, conflicting house/
street/direction/route numbers, coordinate systems, non-finite values, and
missing, duplicated, or shuffled batch IDs. Pipeline tests check the three-column
main schema, point-only selection, original event/value preservation, audit row
identifiers, both timestamp schemas, invalid dates/times, missing offline
address responses, and path conflicts.

Both CSV files and the JSON summary are written to temporary paths before any
final file is replaced. Each replacement is atomic for that file. The input
SHA-256 is checked again before replacing outputs to detect changes during a
run. The summary includes hashes of both CSV files for verification.

Input data originate from the [Austin Animal Center intake dataset](https://data.austintexas.gov/Health-and-Community-Services/Austin-Animal-Center-Intakes-10-01-2013-to-05-05-2/wter-evkm).
The geocoding implementation and this documentation were prepared with AI
assistance. Team members should review the assumptions and flagged matches
before using the result for substantive research.
