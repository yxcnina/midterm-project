"""Conservative geocoding using the public City of Austin locator (stdlib only).

Coordinates are WGS84 longitude/latitude from response.location, NOT attributes.X/Y.
Score is a locator similarity score, not a probability or accuracy radius.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
import time
import urllib.parse
import urllib.request

from aac_street_validation import street_consistency_reason

BASE = Path(__file__).resolve().parents[1] / "data" / "reference" / "geocoding"
SERVICE = "https://maps.austintexas.gov/arcgis/rest/services/Geocode/COA_Locator/GeocodeServer"
MIN_SCORE = 95.0
BATCH_SIZE = 250
ALLOWED_TYPES = {"PointAddress", "Subaddress", "StreetAddress", "StreetInt"}

def split_location(location):
    """Keep the original string elsewhere; only normalize the geocoder query."""
    text = location.strip()
    match = re.match(r"^(.*?)\s+in\s+(.+?)\s*\(TX\)\s*$", text, re.I)
    if match:
        detail, city = match.groups()
        # Travis is a county in this dataset, not the city of Travis, Texas.
        query = f"{detail}, TX" if city.lower() in {"travis", "travis county"} else f"{detail}, {city}, TX"
        return detail.strip(), city.strip(), query
    return text, "", re.sub(r"\s*\(TX\)\s*$", ", TX", text, flags=re.I)

def classify(location):
    detail, city, query = split_location(location)
    if not detail:
        return "missing_location", detail, city, query
    if (re.fullmatch(r"[^()]+\s*\(TX\)", location.strip(), re.I) and not city) or re.search(
        r"^(outside jurisdiction|unknown|not given|none|n/?a)$", detail, re.I
    ):
        return "vague_city_county_or_jurisdiction", detail, city, query
    if re.search(r"\b(block|near|vicinity|behind|across from|area of)\b", detail, re.I):
        return "approximate_location_not_resolved", detail, city, query
    if re.search(r"\s+(?:and|&)\s+|\s*/\s*|\s+at\s+", detail, re.I):
        return "intersection", detail, city, query
    if re.match(r"^\d+[A-Za-z]?\s+\S", detail):
        return "numbered_address", detail, city, query
    return "street_only_or_landmark_not_resolved", detail, city, query

def http_json(url, values=None):
    data = urllib.parse.urlencode(values).encode() if values is not None else None
    for attempt in range(4):
        try:
            request = urllib.request.Request(url, data=data, headers={"User-Agent": "AustinAnimal2024Research/1.0"})
            with urllib.request.urlopen(request, timeout=30) as response:
                result = json.load(response)
            if "error" in result:
                raise RuntimeError(result["error"])
            return result
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 ** (attempt + 1))

def request_batch(locations):
    records = []
    for index, location in enumerate(locations):
        kind, detail, city, query = classify(location)
        if kind == "intersection":
            query = re.sub(r"\s+and\s+|\s*/\s*|\s+at\s+", " & ", query, flags=re.I)
        records.append({"attributes": {"OBJECTID": index, "SingleLine": query}})
    result = http_json(SERVICE + "/geocodeAddresses", {
        "f": "json", "addresses": json.dumps({"records": records}),
        "outSR": "4326", "outFields": "*",
    })
    if result.get("spatialReference", {}).get("wkid") != 4326:
        raise RuntimeError("The geocoder did not return EPSG:4326 coordinates")
    candidates = result.get("locations", [])
    found = {int(x["attributes"]["ResultID"]): x for x in candidates}
    if len(candidates) != len(locations) or len(found) != len(candidates) or set(found) != set(range(len(locations))):
        raise RuntimeError("Geocoder omitted or duplicated a request result")
    timestamp = datetime.now(timezone.utc).isoformat()
    return {location: {"query": records[i]["attributes"]["SingleLine"],
                       "retrieved_at_utc": timestamp, "response": found[i]}
            for i, location in enumerate(locations)}

def validate_result(location, entry):
    kind, detail, city, query = classify(location)
    candidate = entry["response"]
    attrs = candidate.get("attributes", {})
    status = attrs.get("Status", "")
    address_type = attrs.get("Addr_type", "")
    score = float(candidate.get("score", 0))
    matched = candidate.get("address", "")
    x, y = candidate.get("location", {}).get("x"), candidate.get("location", {}).get("y")
    row = {"found_location": location, "geocode_query": entry["query"],
           "is_location_valid": False, "exclusion_reason": "", "latitude": "", "longitude": "",
           "latitude_min": "", "latitude_max": "", "longitude_min": "", "longitude_max": "",
           "location_precision": "", "geocode_match_address": matched,
           "geocode_score": score, "geocode_status": status, "geocode_address_type": address_type,
           "coordinate_source": SERVICE, "geocode_retrieved_at_utc": entry["retrieved_at_utc"]}
    if kind not in {"numbered_address", "intersection"}:
        row["exclusion_reason"] = "input_not_specific_address_or_intersection"
    elif status != "M":
        row["exclusion_reason"] = "ambiguous_match" if status == "T" else "unmatched"
    elif not math.isfinite(score) or not MIN_SCORE <= score <= 100:
        row["exclusion_reason"] = "score_below_95"
    elif address_type not in ALLOWED_TYPES:
        row["exclusion_reason"] = "match_not_address_or_intersection"
    elif kind == "intersection" and address_type != "StreetInt":
        row["exclusion_reason"] = "intersection_not_matched_as_intersection"
    elif kind == "numbered_address" and address_type == "StreetInt":
        row["exclusion_reason"] = "address_not_matched_as_address"
    elif not (isinstance(x, (int, float)) and isinstance(y, (int, float)) and math.isfinite(x) and math.isfinite(y) and -98.6 <= x <= -96.9 and 29.6 <= y <= 31.2):
        row["exclusion_reason"] = "coordinates_outside_austin_region"
    elif kind == "numbered_address" and (
        not re.match(r"^\d+[A-Za-z]?\b", matched)
        or re.match(r"^\d+[A-Za-z]?\b", detail).group().upper() != re.match(r"^\d+[A-Za-z]?\b", matched).group().upper()
    ):
        row["exclusion_reason"] = "house_number_mismatch"
    elif street_consistency_reason(detail, matched, kind):
        row["exclusion_reason"] = street_consistency_reason(detail, matched, kind)
    else:
        row.update(is_location_valid=True, latitude=y, longitude=x,
                   location_precision={"PointAddress": "address_point", "Subaddress": "subaddress_point",
                                       "StreetAddress": "street_address_interpolated", "StreetInt": "street_intersection"}[address_type])
    return row

def geocode_locations(locations, base=BASE, workers=1, offline=False):
    base = Path(base)
    cache_path = base / "geocoder_cache.json"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    unique = sorted(set(locations))
    needed = [x for x in unique if classify(x)[0] in {"intersection", "numbered_address"} and x not in cache]
    if offline and needed:
        raise RuntimeError(f"Offline cache is missing {len(needed)} address/intersection queries. Run without --offline to query the official locator.")
    print(f"Unique locations: {len(unique)}; uncached address/intersection queries: {len(needed)}", flush=True)
    batches = [needed[i:i + BATCH_SIZE] for i in range(0, len(needed), BATCH_SIZE)]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(request_batch, batch) for batch in batches]
        for count, future in enumerate(as_completed(futures), 1):
            cache.update(future.result())
            temp = cache_path.with_suffix(".tmp")
            temp.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
            temp.replace(cache_path)
            print(f"Geocoded batch {count}/{len(batches)}; cached locations={len(cache)}", flush=True)
    results = {}
    for location in unique:
        if classify(location)[0] in {"intersection", "numbered_address"}:
            results[location] = validate_result(location, cache[location])
        else:
            results[location] = {"found_location": location, "is_location_valid": False,
                                 "exclusion_reason": classify(location)[0]}
    return results
