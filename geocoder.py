"""
Geocoder
=========
Converts venue addresses to lat/lng coordinates.
Uses Nominatim (OpenStreetMap) — completely free, no API key needed.
Rate limit: 1 request/second (enforced in run.py).

Falls back to a hand-curated lookup of London's major art venues
so we never have to geocode the same place twice.
"""

import requests
import time

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

HEADERS = {
    "User-Agent": "Globe-Art-London/1.0 (art events aggregator; contact@globe.art)",
}

# ── Pre-cached coordinates for London's major art venues ──────────────────────
# Add more here to avoid API calls and speed up the scraper
VENUE_CACHE = {
    # Major institutions
    "tate modern":               (51.5076, -0.0994),
    "tate britain":              (51.4912, -0.1276),
    "national gallery":          (51.5088, -0.1283),
    "national portrait gallery": (51.5096, -0.1285),
    "victoria and albert museum":(51.4966, -0.1722),
    "v&a":                       (51.4966, -0.1722),
    "british museum":            (51.5194, -0.1270),
    "royal academy of arts":     (51.5096, -0.1393),
    "barbican gallery":          (51.5202, -0.0944),
    "barbican centre":           (51.5202, -0.0944),
    "serpentine gallery":        (51.5053, -0.1759),
    "serpentine south":          (51.5052, -0.1759),
    "serpentine north":          (51.5055, -0.1762),
    "whitechapel gallery":       (51.5154, -0.0726),
    "ica":                       (51.5072, -0.1310),
    "ica london":                (51.5072, -0.1310),
    "hayward gallery":           (51.5054, -0.1144),
    "south london gallery":      (51.4710, -0.0643),
    "courtauld gallery":         (51.5113, -0.1166),
    "natural history museum":    (51.4967, -0.1764),
    "science museum":            (51.4977, -0.1746),
    "design museum":             (51.4997, -0.2013),
    "photographer's gallery":    (51.5148, -0.1386),
    "photographers gallery":     (51.5148, -0.1386),
    "newport street gallery":    (51.4921, -0.1143),
    "saatchi gallery":           (51.4897, -0.1594),

    # Commercial galleries
    "white cube bermondsey":     (51.4983, -0.0803),
    "white cube mason's yard":   (51.5072, -0.1370),
    "white cube masons yard":    (51.5072, -0.1370),
    "gagosian london":           (51.5303, -0.1138),
    "gagosian":                  (51.5303, -0.1138),
    "hauser & wirth":            (51.5102, -0.1416),
    "hauser and wirth":          (51.5102, -0.1416),
    "victoria miro":             (51.5318, -0.0988),
    "victoria miro mayfair":     (51.5124, -0.1455),
    "lisson gallery":            (51.5228, -0.1628),
    "sadie coles hq":            (51.5127, -0.1396),
    "frith street gallery":      (51.5118, -0.1378),
    "maureen paley":             (51.5265, -0.0671),
    "david zwirner london":      (51.5098, -0.1444),
    "david zwirner":             (51.5098, -0.1444),
    "sprüth magers":             (51.5097, -0.1449),
    "spruth magers":             (51.5097, -0.1449),
    "thomas dane gallery":       (51.5066, -0.1365),
    "pippy houldsworth gallery": (51.5123, -0.1405),
    "corvi-mora":                (51.4888, -0.1102),
    "hannah barry gallery":      (51.4719, -0.0655),
    "arcadia missa":             (51.4748, -0.0254),
    "camden arts centre":        (51.5494, -0.1858),
    "zabludowicz collection":    (51.5489, -0.1478),
    "ordovas gallery":           (51.5103, -0.1414),
    "simon lee gallery":         (51.5116, -0.1416),
    "stephen friedman gallery":  (51.5107, -0.1416),
    "marlborough gallery":       (51.5090, -0.1440),
    "michael werner gallery":    (51.5121, -0.1527),
    "peter doig gallery":        (51.5240, -0.0826),

    # Performance / music venues
    "royal festival hall":       (51.5051, -0.1162),
    "southbank centre":          (51.5054, -0.1148),
    "barbican":                  (51.5202, -0.0944),
    "sadler's wells":            (51.5293, -0.1062),
    "sadlers wells":             (51.5293, -0.1062),
    "roundhouse":                (51.5430, -0.1519),
    "bfi southbank":             (51.5061, -0.1145),
    "bethnal green working men's club": (51.5257, -0.0637),
    "rich mix":                  (51.5232, -0.0718),

    # Markets / pop-up venues
    "netil market":              (51.5404, -0.0573),
    "coal drops yard":           (51.5362, -0.1237),
    "exmouth market":            (51.5259, -0.1087),
    "brixton village":           (51.4619, -0.1143),
    "battersea evolution":       (51.4783, -0.1517),
    "peckham levels":            (51.4693, -0.0697),
    "goldsmiths":                (51.4747, -0.0368),
}


def geocode_address(address: str) -> tuple[float, float] | None:
    """
    Returns (lat, lng) for the given address string, or None if not found.
    Checks the venue cache first, then falls back to Nominatim.
    """
    # Check static cache (normalised key)
    key = address.lower().strip()
    for venue_key, coords in VENUE_CACHE.items():
        if venue_key in key or key in venue_key:
            return coords

    # Call Nominatim
    try:
        params = {
            "q":              address,
            "format":         "json",
            "limit":          1,
            "countrycodes":   "gb",
            "addressdetails": 0,
        }
        resp = requests.get(
            NOMINATIM_URL,
            params=params,
            headers=HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
    except Exception as e:
        print(f"  Geocode error for '{address}': {e}")

    return None
