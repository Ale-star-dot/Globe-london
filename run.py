#!/usr/bin/env python3
"""
Globe Art Events Scraper — run.py
Scrapes London art events and deploys to Netlify.
"""

import json, sys, time, logging, argparse
from datetime import datetime
from pathlib import Path

from eventbrite    import scrape_eventbrite
from designmynight import scrape_designmynight
from timeout       import scrape_timeout
from ra            import scrape_ra
from geocoder      import geocode_address
from deployer      import deploy_to_netlify
from writer        import write_events_js

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("globe")

SOURCES = {
    "eventbrite":    scrape_eventbrite,
    "designmynight": scrape_designmynight,
    "timeout":       scrape_timeout,
    "ra":            scrape_ra,
}

ALLOWED_TYPES = {"gallery", "exhibition", "popup", "performance", "talk"}

LONDON_BOUNDS = {"lat_min": 51.28, "lat_max": 51.70, "lng_min": -0.51, "lng_max": 0.33}

def load_geocode_cache():
    p = Path(".geocode_cache.json")
    return json.loads(p.read_text()) if p.exists() else {}

def save_geocode_cache(cache):
    Path(".geocode_cache.json").write_text(json.dumps(cache, indent=2))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--source",  default=None, choices=list(SOURCES.keys()))
    args = parser.parse_args()

    log.info("Globe scraper starting — %s", datetime.now().strftime("%A %d %b %Y %H:%M"))

    # 1. Scrape
    raw_events = []
    sources_to_run = {args.source: SOURCES[args.source]} if args.source else SOURCES
    for name, fn in sources_to_run.items():
        log.info("Scraping %s …", name)
        try:
            events = fn()
            log.info("  → %d events from %s", len(events), name)
            raw_events.extend(events)
        except Exception as e:
            log.error("  ✗ %s failed: %s", name, e)

    log.info("Total raw: %d", len(raw_events))

    # 2. Geocode
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

    # 3. Filter
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

    # 6. Deploy
    log.info("Deploying …")
    try:
        deploy_to_netlify(output)
        log.info("✓ Done")
    except Exception as e:
        log.error("✗ Deploy failed: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
