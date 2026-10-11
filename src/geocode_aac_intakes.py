"""Geocode cleaned 2024 Austin Animal Center intake records.

Run: python src/geocode_aac_intakes.py
Input: data/processed/aac_intakes_clean.csv
Output: data/processed/aac_intakes_clean_geocoded.csv

Only accepted address/intersection points are exported, with the original
columns plus latitude, longitude, and location_precision. Counts are printed.
Saved API responses in .cache/ are optional local files, excluded from Git.

Source: City of Austin COA Locator, requested in WGS84 (EPSG:4326).
Coordinates describe reported locations, not observed animal GPS positions.
AI-assisted implementation; see the existing README for methods and limits.
"""

from datetime import datetime, timezone
from difflib import SequenceMatcher
import hashlib
from itertools import permutations
import json
import math
from pathlib import Path
import re
import time
import urllib.error
import urllib.parse
import urllib.request

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data/processed/aac_intakes_clean.csv"
OUTPUT_PATH = PROJECT_ROOT / "data/processed/aac_intakes_clean_geocoded.csv"
CACHE_PATH = PROJECT_ROOT / ".cache/geocoder_cache.json"
SERVICE = (
    "https://maps.austintexas.gov/arcgis/rest/services/Geocode/"
    "COA_Locator/GeocodeServer"
)
MIN_SCORE = 95.0
BATCH_SIZE = 250
PRECISIONS = {
    "PointAddress": "address_point",
    "Subaddress": "subaddress_point",
    "StreetAddress": "street_address_interpolated",
    "StreetInt": "street_intersection",
}
GEO_FIELDS = ["latitude", "longitude", "location_precision"]


_DIRECTIONS = {"NORTH": "N", "SOUTH": "S", "EAST": "E", "WEST": "W"}
_SUFFIXES = {
    "ST", "STREET", "RD", "ROAD", "DR", "DRIVE", "LN", "LANE",
    "BLVD", "BOULEVARD", "AVE", "AVENUE", "CIR", "CIRCLE", "CT", "COURT",
    "CV", "COVE", "TRL", "TRAIL", "PKWY", "PARKWAY", "PL", "PLACE",
    "TER", "TERRACE", "LOOP", "PASS", "BEND", "HOLLOW", "SKWY", "SKYWAY",
    "XING", "CROSSING", "PLZ", "PLAZA", "WAY", "PT", "POINT",
    "HWY", "HIGHWAY", "EXPY", "EXPRESSWAY", "SVRD", "SERVICE",
    "US", "IH", "SH", "FM", "RM", "INTERSTATE", "STATE",
    "BOULVARD", "BOULIVARD", "BOULEVARD", "AVANUE", "SREET", "STREEET",
    "DRVE", "DIRVE", "SRVRD",
    "BND", "HOLW", "LP", "WY", "TERR", "PATH", "BVLD", "ROADS", "EXPWY",
}
_SUFFIX_EQUIVALENTS = {
    "STREET": "ST", "ROAD": "RD", "DRIVE": "DR", "LANE": "LN",
    "BOULEVARD": "BLVD", "AVENUE": "AVE", "CIRCLE": "CIR", "COURT": "CT",
    "COVE": "CV", "TRAIL": "TRL", "PARKWAY": "PKWY", "PLACE": "PL",
    "TERRACE": "TER", "TERR": "TER", "LP": "LOOP", "BND": "BEND",
    "HOLW": "HOLLOW", "SKWY": "SKYWAY", "XING": "CROSSING", "PLZ": "PLAZA",
    "WY": "WAY", "PT": "POINT", "HIGHWAY": "HWY", "EXPRESSWAY": "EXPY",
    "EXPWY": "EXPY", "SRVRD": "SVRD", "ROADS": "RD", "BVLD": "BLVD",
}
_ORDINALS = {
    "FIRST": "1ST", "SECOND": "2ND", "THIRD": "3RD", "FOURTH": "4TH",
    "FIFTH": "5TH", "SIXTH": "6TH", "SEVENTH": "7TH", "EIGHTH": "8TH",
    "NINTH": "9TH", "TENTH": "10TH", "ELEVENTH": "11TH", "TWELFTH": "12TH",
    "THIRTEENTH": "13TH", "FOURTEENTH": "14TH", "FIFTEENTH": "15TH",
    "SIXTEENTH": "16TH", "SEVENTEENTH": "17TH", "EIGHTEENTH": "18TH",
    "NINETEENTH": "19TH", "TWENTIETH": "20TH",
}


def _prepare(text):
    """Return uppercase street text with known aliases and abbreviations."""
    text = text.upper().replace("\u00bd", " HALF ")
    text = re.sub(r"\b(?:AND\s+)?ONE\s+HALF\b|\b1\s*/\s*2\b", " HALF ", text)
    for before, after in {
        "FIFTY FIRST": "51ST", "FIFTY SECOND": "52ND",
        "TWENTY EIGHTH": "28TH", "TWENTY NINTH": "29TH",
        "MANCHACA": "MENCHACA", "MLK": "MARTIN LUTHER KING JR",
        "M L K": "MARTIN LUTHER KING JR", "MO PAC": "MOPAC",
        "SAINT": "ST", "NORTHBOUND": "NB", "SOUTHBOUND": "SB",
        "EASTBOUND": "EB", "WESTBOUND": "WB", "NORTH BOUND": "NB",
        "SOUTH BOUND": "SB", "EAST BOUND": "EB", "WEST BOUND": "WB",
        "EXPRESS WAY": "EXPY", "SERVICE ROAD": "SVRD",
        "I H": "IH", "F M": "FM", "R M": "RM", "U S": "US",
        "ROBERT MARTINEZ": "ROBERT T MARTINEZ JR",
    }.items():
        text = re.sub(r"\b" + re.escape(before) + r"\b", after, text)
    for before, after in _ORDINALS.items():
        text = re.sub(r"\b" + before + r"\b", after, text)
    # IH35, FM812, etc. are highway identifiers, not distinct street names.
    text = re.sub(r"\b(IH|FM|RM|US|SH)(\d)", r"\1 \2", text)
    text = re.sub(
        r"\b(UNIT|APT|APARTMENT|LOT|BUILDING|BLDG|BLD|STE|SUITE|TRLR)"
        r"(?=\b|\d)\s*\w*.*", "", text,
    )
    text = re.sub(r"\bSIDE\s+[A-Z]\b.*", "", text)
    text = re.sub(r"\b(?:NORTH|N)\s+LOOP\b", "NORTHLOOP", text)
    text = re.sub(r"\bDOG PARK\b.*", "", text)
    text = re.sub(r"\bAUSTIN(?:\s+TX)?(?:\s+\d{5})?\s*$", "", text)
    text = re.sub(r"\s+\d{5}\s*$", "", text)
    text = re.sub(r"\b(\d+)(?:ST|ND|RD|TH)\b", r"\1", text)
    return text.strip()


def _street(text, strip_house=False):
    """Return street-name forms, directions, and numbers used for comparison."""
    # A source intersection can also contain a leading house number.
    text = text.strip()
    if strip_house:
        text = re.sub(r"^\d+[A-Z]?\s+(?:[ABCD]\s+)?", "", text)
    else:
        match = re.match(r"^\d{3,}\s+([A-Z]+)\b", text)
        if match and match.group(1) not in _SUFFIXES:
            text = re.sub(r"^\d+\s+", "", text)
    text = re.sub(r"\b\d+(?:ST|ND|RD|TH)?\s+FLOOR\b.*", "", text)
    tokens = re.findall(r"[A-Z0-9]+", text)
    tokens = [t for t in tokens if not re.fullmatch(r"[A-Z]\d+", t)]
    bounds = set(tokens) & {"NB", "SB", "EB", "WB"}
    prefix = _DIRECTIONS.get(tokens[0], tokens[0]) if tokens else ""
    if prefix not in {"N", "S", "E", "W"}:
        prefix = ""
    # A standalone NORTH/SOUTH is a street name, not a directional qualifier.
    if prefix and len(tokens) == 1:
        prefix = ""
    if prefix:
        tokens = tokens[1:]
    postfix = _DIRECTIONS.get(tokens[-1], tokens[-1]) if tokens else ""
    is_highway = any(
        token in {"IH", "US", "FM", "RM", "SH", "HWY", "HIGHWAY"}
        for token in tokens
    )
    if (
        postfix in {"N", "S", "E", "W"} and len(tokens) > 1
        and (tokens[-2] in _SUFFIXES or is_highway)
    ):
        if is_highway:
            bounds.add(postfix + "B")
        elif not prefix:
            prefix = postfix
        tokens = tokens[:-1]
    # Units or comments sometimes follow a fully spelled-out street suffix.
    # Preserve route numbers after HWY, and inspect directions before trimming.
    for i, token in enumerate(tokens):
        if token in {
            "ST", "STREET", "RD", "ROAD", "DR", "DRIVE", "LN", "LANE",
            "BLVD", "BOULEVARD", "AVE", "AVENUE", "CIR", "CIRCLE",
            "CT", "COURT", "CV", "COVE", "TRL", "TRAIL",
        } and i > 0:
            following = tokens[i + 1:]
            if following and (
                following[0].isdigit()
                or re.fullmatch(r"[A-Z]\d+", following[0])
                or any(
                    t in {"SCHOOL", "HS", "PARKING", "FLOOR", "ROCKS", "TX"}
                    for t in following
                )
            ):
                tokens = tokens[:i + 1]
                break
    # Keep alternate forms before dropping suffixes: RIDGE POINT DR and
    # RIDGEPOINT DR, or COPPER BEND BLVD and COPPERBEND BLVD, are equivalent.
    full = [
        _SUFFIX_EQUIVALENTS.get(t, t) for t in tokens
        if t not in {"NB", "SB", "EB", "WB", "OF", "THE", "JR"}
    ]
    forms = {"".join(full)}
    while full and (full[-1] in _SUFFIXES or full[-1] in {"A", "B", "C", "D"}):
        # Do not mistake Avenue A for a unit designation.
        if full[-1] in {"A", "B", "C", "D"} and len(full) >= 2 and full[-2] == "AVE":
            break
        full = full[:-1]
        forms.add("".join(full))
    tokens = [
        t for t in tokens
        if t not in _SUFFIXES and t not in {"NB", "SB", "EB", "WB", "OF", "THE", "JR"}
    ]
    numbers = set(re.findall(r"\d+", " ".join(tokens)))
    return {
        "prefix": prefix, "bounds": bounds, "tokens": tokens,
        "core": "".join(tokens), "forms": forms,
        "numbers": numbers, "half": "HALF" in tokens,
    }


def _pair_reason(source, target):
    """Compare parsed streets and return a conflict label, or an empty string."""
    if source["prefix"] and target["prefix"] and source["prefix"] != target["prefix"]:
        return "street_direction_mismatch"
    if any(
        a in source["bounds"] and b in target["bounds"]
        for a, b in (("NB", "SB"), ("SB", "NB"), ("EB", "WB"), ("WB", "EB"))
    ):
        return "street_direction_mismatch"
    if source["half"] != target["half"]:
        return "fractional_street_mismatch"
    if source["numbers"] != target["numbers"]:
        return "street_or_highway_number_mismatch"
    left, right = source["core"], target["core"]
    if left == right:
        return ""
    if (source["forms"] & target["forms"]) - {""}:
        return ""
    # Direction words can belong to a compound street name (Northcross,
    # Southwest). Restore the prefix only when it produces an exact match.
    expanded = {"N": "NORTH", "S": "SOUTH", "E": "EAST", "W": "WEST", "": ""}
    if (
        expanded[source["prefix"]] + left == right
        or left == expanded[target["prefix"]] + right
    ):
        return ""
    if not left or not right:
        return "street_name_mismatch"
    # Reject loss/addition of an entire substantive word even when the
    # remaining long street name would still have a high overall similarity.
    ls, rs = set(source["tokens"]), set(target["tokens"])
    if (ls < rs or rs < ls) and left != right:
        return "street_name_mismatch"
    if SequenceMatcher(None, left, right).ratio() < 0.85:
        return "street_name_mismatch"
    return ""


def street_consistency_reason(detail, matched_address, kind):
    """Return an exclusion reason, or '' when street information is consistent."""
    source = _prepare(detail)
    target = _prepare(matched_address.split(",", 1)[0])
    if kind != "intersection":
        return _pair_reason(_street(source, True), _street(target, True))
    split = r"\s+(?:AND|AT|&)\s+|\s*/\s*"
    left = [_street(s) for s in re.split(split, source)]
    right = [_street(s) for s in re.split(split, target)]
    if len(left) != 2 or len(right) != 2:
        return "intersection_street_names_not_resolved"
    reasons = []
    for permutation in permutations(right):
        pair_reasons = [_pair_reason(a, b) for a, b in zip(left, permutation)]
        if not any(pair_reasons):
            return ""
        reasons.extend(r for r in pair_reasons if r)
    # Prefer a specific explanation when a valid street pairing exposed one.
    for reason in (
        "fractional_street_mismatch", "street_direction_mismatch",
        "street_or_highway_number_mismatch",
    ):
        if reason in reasons:
            return reason
    return "street_name_mismatch"


def split_location(location):
    """Return address detail, source city/county label, and an API query."""
    text = location.strip()
    match = re.match(r"^(.*?)\s+in\s+(.+?)\s*\(TX\)\s*$", text, re.I)
    if match:
        detail, city = match.groups()
        # Travis is a county in this dataset, not a city named Travis.
        if city.lower() in {"travis", "travis county"}:
            query = f"{detail}, TX"
        else:
            query = f"{detail}, {city}, TX"
        return detail.strip(), city.strip(), query
    return text, "", re.sub(r"\s*\(TX\)\s*$", ", TX", text, flags=re.I)


def classify(location):
    """Return the location kind, address detail, city label, and query."""
    detail, city, query = split_location(location)
    if not detail:
        kind = "missing_location"
    elif (
        re.fullmatch(r"[^()]+\s*\(TX\)", location.strip(), re.I) and not city
    ) or re.search(
        r"^(outside jurisdiction|unknown|not given|none|n/?a)$", detail, re.I
    ):
        kind = "vague_city_county_or_jurisdiction"
    elif re.search(
        r"\b(block|near|vicinity|behind|across from|area of)\b", detail, re.I
    ):
        kind = "approximate_location_not_resolved"
    elif re.search(r"\s+(?:and|&)\s+|\s*/\s*|\s+at\s+", detail, re.I):
        kind = "intersection"
    elif re.match(r"^\d+[A-Za-z]?\s+\S", detail):
        kind = "numbered_address"
    else:
        kind = "street_only_or_landmark_not_resolved"
    return kind, detail, city, query


def http_json(url, values):
    """POST parameters to a URL and return JSON, retrying temporary failures."""
    data = urllib.parse.urlencode(values).encode()
    for attempt in range(4):
        try:
            request = urllib.request.Request(
                url, data=data,
                headers={"User-Agent": "AustinAnimal2024Research/1.0"},
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                result = json.load(response)
            if "error" in result:
                raise RuntimeError(result["error"])
            return result
        except (urllib.error.URLError, TimeoutError, RuntimeError):
            if attempt == 3:
                raise
            time.sleep(2 ** (attempt + 1))


def request_batch(locations):
    """Return official responses keyed by location, checking IDs and CRS."""
    records = []
    for index, location in enumerate(locations):
        kind, _, _, query = classify(location)
        if kind == "intersection":
            query = re.sub(
                r"\s+and\s+|\s*/\s*|\s+at\s+", " & ", query, flags=re.I
            )
        records.append({"attributes": {"OBJECTID": index, "SingleLine": query}})
    result = http_json(SERVICE + "/geocodeAddresses", {
        "f": "json", "addresses": json.dumps({"records": records}),
        "outSR": "4326", "outFields": "*",
    })
    if result.get("spatialReference", {}).get("wkid") != 4326:
        raise RuntimeError("The geocoder did not return EPSG:4326 coordinates.")
    candidates = result.get("locations", [])
    found = {int(item["attributes"]["ResultID"]): item for item in candidates}
    if (
        len(candidates) != len(locations)
        or len(found) != len(candidates)
        or set(found) != set(range(len(locations)))
    ):
        raise RuntimeError("Geocoder omitted or duplicated a request result.")
    timestamp = datetime.now(timezone.utc).isoformat()
    return {
        location: {
            "query": records[index]["attributes"]["SingleLine"],
            "retrieved_at_utc": timestamp,
            "response": found[index],
        }
        for index, location in enumerate(locations)
    }


def validate_result(location, entry):
    """Return the three coordinate fields for an accepted match, else None."""
    kind, detail, _, _ = classify(location)
    candidate = entry["response"]
    attributes = candidate.get("attributes", {})
    address_type = attributes.get("Addr_type", "")
    score = float(candidate.get("score", 0))
    matched = candidate.get("address", "")
    point = candidate.get("location", {})
    longitude, latitude = point.get("x"), point.get("y")
    if (
        kind not in {"numbered_address", "intersection"}
        or attributes.get("Status") != "M"
        or not math.isfinite(score)
        or not MIN_SCORE <= score <= 100
        or address_type not in PRECISIONS
        or (kind == "intersection") != (address_type == "StreetInt")
    ):
        return None
    # Use response.location, not attributes.X/Y (which may be projected feet).
    if not (
        isinstance(longitude, (int, float))
        and isinstance(latitude, (int, float))
        and math.isfinite(longitude)
        and math.isfinite(latitude)
        and -98.6 <= longitude <= -96.9
        and 29.6 <= latitude <= 31.2
    ):
        return None
    if kind == "numbered_address":
        source_number = re.match(r"^\d+[A-Za-z]?\b", detail)
        target_number = re.match(r"^\d+[A-Za-z]?\b", matched)
        if (
            not source_number or not target_number
            or source_number.group().upper() != target_number.group().upper()
        ):
            return None
    if street_consistency_reason(detail, matched, kind):
        return None
    return {
        "latitude": latitude,
        "longitude": longitude,
        "location_precision": PRECISIONS[address_type],
    }


def build_location_lookup(locations, cache_path):
    """Query unique addresses, reuse local responses, and return valid points."""
    cache_path = Path(cache_path)
    cache = (
        json.loads(cache_path.read_text(encoding="utf-8"))
        if cache_path.exists() else {}
    )
    candidates = sorted({
        value for value in locations
        if classify(value)[0] in {"numbered_address", "intersection"}
    })
    needed = [value for value in candidates if value not in cache]
    print(f"Unique locations to query: {len(needed):,}", flush=True)
    for start in range(0, len(needed), BATCH_SIZE):
        cache.update(request_batch(needed[start:start + BATCH_SIZE]))
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = cache_path.with_suffix(".tmp")
        try:
            temporary.write_text(
                json.dumps(cache, ensure_ascii=False), encoding="utf-8"
            )
            temporary.replace(cache_path)
        finally:
            temporary.unlink(missing_ok=True)
        print(
            f"Queried {min(start + BATCH_SIZE, len(needed)):,}"
            f"/{len(needed):,} locations", flush=True,
        )
    accepted = {}
    for location in candidates:
        point = validate_result(location, cache[location])
        if point is not None:
            accepted[location] = point
    return accepted


def run(input_path=INPUT_PATH, output_path=OUTPUT_PATH, cache_path=CACHE_PATH):
    """Read cleaned events, save accepted points to one CSV, and return counts."""
    input_path, output_path, cache_path = map(
        Path, (input_path, output_path, cache_path)
    )
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    paths = [
        input_path, output_path, temporary,
        cache_path, cache_path.with_suffix(".tmp"),
    ]
    if len({path.resolve() for path in paths}) != len(paths):
        raise ValueError("Input, output, cache, and temporary paths must differ.")
    input_hash = hashlib.sha256(input_path.read_bytes()).digest()
    intakes = pd.read_csv(input_path, dtype=str, keep_default_na=False)
    if not {"Animal ID", "Found Location"}.issubset(intakes.columns):
        raise ValueError("Input needs Animal ID and Found Location columns.")
    if set(GEO_FIELDS) & set(intakes.columns):
        raise ValueError("Use the cleaned input, not an already geocoded file.")
    if {"Intake Date", "Intake Time"}.issubset(intakes.columns):
        dates = pd.to_datetime(
            intakes["Intake Date"] + " " + intakes["Intake Time"],
            format="%Y-%m-%d %H:%M:%S", errors="raise",
        )
    elif "DateTime" in intakes.columns:
        dates = pd.to_datetime(intakes["DateTime"], errors="raise")
    else:
        raise ValueError("Input needs Intake Date and Intake Time, or DateTime.")
    if not ((dates >= "2024-01-01") & (dates < "2025-01-01")).all():
        raise ValueError("Input must contain only valid 2024 intake dates.")
    accepted = build_location_lookup(
        intakes["Found Location"].str.strip().tolist(), cache_path
    )
    records = []
    for original in intakes.to_dict(orient="records"):
        location = original["Found Location"].strip()
        if location in accepted:
            # Keep every accepted event in its original order, even duplicates.
            records.append({**original, **accepted[location]})
    output = pd.DataFrame(records, columns=[*intakes.columns, *GEO_FIELDS])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        output.to_csv(
            temporary, index=False, encoding="utf-8-sig", lineterminator="\n"
        )
        if hashlib.sha256(input_path.read_bytes()).digest() != input_hash:
            raise RuntimeError("Input changed during this run; please rerun.")
        temporary.replace(output_path)
    finally:
        temporary.unlink(missing_ok=True)
    counts = {
        "total_records": len(intakes),
        "successfully_located_records": len(output),
        "unsuccessfully_located_records": len(intakes) - len(output),
    }
    print(f"Total records: {counts['total_records']:,}")
    print(f"Successfully located records: {len(output):,}")
    print(f"Unsuccessfully located records: {len(intakes) - len(output):,}")
    print(f"Saved CSV: {output_path}")
    return counts


if __name__ == "__main__":
    run()
