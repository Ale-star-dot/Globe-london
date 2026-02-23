"""
Designmynight London Art Events
=================================
Uses their working search endpoint.
"""

import requests
from datetime import datetime, timedelta, timezone

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://www.designmynight.com/",
}

TYPE_KEYWORDS = {
    "gallery":     ["gallery", "opening", "private view", "vernissage"],
    "popup":       ["pop-up", "popup", "market", "fair", "open studios"],
    "performance": ["performance", "dance", "live", "concert", "theatre"],
    "talk":        ["talk", "lecture", "workshop", "screening", "panel"],
    "exhibition":  ["exhibition", "exhibit", "show", "museum", "art"],
}


def scrape_designmynight(days_ahead=7):
    events = []
    today  = datetime.now(timezone.utc)
    end    = today + timedelta(days=days_ahead)

    url    = "https://api.designmynight.com/v4/events"
    params = {
        "q":          "art",
        "location":   "London",
        "from":       today.strftime("%Y-%m-%d"),
        "to":         end.strftime("%Y-%m-%d"),
        "per_page":   100,
    }

    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        for item in data.get("payload", {}).get("results", []):
            ev = parse_event(item)
            if ev:
                events.append(ev)
    except Exception as e:
        print(f"  Designmynight error: {e}")

    return events


def parse_event(item):
    try:
        title = item.get("name") or item.get("title", "")
        if not title:
            return None

        venue      = item.get("venue", {}) or {}
        venue_name = venue.get("name", "London")
        address    = venue.get("address", {}) or {}
        addr_parts = [address.get("address1",""), address.get("postcode","")]
        addr_str   = ", ".join(p for p in addr_parts if p) or venue_name
        lat        = venue.get("latitude")
        lng        = venue.get("longitude")

        dates      = item.get("dates", [{}])
        first      = dates[0] if dates else {}
        start      = first.get("start","")
        end_dt     = first.get("end","")

        price_obj  = item.get("tickets",{}) or {}
        price_num  = price_obj.get("min_price", 0) or 0
        price_str  = f"£{price_num:.0f}" if price_num else "Free entry"

        desc       = item.get("description","") or ""
        if "<" in desc:
            import re
            desc = re.sub(r"<[^>]+>","",desc)

        event_type = classify_type(title+" "+desc)

        return {
            "source":      "designmynight",
            "source_id":   str(item.get("_id","")),
            "type":        event_type,
            "label":       get_label(event_type),
            "title":       title,
            "artist":      item.get("subtitle",""),
            "venue":       venue_name,
            "address":     addr_str,
            "lat":         float(lat) if lat else None,
            "lng":         float(lng) if lng else None,
            "time":        format_time(start, end_dt),
            "date":        format_date(start),
            "price":       price_str,
            "priceNum":    float(price_num),
            "description": desc[:300],
            "url":         item.get("url",""),
            "highlight":   item.get("featured", False),
            "sponsored":   False,
        }
    except Exception as e:
        print(f"  DMN parse error: {e}")
        return None


def classify_type(text):
    t = text.lower()
    for etype, kws in TYPE_KEYWORDS.items():
        if any(kw in t for kw in kws):
            return etype
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
        if delta<=7: return "This Week"
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
