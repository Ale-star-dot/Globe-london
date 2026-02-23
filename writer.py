"""
Writer
=======
Takes the cleaned, geocoded list of events and writes events-data.js
in the exact format the Globe frontend expects.
"""

import json
from datetime import datetime, timezone
from pathlib import Path


def write_events_js(events: list, output_path: Path) -> None:
    """Write the events list as a JavaScript file."""

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Build JS array entries
    entries = []
    for ev in events:
        entry = f"""  {{
    id: {ev['id']},
    type: "{ev['type']}", label: "{ev['label']}",
    title: {json.dumps(ev['title'])},
    artist: {json.dumps(ev.get('artist', ''))},
    venue: {json.dumps(ev['venue'])},
    address: {json.dumps(ev.get('address', ev['venue']))},
    lat: {ev.get('lat') or 'null'}, lng: {ev.get('lng') or 'null'},
    time: {json.dumps(ev.get('time', 'See website'))},
    date: {json.dumps(ev.get('date', 'Today'))},
    price: {json.dumps(ev.get('price', 'Free entry'))},
    priceNum: {ev.get('priceNum', 0)},
    description: {json.dumps(ev.get('description', ''))},
    url: {json.dumps(ev.get('url', ''))},
    highlight: {str(ev.get('highlight', False)).lower()},
    sponsored: {str(ev.get('sponsored', False)).lower()},
  }}"""
        entries.append(entry)

    js = f"""// ─────────────────────────────────────────────────────────────────
//  Globe — Auto-generated Events Data
//  Last updated: {now}
//  Source: Eventbrite · Designmynight · Time Out · Resident Advisor
//  DO NOT EDIT MANUALLY — this file is overwritten every hour
// ─────────────────────────────────────────────────────────────────

const GLOBE_EVENTS = [
{",\n".join(entries)}
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
