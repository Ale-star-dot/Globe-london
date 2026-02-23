"""
Designmynight London Art Events Scraper
=========================================
Designmynight is one of London's best curated event listing sites.
They have a public API (no key required for read access).

API docs: https://api.designmynight.com/v4/venues?type=art-gallery&location=london
"""

import requests
from datetime import datetime, timedelta

DMN_API_BASE = "https://api.designmynight.com/v4"

# Designmynight venue types relevant to us
ART_TYPES = [
    "art-gallery",
    "museum",
    "exhibition-space",
    "theatre",
    "arts-centre",
]

# Directly search their events endpoint
EVENTS_URL = f"{DMN_API_BASE}/events"

HEADERS = {
    "User-Agent": "Globe-Art-Scraper/1.0 (london art events aggregator)",
    "Accept": "application/json",
}

TYPE_MAP = {
    "art-gallery":       "gallery",
    "museum":            "exhibition",
    "exhibition-space":  "exhibition",
    "theatre":           "performance",
    "arts-centre":       "exhibition",
    "comedy-club":       None,  # exclude
    "bar":               None,  # exclude
}


def scrape_designmynight(days_ahead=7):
    events = []
    today = datetime.now()

    params = {
        "city":       "london",
        "category":   "art",
        "start_date": today.strftime("%Y-%m-%d"),
        "end_date":   (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d"),
        "per_page":   100,
        "page":       1,
    }

    while True:
        try:
            resp = requests.get(
                EVENTS_URL,
                params=params,
                headers=HEADERS,
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  Designmynight error: {e}")
            break

        items = data.get("payload", {}).get("results", [])
        if not items:
            break

        for item in items:
            ev = parse_dmn_event(item)
            if ev:
                events.append(ev)

        # Pagination
        if not data.get("payload", {}).get("has_more"):
            break
        params["page"] += 1

    return events


def parse_dmn_event(item):
    try:
        title = item.get("name") or item.get("title", "")
        if not title:
            return None

        venue = item.get("venue", {})
        venue_name = venue.get("name", "London")
        address    = venue.get("address", {})
        addr_str   = ", ".join(filter(None, [
            address.get("address1"),
            address.get("address2"),
            address.get("city", "London"),
            address.get("postcode"),
        ]))

        lat = venue.get("latitude")  or address.get("latitude")
        lng = venue.get("longitude") or address.get("longitude")
        if lat: lat = float(lat)
        if lng: lng = float(lng)

        # Dates
        dates = item.get("dates", [{}])
        first_date = dates[0] if dates else {}
        start_iso  = first_date.get("start")
        end_iso    = first_date.get("end")

        date_str  = format_date(start_iso)
        time_str  = format_time(start_iso, end_iso)

        # Pricing
        tickets   = item.get("tickets", {})
        min_price = tickets.get("min_price", 0)
        max_price = tickets.get("max_price", 0)
        if min_price == 0:
            price_str = "Free entry"
            price_num = 0
        elif max_price and max_price != min_price:
            price_str = f"£{min_price:.0f} – £{max_price:.0f}"
            price_num = min_price
        else:
            price_str = f"£{min_price:.0f}"
            price_num = min_price

        # Type
        tags       = [t.get("slug", "") for t in item.get("tags", [])]
        venue_type = venue.get("type", "")
        event_type = classify_dmn_type(tags, venue_type, title)
        if not event_type:
            return None  # skip non-art events

        description = item.get("description", "")
        if description:
            # Strip HTML tags
            from bs4 import BeautifulSoup
            description = BeautifulSoup(description, "lxml").get_text()[:200]

        return {
            "source":      "designmynight",
            "source_id":   str(item.get("_id", "")),
            "type":        event_type,
            "label":       get_label(event_type),
            "title":       title,
            "artist":      item.get("subtitle", ""),
            "venue":       venue_name,
            "address":     addr_str or venue_name,
            "lat":         lat,
            "lng":         lng,
            "time":        time_str,
            "date":        date_str,
            "price":       price_str,
            "priceNum":    price_num,
            "description": description.strip(),
            "url":         item.get("url", ""),
            "image":       item.get("image", {}).get("url", ""),
            "highlight":   item.get("featured", False),
            "sponsored":   False,
        }
    except Exception as e:
        print(f"  DMN parse error: {e}")
        return None


def classify_dmn_type(tags, venue_type, title):
    title_l = title.lower()
    tag_set  = set(tags)
    vtype    = TYPE_MAP.get(venue_type)

    # Explicit tag matches
    if "art-gallery"      in tag_set: return "gallery"
    if "exhibition"       in tag_set: return "exhibition"
    if "pop-up"           in tag_set: return "popup"
    if "performance"      in tag_set: return "performance"
    if "workshop"         in tag_set: return "talk"
    if "talk"             in tag_set: return "talk"

    # Title keywords
    kw_map = {
        "gallery":     ["gallery", "opening", "private view", "vernissage"],
        "popup":       ["pop-up", "market", "fair", "open studios"],
        "performance": ["performance", "dance", "live"],
        "talk":        ["talk", "lecture", "workshop", "screening"],
        "exhibition":  ["exhibition", "exhibit"],
    }
    for etype, kws in kw_map.items():
        if any(kw in title_l for kw in kws):
            return etype

    # Venue type fallback
    if vtype:
        return vtype

    return "exhibition"


def get_label(event_type):
    return {
        "gallery":     "Gallery Opening",
        "exhibition":  "Exhibition",
        "popup":       "Pop-up & Market",
        "performance": "Performance",
        "talk":        "Artist Talk",
    }.get(event_type, "Event")


def format_date(iso_str):
    if not iso_str:
        return "Today"
    try:
        dt    = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        today = datetime.now().date()
        delta = (dt.date() - today).days
        if delta == 0:  return "Today"
        if delta == 1:  return "Tomorrow"
        if delta <= 7:  return "This Week"
        return dt.strftime("%-d %b")
    except Exception:
        return "Upcoming"


def format_time(start_iso, end_iso):
    try:
        s = datetime.fromisoformat(start_iso.replace("Z", "+00:00"))
        if end_iso:
            e = datetime.fromisoformat(end_iso.replace("Z", "+00:00"))
            return f"{s.strftime('%H:%M')} – {e.strftime('%H:%M')}"
        return s.strftime("%H:%M")
    except Exception:
        return "See website"
