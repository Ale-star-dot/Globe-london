"""
Resident Advisor — London Art/Performance Events
==================================================
RA has a GraphQL API used by their own frontend.
We query it for London events in art/gallery/performance categories.

RA is particularly good for:
  - Performance art
  - Sound art / AV events
  - Club-gallery crossovers
  - Artist DJ sets

Note: RA's GraphQL endpoint is public (same as their website uses).
Be polite — max 1 request per second.
"""

import json
import time
import requests
from datetime import datetime, timedelta

RA_GRAPHQL = "https://ra.co/graphql"

# RA area ID for London = 13
LONDON_AREA_ID = 13

# Query for events listing
EVENTS_QUERY = """
query GET_EVENTS($filters: FilterInputDtoInput, $pageSize: Int, $page: Int) {
  eventListings(
    filters: $filters
    pageSize: $pageSize
    page: $page
    sort: { attending: { priority: 1, order: DESCENDING } }
  ) {
    data {
      id
      event {
        id
        title
        date
        startTime
        endTime
        venue {
          name
          address
          area { name }
          lat
          lng
        }
        images { filename }
        artists { name }
        cost
        content
        tags { name }
      }
    }
    totalResults
  }
}
"""

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (compatible; GlobeArtScraper/1.0)",
    "Referer": "https://ra.co/",
}

# Tags we consider art events (RA is broader than just art)
ART_TAGS = {
    "art", "gallery", "performance", "live art", "audio visual", "av",
    "visual arts", "installation", "multimedia", "experimental",
    "noise", "ambient", "electronic", "club", "rave",
}

# Tags to exclude
EXCLUDE_TAGS = {"comedy", "sports", "food", "dating"}


def scrape_ra(days_ahead=3):
    events   = []
    today    = datetime.now()
    end_date = today + timedelta(days=days_ahead)

    variables = {
        "filters": {
            "areas":     {"eq": LONDON_AREA_ID},
            "listingDate": {
                "gte": today.strftime("%Y-%m-%d"),
                "lte": end_date.strftime("%Y-%m-%d"),
            },
        },
        "pageSize": 50,
        "page":     1,
    }

    while True:
        try:
            resp = requests.post(
                RA_GRAPHQL,
                json={"query": EVENTS_QUERY, "variables": variables},
                headers=HEADERS,
                timeout=20,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  RA error: {e}")
            break

        listings = (
            data.get("data", {})
                .get("eventListings", {})
                .get("data", [])
        )
        if not listings:
            break

        for listing in listings:
            event = listing.get("event", {})
            if not event:
                continue

            # Filter: only art-adjacent events
            tags = {t["name"].lower() for t in event.get("tags", [])}
            if tags & EXCLUDE_TAGS:
                continue
            # Must have at least one art tag, OR be in a gallery venue
            venue_name = event.get("venue", {}).get("name", "").lower()
            is_art = bool(tags & ART_TAGS) or any(
                kw in venue_name for kw in ["gallery", "museum", "institute", "centre", "tate", "ica"]
            )
            if not is_art:
                continue

            ev = parse_ra_event(event)
            if ev:
                events.append(ev)

        # Check if more pages
        total = data.get("data", {}).get("eventListings", {}).get("totalResults", 0)
        if variables["page"] * variables["pageSize"] >= total:
            break
        variables["page"] += 1
        time.sleep(0.5)

    return events


def parse_ra_event(event):
    try:
        title = event.get("title", "")
        if not title:
            return None

        venue      = event.get("venue", {})
        venue_name = venue.get("name", "London")
        address    = venue.get("address", venue_name)
        lat        = venue.get("lat")
        lng        = venue.get("lng")

        # Artists
        artists = [a["name"] for a in event.get("artists", [])]
        artist_str = ", ".join(artists[:3]) if artists else ""

        # Dates
        date_iso  = event.get("date", "")
        start_iso = event.get("startTime", "")
        end_iso   = event.get("endTime", "")
        date_str  = format_date(date_iso)
        time_str  = format_time(start_iso, end_iso)

        # Price
        cost     = event.get("cost", "")
        if not cost or cost.strip() in ("0", "0.00", "Free", ""):
            price_str = "Free entry"
            price_num = 0
        else:
            price_str = f"£{cost}" if not cost.startswith("£") else cost
            try:
                price_num = float(cost.replace("£", "").split("-")[0].strip())
            except Exception:
                price_num = 0

        # Description
        content = event.get("content", "") or ""
        from bs4 import BeautifulSoup
        description = BeautifulSoup(content, "lxml").get_text()[:200]

        # Type
        tags       = {t["name"].lower() for t in event.get("tags", [])}
        event_type = classify_ra_type(tags, title, venue_name)

        # Image
        images = event.get("images", [])
        image  = f"https://ra.co/{images[0]['filename']}" if images else ""

        return {
            "source":      "ra",
            "source_id":   str(event.get("id", "")),
            "type":        event_type,
            "label":       get_label(event_type),
            "title":       title,
            "artist":      artist_str,
            "venue":       venue_name,
            "address":     address,
            "lat":         float(lat) if lat else None,
            "lng":         float(lng) if lng else None,
            "time":        time_str,
            "date":        date_str,
            "price":       price_str,
            "priceNum":    price_num,
            "description": description.strip(),
            "url":         f"https://ra.co/events/{event.get('id', '')}",
            "image":       image,
            "highlight":   False,
            "sponsored":   False,
        }
    except Exception as e:
        print(f"  RA parse error: {e}")
        return None


def classify_ra_type(tags, title, venue):
    title_l = title.lower()
    venue_l = venue.lower()

    if "gallery"         in venue_l: return "gallery"
    if "live art"        in tags:    return "performance"
    if "performance"     in tags:    return "performance"
    if "audio visual"    in tags:    return "performance"
    if "opening"         in title_l: return "gallery"
    if "exhibition"      in title_l: return "exhibition"
    if "workshop"        in title_l: return "talk"
    if "talk"            in title_l: return "talk"
    if "screening"       in title_l: return "talk"
    return "performance"  # RA default is performance/club


def get_label(event_type):
    return {
        "gallery":     "Gallery Opening",
        "exhibition":  "Exhibition",
        "popup":       "Pop-up & Market",
        "performance": "Performance",
        "talk":        "Artist Talk",
    }.get(event_type, "Event")


def format_date(date_str):
    if not date_str:
        return "Today"
    try:
        dt    = datetime.fromisoformat(date_str[:10])
        today = datetime.now().date()
        delta = (dt - today).days
        if delta == 0:  return "Today"
        if delta == 1:  return "Tomorrow"
        return dt.strftime("%-d %b")
    except Exception:
        return "Upcoming"


def format_time(start, end):
    try:
        s = datetime.fromisoformat(start.replace("Z", "+00:00"))
        if end:
            e = datetime.fromisoformat(end.replace("Z", "+00:00"))
            return f"{s.strftime('%H:%M')} – {e.strftime('%H:%M')}"
        return s.strftime("%H:%M")
    except Exception:
        return "See website"
