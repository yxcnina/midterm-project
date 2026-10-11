# Austin Animal Center Midterm Project

## Intake geocoding

This part of the project has two deliverables:

- [Python script](src/geocode_aac_intakes.py)
- [Geocoded intake data](data/processed/aac_intakes_clean_geocoded.csv)

The script reads the existing `data/processed/aac_intakes_clean.csv`. It keeps
the original columns and event order, adding only `latitude`, `longitude`, and
`location_precision`. Only accepted address and intersection points are saved.

From the repository root, with Python 3.10 or later:

```bash
python -m pip install -r requirements.txt
python src/geocode_aac_intakes.py
```

The first run needs internet access to query the
[City of Austin locator](https://maps.austintexas.gov/arcgis/rest/services/Geocode/COA_Locator/GeocodeServer).
Responses are saved automatically in `.cache/geocoder_cache.json`, which is
ignored by Git and is not a deliverable. Subsequent runs reuse these responses
and query only missing locations. Deleting the local cache requires new queries.
No separate audit CSV or summary JSON is generated; counts appear in the terminal.

The included CSV has **7,545 rows and 14 columns**: 11 original columns and
3 added columns. Of 11,815 input events, 7,545 passed the rules and 4,270 were
excluded. Counts refer to intake events, not distinct animals.

The script checks that all input dates are in 2024. It queries unique numbered
addresses and intersections, then maps accepted coordinates back to every event.
City/county-only descriptions, approximate locations, and park ranges are excluded.
An accepted match must have status `M`, a similarity score of 95–100, a suitable
address type, consistent house/street/route information, and finite coordinates
within a broad Austin-region screening box. This box is not the city boundary.

| Added column | Meaning |
| --- | --- |
| `latitude` | WGS84 latitude in decimal degrees |
| `longitude` | WGS84 longitude in decimal degrees |
| `location_precision` | `address_point`, `subaddress_point`, `street_address_interpolated`, or `street_intersection` |

Coordinates describe reported intake locations, not adoption destinations or
verified animal GPS observations. Interpolated addresses and intersections have
different precision from address points. Excluded events may differ from those
retained, so check coverage before community-level analysis. Official address
data can change: a fresh online run may differ from this saved result, which used
responses collected in October 2026, and does not reconstruct 2024 geography.

Input records originate from the
[Austin Animal Center intake dataset](https://data.austintexas.gov/Health-and-Community-Services/Austin-Animal-Center-Intakes-10-01-2013-to-05-05-2/wter-evkm).
The geocoding code and this documentation were prepared with AI assistance.
