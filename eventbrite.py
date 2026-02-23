"""
Eventbrite London Art Events — Official API
=============================================
Uses Eventbrite's official search API.
Requires a free API key from https://www.eventbrite.com/platform/api-key

Set the environment variable EVENTBRITE_API_KEY in your GitHub repo secrets.
"""

import os
import requests
from datetime import datetime, timedelta, timezone

API_BASE = "https://www.eventbriteapi.com/v3"

# Eventbrite category ID 105 = Arts
ART_CATEGORY_ID = "105"

HEADERS = {
    "Authorization": f"Bearer {os.environ.get('EVENTBRITE_API_KEY', '')}",
}

TYPE_KEYWORDS = {
    "gallery":     ["gallery", "private view", "opening night", "vernissage", "preview"],
    "exhibition":  ["exhibition", "exhibit", "show", "retrospective", "survey"],
    "popup":       ["pop-up", "popup", "market", "fair", "open studios"],
    "performance": ["performance", "dance", "live art", "durational", "theatre"],
    "talk":        ["talk", "lecture", "conversation", "workshop", "panel", "screening"],
}


def scrape_eventbrite(max_pages=5):
    api_key = os.environ.get("EVENTBRITE_API_KEY", "")
    if not api_key:
        print("  Eventbrite: no API key set — skipping")
        return []

    events = []
    today = datetime.now(timezone.utc)
    end   = today + timedelta(days=7)

    params = {
        "location.address":       "London, UK",
        "location.within":        "30km",
        "categories":             ART_CATEGORY_ID,
        "start_date.range_start": today.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "start_date.range_end":   end.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "expand":                 "venue,ticket_classes",
        "page_size":              50,
    }

    for page in range(1, max_pages + 1):
        params["page"] = page
        try:
            resp = requests.get(
                f"{API_BASE}/events/search/",
                headers=HEADERS,
                params=params,
                timeout=20,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  Eventbrite API error page {page}: {e}")
            break

        for item in data.get("events", []):
            ev = parse_event(item)
            if ev:
                events.append(ev)

        if not data.get("pagination", {}).get("has_more_items"):
            break

    return events


def parse_event(item):
    try:
        title = item.get("name", {}).get("text", "")
        if not title:
            return None

        desc = item.get("description", {}).get("text", "") or ""
        event_type = classify_type(title + " " + desc)

        venue = item.get("venue", {}) or {}
        address_obj = venue.get("address", {}) or {}
        venue_name = venue.get("name", "London")
        addr_str = address_obj.get("localized_address_display", venue_name)
        lat = venue.get("latitude")
        lng = venue.get("longitude")

        start = item.get("start", {}).get("utc", "")
        end   = item.get("end",   {}).get("utc", "")
        date_str = format_date(start)
        time_str = format_time(start, end)

        tickets = item.get("ticket_classes", []) or []
        prices  = [float(t["cost"]["major_value"]) for t in tickets
                   if t.get("cost") and not t.get("free")]
        price_num = min(prices) if prices else 0
        price_str = f"£{price_num:.0f}" if price_num else "Free entry"

        return {
            "source":      "eventbrite",
            "source_id":   item.get("id", ""),
            "type":        event_type,
            "label":       get_label(event_type),
            "title":       title,
            "artist":      "",
            "venue":       venue_name,
            "address":     addr_str,
            "lat":         float(lat) if lat else None,
            "lng":         float(lng) if lng else None,
            "time":        time_str,
            "date":        date_str,
            "price":       price_str,
            "priceNum":    price_num,
            "description": desc[:300],
            "url":         item.get("url", ""),
            "highlight":   False,
            "sponsored":   False,
        }
    except Exception as e:
        print(f"  Eventbrite parse error: {e}")
        return None


def classify_type(text):
    t = text.lower()
    for event_type, keywords in TYPE_KEYWORDS.items():
        if any(kw in t for kw in keywords):
            return event_type
    return "exhibition"

def get_label(event_type):
    return {"gallery":"Gallery Opening","exhibition":"Exhibition","popup":"Pop-up & Market",
            "performance":"Performance","talk":"Artist Talk"}.get(event_type,"Event")

def format_date(iso_str):
    if not iso_str: return "Today"
    try:
        dt    = datetime.fromisoformat(iso_str.replace("Z","+00:00"))
        today = datetime.now(timezone.utc).date()
        delta = (dt.date()-today).days
        if delta==0: return "Today"
        if delta==1: return "Tomorrow"
        return dt.strftime("%-d %b")
    except: return "Upcoming"

def format_time(start, end):
    try:
        s = datetime.fromisoformat(start.replace("Z","+00:00"))
        if end:
            e = datetime.fromisoformat(end.replace("Z","+00:00"))
            return f"{s.strftime('%H:%M')} – {e.strftime('%H:%M')}"
        return s.strftime("%H:%M")
    except: return "See website"
