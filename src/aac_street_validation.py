"""Check that a high geocoder score did not silently change the input street.

This supplements, rather than replaces, locator score/status and house-number
checks. Common suffixes, explicit aliases and small spelling errors are allowed.
An empty return value means no material street conflict was detected; it is not
an independent guarantee that a geocode is correct.
"""
from difflib import SequenceMatcher
from itertools import permutations
import re

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
    text = re.sub(r"\b(UNIT|APT|APARTMENT|LOT|BUILDING|BLDG|BLD|STE|SUITE|TRLR)(?=\b|\d)\s*\w*.*", "", text)
    text = re.sub(r"\bSIDE\s+[A-Z]\b.*", "", text)
    text = re.sub(r"\b(?:NORTH|N)\s+LOOP\b", "NORTHLOOP", text)
    text = re.sub(r"\bDOG PARK\b.*", "", text)
    text = re.sub(r"\bAUSTIN(?:\s+TX)?(?:\s+\d{5})?\s*$", "", text)
    text = re.sub(r"\s+\d{5}\s*$", "", text)
    text = re.sub(r"\b(\d+)(?:ST|ND|RD|TH)\b", r"\1", text)
    return text.strip()


def _street(text, strip_house=False):
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
    if postfix in {"N", "S", "E", "W"} and len(tokens) > 1 and (tokens[-2] in _SUFFIXES or any(t in tokens for t in {"IH", "US", "FM", "RM", "SH", "HWY", "HIGHWAY"})):
        if any(t in tokens for t in {"IH", "US", "FM", "RM", "SH", "HWY", "HIGHWAY"}):
            bounds.add(postfix + "B")
        elif not prefix:
            prefix = postfix
        tokens = tokens[:-1]
    # Units or comments sometimes follow a fully spelled-out street suffix.
    # Preserve route numbers after HWY, and inspect directions before trimming.
    for i, token in enumerate(tokens):
        if token in {"ST", "STREET", "RD", "ROAD", "DR", "DRIVE", "LN", "LANE", "BLVD", "BOULEVARD", "AVE", "AVENUE", "CIR", "CIRCLE", "CT", "COURT", "CV", "COVE", "TRL", "TRAIL"} and i > 0:
            following = tokens[i + 1:]
            if following and (following[0].isdigit() or re.fullmatch(r"[A-Z]\d+", following[0]) or any(t in following for t in {"SCHOOL", "HS", "PARKING", "FLOOR", "ROCKS", "TX"})):
                tokens = tokens[:i + 1]
                break
    # Keep alternate forms before dropping suffixes: RIDGE POINT DR and
    # RIDGEPOINT DR, or COPPER BEND BLVD and COPPERBEND BLVD, are equivalent.
    full = [_SUFFIX_EQUIVALENTS.get(t, t) for t in tokens if t not in {"NB", "SB", "EB", "WB", "OF", "THE", "JR"}]
    forms = {"".join(full)}
    while full and (full[-1] in _SUFFIXES or full[-1] in {"A", "B", "C", "D"}):
        # Do not mistake Avenue A for a unit designation.
        if full[-1] in {"A", "B", "C", "D"} and len(full) >= 2 and full[-2] == "AVE":
            break
        full = full[:-1]
        forms.add("".join(full))
    tokens = [t for t in tokens if t not in _SUFFIXES and t not in {"NB", "SB", "EB", "WB", "OF", "THE", "JR"}]
    numbers = set(re.findall(r"\d+", " ".join(tokens)))
    return {"prefix": prefix, "bounds": bounds, "tokens": tokens,
            "core": "".join(tokens), "forms": forms, "numbers": numbers, "half": "HALF" in tokens}


def _pair_reason(source, target):
    if source["prefix"] and target["prefix"] and source["prefix"] != target["prefix"]:
        return "street_direction_mismatch"
    if any(a in source["bounds"] and b in target["bounds"] for a, b in (("NB", "SB"), ("SB", "NB"), ("EB", "WB"), ("WB", "EB"))):
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
    if expanded[source["prefix"]] + left == right or left == expanded[target["prefix"]] + right:
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
    for reason in ("fractional_street_mismatch", "street_direction_mismatch", "street_or_highway_number_mismatch"):
        if reason in reasons:
            return reason
    return "street_name_mismatch"
