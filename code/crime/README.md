# Crime Data Integration (Issue #22)

## Goal

Construct a reproducible Austin **2024 council-district-by-month** dataset that combines reported crime incidents with **stray animal intakes**. This dataset supports an exploratory analysis of associations; it does **not** measure the causal effect of crime on animal intake.

## Data sources

1. **Austin Police Department, Crime Reports 2024:** https://data.austintexas.gov/d/hbc5-hmey  
   The script accesses its public Socrata API, selecting `incident_report_number`, `occ_date`, and `council_district` and restricting observations to occurrence dates in 2024. Each incident ID is counted once.
2. **City of Austin, Council District geographic boundaries:** https://maps.austintexas.gov/arcgis/rest/services/Shared/BoundariesGrids_2/MapServer/0  
   The script downloads council-district polygons through the ArcGIS REST API in WGS84 coordinates. The published boundary may be updated over time; the committed GeoJSON preserves the geometry used in this run.
3. **Austin Animal Center (AAC), 2024 geocoded intake data:** `data/processed/aac_intakes_clean_geocoded.csv`, produced by the team's upstream intake-cleaning and geocoding process. The animal data must be prepared before running this module.

## Run from the repository root

```bash
python -m pip install -r requirements.txt
python code/crime/crime_component.py
```

The program makes internet requests to the two City of Austin endpoints. It uses repository-relative locations resolved from the Python file, so commands can be run from the repository root on another computer.

## Outputs

- `data/raw/crime_reports_2024.csv`: selected crime API fields plus derived date, district and month (an API extract rather than a complete raw police dataset).
- `data/raw/council_districts.geojson`: downloaded council district boundaries.
- `data/processed/stray_geocoded_districts_2024.csv`: intermediate matched animal-level rows, **generated locally and intentionally not committed** because it contains precise location information.
- `data/processed/crime_stray_district_month_2024.csv`: one row per council district and month (10 × 12 = 120 rows).
- `data/processed/crime_stray_district_2024.csv`: annual totals for each of the 10 council districts.
- `artifacts/crime/district_scatter.png` and `artifacts/crime/monthly_trends.png`: quick exploratory figures. Final statistical analysis and presentation figures belong to Issue #23.

## Methods and checks

- Filter geocoded AAC records to `Intake Type == "Stray"`, and remove records referring to the shelter's `7201 Levander` address so that the shelter is not treated as the animal's original found location.
- Match each remaining latitude/longitude point to **exactly one** official council-district polygon; drop observations with no unique district assignment.
- Count reported crime incidents and matched stray intakes separately by district and month; combine counts onto a complete 10-district × 12-month grid, filling absent event counts with zero.
- Aggregate monthly counts to annual totals.

## Results from the initial local run

The downloaded crime extract contained **86,314** reported incidents with unique incident IDs. Of these, **85,437** were assigned to districts 1–10; **877** lacked a valid district code. From **6,174** geocoded stray-intake records, the pipeline excluded **62** potential shelter-location records and **1,448** records without a unique council-district match, leaving **4,664** matched stray intakes. This produced **120 district-month observations**. These figures describe the tested data snapshot; API updates may alter a later run.

## Limitations

- **Crime counts are not crime rates:** district population was not used as a denominator.
- **Stray is not the same as abandonment:** some strays may be lost pets.
- Animal-level matching covers only a subset of all AAC stray intakes, and missing or inaccurate geocodes may bias geographic comparisons.
- Reported police incidents do not capture all crimes. The API extract and geographic boundary data can be revised after the snapshot date.
- Geographic comparisons may reflect population, area, pet ownership, reporting practices or other confounding factors; correlations are not causal findings.

## Suggested extensions

Validate geocoding coverage by district; compare rates using appropriate area/population denominators; examine additional years or crime categories; and document the exact versions and sources of the upstream AAC geocoding pipeline.
