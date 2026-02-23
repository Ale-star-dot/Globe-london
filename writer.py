"""
Writer
=======
Takes the cleaned, geocoded list of events and writes events-data.js
in the exact format the Globe frontend expects.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

# Derive display fields from scraped type/price data
TYPE_CONFIG = {
    "gallery":     {"color": "#C8102E", "tag": "Gallery Opening",  "tagClass": "tag-opening",    "category": "opening"},
    "exhibition":  {"color": "#D4A020", "tag": "Exhibition",        "tagClass": "tag-exhibition",  "category": "exhibition"},
    "popup":       {"color": "#1C6B3A", "tag": "Pop-up & Market",   "tagClass": "tag-popup",       "category": "popup"},
    "performance": {"color": "#6B3FA0", "tag": "Performance",       "tagClass": "tag-performance", "category": "performance"},
    "talk":        {"color": "#2A5BAD", "tag": "Artist Talk",       "tagClass": "tag-talk",        "category": "talk"},
}

def derive_booking_type(ev):
    price_num = ev.get("priceNum", 0)
    price_str = ev.get("price", "").lower()
    if price_num == 0 or "free" in price_str:
        if "rsvp" in price_str or "rsvp" in ev.get("title", "").lower():
            return "rsvp"
        return "free"
    return "paid"

def derive_neighbourhood(ev):
    """Rough neighbourhood from lat/lng."""
    lat = ev.get("lat") or 0
    lng = ev.get("lng") or 0
    if lat < 51.47:                      return "south-london"
    if lng < -0.17:                      return "west-end"
    if lng > -0.07 and lat > 51.51:      return "east-london"
    if lat > 51.53:                      return "north-london"
    if lat < 51.51 and lng > -0.12:      return "southbank"
    return "central-london"


def write_events_js(events: list, output_path: Path) -> None:
    """Write the events list as a JavaScript file."""

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    entries = []
    for ev in events:
        ev_type   = ev.get("type", "exhibition")
        cfg       = TYPE_CONFIG.get(ev_type, TYPE_CONFIG["exhibition"])
        price_num = ev.get("priceNum", 0)

        entry = f"""  {{
    id: {ev['id']},
    type: "{ev_type}",
    category: "{cfg['category']}",
    label: {json.dumps(ev.get('label', cfg['tag']))},
    tag: {json.dumps(cfg['tag'])},
    tagClass: "{cfg['tagClass']}",
    color: "{cfg['color']}",
    title: {json.dumps(ev['title'])},
    artist: {json.dumps(ev.get('artist', ''))},
    venue: {json.dumps(ev['venue'])},
    address: {json.dumps(ev.get('address', ev['venue']))},
    neighbourhood: "{derive_neighbourhood(ev)}",
    lat: {ev.get('lat') or 'null'}, lng: {ev.get('lng') or 'null'},
    time: {json.dumps(ev.get('time', 'See website'))},
    date: {json.dumps(ev.get('date', 'Today'))},
    price: {json.dumps(ev.get('price', 'Free entry'))},
    priceDisplay: {json.dumps(ev.get('price', 'Free entry'))},
    priceNum: {price_num},
    bookingType: "{derive_booking_type(ev)}",
    description: {json.dumps(ev.get('description', ''))},
    url: {json.dumps(ev.get('url', ''))},
    highlight: {str(ev.get('highlight', False)).lower()},
    sponsored: {str(ev.get('sponsored', False)).lower()},
  }}"""
        entries.append(entry)

    entries_joined = ",\n".join(entries)
    js = f"""// ─────────────────────────────────────────────────────────────────
//  Globe — Auto-generated Events Data
//  Last updated: {now}
//  Source: Eventbrite · Designmynight · Time Out · Resident Advisor
//  DO NOT EDIT MANUALLY — this file is overwritten daily
// ─────────────────────────────────────────────────────────────────

const GLOBE_EVENTS = [
{entries_joined}
];

// ── TYPE CONFIG: colours, icons, labels ──
const EVENT_TYPES = {{
  gallery:     {{ color: "#C8102E", icon: "🏛️", label: "Gallery Opening", markerColor: "#C8102E" }},
  exhibition:  {{ color: "#D4A020", icon: "🖼️", label: "Exhibition",      markerColor: "#D4A020" }},
  popup:       {{ color: "#1C6B3A", icon: "🛍️", label: "Pop-up & Market", markerColor: "#1C6B3A" }},
  performance: {{ color: "#6B3FA0", icon: "🎭", label: "Performance",     markerColor: "#6B3FA0" }},
  talk:        {{ color: "#2A5BAD", icon: "🎙️", label: "Artist Talk",     markerColor: "#2A5BAD" }},
}};
"""

    output_path.write_text(js, encoding="utf-8")
    print(f"Wrote {len(events)} events to {output_path}")
