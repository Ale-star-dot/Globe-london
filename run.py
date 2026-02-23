#!/usr/bin/env python3
"""
Globe Art Events Scraper — run.py
"""

import json, sys, time, logging, argparse
from datetime import datetime
from pathlib import Path

from venues_rss    import scrape_venues_rss
from eventbrite    import scrape_eventbrite
from designmynight import scrape_designmynight
from ra            import scrape_ra
from geocoder      import geocode_address
from writer        import write_events_js

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("globe")

ALLOWED_TYPES  = {"gallery", "exhibition", "popup", "performance", "talk"}
LONDON_BOUNDS  = {"lat_min": 51.28, "lat_max": 51.70, "lng_min": -0.51, "lng_max": 0.33}

def load_geocode_cache():
    p = Path(".geocode_cache.json")
    return json.loads(p.read_text()) if p.exists() else {}

def save_geocode_cache(cache):
    Path(".geocode_cache.json").write_text(json.dumps(cache, indent=2))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    log.info("Globe scraper starting — %s", datetime.now().strftime("%A %d %b %Y %H:%M"))

    raw_events = []

    # 1. Venue RSS feeds — most reliable, always run first
    log.info("Scraping venue RSS feeds …")
    try:
        rss_events = scrape_venues_rss()
        log.info("  → %d events from venue RSS", len(rss_events))
        raw_events.extend(rss_events)
    except Exception as e:
        log.error("  ✗ venue RSS failed: %s", e)

    # 2. RA GraphQL
    log.info("Scraping RA …")
    try:
        ra_events = scrape_ra()
        log.info("  → %d events from RA", len(ra_events))
        raw_events.extend(ra_events)
    except Exception as e:
        log.error("  ✗ RA failed: %s", e)

    # 3. Eventbrite official API (only if key set)
    log.info("Scraping Eventbrite …")
    try:
        eb_events = scrape_eventbrite()
        log.info("  → %d events from Eventbrite", len(eb_events))
        raw_events.extend(eb_events)
    except Exception as e:
        log.error("  ✗ Eventbrite failed: %s", e)

    # 4. Designmynight
    log.info("Scraping Designmynight …")
    try:
        dmn_events = scrape_designmynight()
        log.info("  → %d events from Designmynight", len(dmn_events))
        raw_events.extend(dmn_events)
    except Exception as e:
        log.error("  ✗ Designmynight failed: %s", e)

    log.info("Total raw: %d", len(raw_events))

    # 2. Geocode missing coords
    cache = load_geocode_cache()
    geocoded = []
    for ev in raw_events:
        if ev.get("lat") and ev.get("lng"):
            geocoded.append(ev)
            continue
        addr = ev.get("address") or ev.get("venue", "")
        if addr in cache:
            ev["lat"], ev["lng"] = cache[addr]
        else:
            result = geocode_address(addr + ", London, UK")
            if result:
                ev["lat"], ev["lng"] = result
                cache[addr] = result
                time.sleep(0.15)
            else:
                continue
        geocoded.append(ev)
    save_geocode_cache(cache)

    # 3. Filter to London bounds
    filtered = [
        ev for ev in geocoded
        if ev.get("type") in ALLOWED_TYPES
        and LONDON_BOUNDS["lat_min"] <= ev.get("lat", 0) <= LONDON_BOUNDS["lat_max"]
        and LONDON_BOUNDS["lng_min"] <= ev.get("lng", 0) <= LONDON_BOUNDS["lng_max"]
    ]

    # 4. Deduplicate
    seen, unique = set(), []
    for ev in filtered:
        key = (ev.get("title","").lower().strip(), ev.get("venue","").lower().strip())
        if key not in seen:
            seen.add(key)
            unique.append(ev)

    for i, ev in enumerate(unique, 1):
        ev["id"] = i

    log.info("Final: %d events", len(unique))

    # 5. Write
    output = Path("output/events-data.js")
    output.parent.mkdir(exist_ok=True)
    write_events_js(unique, output)

    if args.dry_run:
        log.info("Dry run — not deploying")
        return

if __name__ == "__main__":
    main()
