# Austin Animal Center Midterm Project

## Intake geocoding

The geocoding workflow uses `data/processed/aac_intakes_clean.csv` and preserves
the original fields of accepted intake events. It adds `latitude`, `longitude`,
and `location_precision`; records without an accepted point are excluded.

From the repository root, with Python 3.10 or later:

```bash
python -m pip install -r requirements.txt
python src/geocode_aac_intakes.py --offline
```

The saved official locator responses make the current input reproducible
without new network requests. Run without `--offline` only when an updated
input needs additional address queries.

- [Geocoded intake data](data/processed/aac_intakes_clean_geocoded.csv)
- [Methods, sources, field definitions, and limitations](docs/geocoding.md)
- [Run summary](reports/geocoding/summary.json)
- [Detailed match audit](reports/geocoding/match_audit.csv)

The current cleaned input has 11,815 events; 7,545 pass the point-location rules
and 4,270 are excluded. These are event counts, not distinct animals. Coordinates
describe reported intake locations, not adoption destinations or verified animal
GPS observations. The method documentation records AI assistance and assumptions.

To run the offline tests:

```bash
python -m unittest discover -s tests -p test_geocode_aac_intakes.py -v
```
