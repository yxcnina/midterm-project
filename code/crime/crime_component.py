"""Austin 2024 crime and stray-intake analysis: reproducible data pipeline.

Inputs: data/processed/aac_intakes_clean_geocoded.csv (created by the team's
reproducible intake cleaning/geocoding process).

Official sources:
Crime Reports 2024: https://data.austintexas.gov/d/hbc5-hmey
District boundaries: https://maps.austintexas.gov/arcgis/rest/services/Shared/BoundariesGrids_2/MapServer/0

Run from repository root: python code/crime/crime_component.py
"""
from pathlib import Path
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import requests
from shapely.geometry import Point, shape

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
DATA = ROOT / "data" / "processed"
RESULTS = ROOT / "artifacts" / "crime"
INTAKES = DATA / "aac_intakes_clean_geocoded.csv"
CRIME_URL = "https://data.austintexas.gov/resource/hbc5-hmey.json"
DISTRICT_URL = (
    "https://maps.austintexas.gov/arcgis/rest/services/"
    "Shared/BoundariesGrids_2/MapServer/0/query"
)


def get_json(url, params):
    """Fetch JSON from an official endpoint and raise clear HTTP errors."""
    response = requests.get(url, params=params, timeout=90)
    response.raise_for_status()
    payload = response.json()
    if isinstance(payload, dict) and "error" in payload:
        raise RuntimeError(f"API error: {payload}")
    return payload


def download_crime():
    """Download 2024 reported incidents with date and council district."""
    pages = []
    offset = 0
    page_size = 50000
    while True:
        params = {
            "$select": "incident_report_number,occ_date,council_district",
            "$order": "incident_report_number",
            "$limit": page_size,
            "$offset": offset,
        }
        data = get_json(CRIME_URL, params)
        if not isinstance(data, list):
            raise ValueError(f"Unexpected response from crime API: {data}")
        pages.extend(data)
        print(f"Crime API: downloaded {len(pages):,} rows", flush=True)
        if len(data) < page_size:
            break
        offset += page_size
        if offset > 200000:
            raise RuntimeError("Unexpected number of 2024 records; check API")

    if not pages:
        raise ValueError("No crime data returned. Check the official API link.")
    df = pd.DataFrame(pages)
    needed = {"incident_report_number", "occ_date", "council_district"}
    if not needed.issubset(df.columns):
        raise ValueError(f"Crime dataset missing columns: {needed - set(df.columns)}")
    df["date"] = pd.to_datetime(df["occ_date"], errors="coerce")
    df = df.loc[df["date"].dt.year.eq(2024)].copy()
    if df.empty:
        raise ValueError("No incidents with occurrence dates in 2024")
    # One row is expected per reported incident; prevent duplicate counting.
    print("Crime duplicated incident IDs:", df["incident_report_number"].duplicated().sum())
    df = df.drop_duplicates(subset="incident_report_number")
    df["district"] = pd.to_numeric(df["council_district"], errors="coerce")
    df["month"] = df["date"].dt.month
    df.to_csv(RAW / "crime_reports_2024.csv", index=False)
    return df


def district_number(properties):
    """Find council district 1-10 from the official polygon properties."""
    for key, value in properties.items():
        if "district" not in key.lower() or value is None:
            continue
        value_text = str(value).strip()
        found = re.fullmatch(r"(?:District\s*)?(10|[1-9])(?:\.0)?", value_text, re.I)
        if found:
            return int(found.group(1))
    raise ValueError(f"Cannot find district number among polygon attributes: {properties}")


def download_district_polygons():
    """Obtain council district boundaries as WGS84 GeoJSON polygons."""
    params = {
        "where": "1=1",
        "outFields": "*",
        "outSR": "4326",
        "returnGeometry": "true",
        "f": "geojson",
    }
    geojson = get_json(DISTRICT_URL, params)
    features = geojson.get("features", [])
    if not features:
        raise ValueError(f"No district polygons returned: {geojson}")
    district_polygons = {}
    for feature in features:
        district = district_number(feature.get("properties", {}))
        geometry = shape(feature["geometry"])
        if district in district_polygons:
            district_polygons[district] = district_polygons[district].union(geometry)
        else:
            district_polygons[district] = geometry
    if len(district_polygons) != 10:
        raise ValueError(f"Expected 10 district polygons, got {sorted(district_polygons)}")
    import json
    (RAW / "council_districts.geojson").write_text(
        json.dumps(geojson), encoding="utf-8"
    )
    return district_polygons


def assign_district(longitude, latitude, polygons):
    """Return the matching city council district or missing for out-of-city."""
    if pd.isna(longitude) or pd.isna(latitude):
        return None
    point = Point(float(longitude), float(latitude))
    matches = [d for d, polygon in polygons.items() if polygon.covers(point)]
    if len(matches) != 1:
        return None
    return matches[0]


def prepare_strays(polygons):
    """Clean located stray-intake records and attach district number."""
    if not INTAKES.exists():
        raise FileNotFoundError(
            f"Missing input: {INTAKES}\n"
            "Copy the team geocoded CSV into the data folder."
        )
    data = pd.read_csv(INTAKES, low_memory=False)
    required = {"Intake Type", "Found Location", "Intake Date", "latitude", "longitude"}
    if not required.issubset(data.columns):
        raise ValueError(f"Intake dataset missing columns: {required - set(data.columns)}")
    df = data.loc[data["Intake Type"].eq("Stray")].copy()
    print(f"Geocoded stray records (before QC): {len(df):,}")
    # Shelter address is not a valid proxy for the original animal location.
    shelter = df["Found Location"].str.contains(
        r"\b7201\s+Levander\b", regex=True, case=False, na=False
    )
    print(f"Excluded possible shelter-address records: {int(shelter.sum()):,}")
    df = df.loc[~shelter].copy()
    df["date"] = pd.to_datetime(df["Intake Date"], errors="coerce")
    df = df.loc[df["date"].dt.year.eq(2024)].copy()
    df["district"] = [
        assign_district(lon, lat, polygons)
        for lon, lat in zip(df["longitude"], df["latitude"])
    ]
    unmatched = int(df["district"].isna().sum())
    print(f"Not in a unique Austin council district: {unmatched:,} / {len(df):,}")
    df = df.dropna(subset=["district"]).copy()
    df["district"] = df["district"].astype(int)
    df["month"] = df["date"].dt.month
    df.to_csv(DATA / "stray_geocoded_districts_2024.csv", index=False)
    return df


def combine_and_plot(crime, strays):
    """Aggregate to district-month level, join, and save two figures."""
    crime_valid = crime.loc[crime["district"].between(1, 10)].copy()
    print("Crime records without district 1-10:", len(crime) - len(crime_valid))
    crimes = crime_valid.groupby(["district", "month"]).size().rename("crime_count")
    intakes = strays.groupby(["district", "month"]).size().rename("stray_intake_count")
    months = pd.MultiIndex.from_product(
        [range(1, 11), range(1, 13)], names=["district", "month"]
    )
    merged = pd.concat([crimes, intakes], axis=1).reindex(months).fillna(0)
    merged = merged.astype(int).reset_index()
    merged.to_csv(DATA / "crime_stray_district_month_2024.csv", index=False)
    annual = merged.groupby("district", as_index=False)[
        ["crime_count", "stray_intake_count"]
    ].sum()
    annual.to_csv(DATA / "crime_stray_district_2024.csv", index=False)
    print("District-month observations:", len(merged))
    print("Annual district results:\n", annual.to_string(index=False))

    plt.figure(figsize=(7, 5))
    plt.scatter(annual["crime_count"], annual["stray_intake_count"])
    for row in annual.itertuples(index=False):
        plt.annotate(str(row.district), (row.crime_count, row.stray_intake_count))
    plt.xlabel("2024 reported crime incidents (count)")
    plt.ylabel("2024 geocoded stray intakes (count)")
    plt.title("Austin council districts: crime vs stray intakes")
    plt.tight_layout()
    plt.savefig(RESULTS / "district_scatter.png", dpi=180)
    plt.close()

    monthly = merged.groupby("month", as_index=False)[["crime_count", "stray_intake_count"]].sum()
    fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    axes[0].plot(monthly["month"], monthly["crime_count"], marker="o")
    axes[0].set_ylabel("Reported incidents")
    axes[1].plot(monthly["month"], monthly["stray_intake_count"], marker="o")
    axes[1].set_ylabel("Geocoded stray intakes")
    axes[1].set_xlabel("Month of 2024")
    axes[1].set_xticks(range(1, 13))
    fig.suptitle("Monthly reports and stray intakes, city districts")
    fig.tight_layout()
    fig.savefig(RESULTS / "monthly_trends.png", dpi=180)
    plt.close(fig)


def main():
    """Run the repeatable download, spatial matching and analysis steps."""
    RAW.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    print("1/4 Downloading reported crime records...")
    crime = download_crime()
    print("2/4 Downloading council district polygons...")
    polygons = download_district_polygons()
    print("3/4 Mapping stray intakes to districts...")
    strays = prepare_strays(polygons)
    print("4/4 Aggregating and plotting...")
    combine_and_plot(crime, strays)
    print("SUCCESS: generated CSV outputs in data/raw/, data/processed/ and figures in artifacts/crime/")


if __name__ == "__main__":
    main()
