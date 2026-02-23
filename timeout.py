"""
Time Out London — Art & Culture Scraper
=========================================
Time Out has structured JSON-LD on their listing pages which makes
scraping clean and reliable. We target:
  /london/art           → exhibitions & gallery shows
  /london/art/free-art  → free events
  /london/theatre       → performances
  /london/things-to-do/markets → markets & pop-ups
"""

import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

TIMEOUT_PAGES = [
    ("exhibition", "https://www.timeout.com/london/art"),
    ("exhibition", "https://www.timeout.com/london/art/free-art-in-london"),
    ("gallery",    "https://www.timeout.com/london/art/london-gallery-openings"),
    ("performance","https://www.timeout.com/london/theatre"),
    ("popup",      "https://www.timeout.com/london/things-to-do/london-markets"),
    ("talk",       "https://www.timeout.com/london/art/art-events-in-london"),
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-GB,en;q=0.9",
}


def scrape_timeout():
    events = []

    for event_type, url in TIMEOUT_PAGES:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            page_events = parse_timeout_page(resp.text, event_type, url)
            events.extend(page_events)
        except Exception as e:
            print(f"  Time Out error ({url}): {e}")

    return events


def parse_timeout_page(html, default_type, source_url):
    soup   = BeautifulSoup(html, "lxml")
    events = []

    # ── Strategy 1: JSON-LD structured data (most reliable) ──
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                items = data.get("@graph", [data])
            else:
                continue

            for item in items:
                if item.get("@type") in ("Event", "ExhibitionEvent", "TheaterEvent"):
                    ev = parse_jsonld_event(item, default_type)
                    if ev:
                        events.append(ev)
        except Exception:
            continue

    # ── Strategy 2: HTML cards (fallback) ──
    if not events:
        cards = soup.select(
            "article, [class*='card'], [class*='listing'], [data-testid*='card']"
        )
        for card in cards[:30]:  # limit to avoid noise
            ev = parse_timeout_card(card, default_type, source_url)
            if ev:
                events.append(ev)

    return events


def parse_jsonld_event(item, default_type):
    try:
        title = item.get("name", "")
        if not title:
            return None

        location = item.get("location", {})
        if isinstance(location, list):
            location = location[0]

        venue_name = location.get("name", "London")
        address    = location.get("address", {})
        if isinstance(address, str):
            addr_str = address
        else:
            addr_str = ", ".join(filter(None, [
                address.get("streetAddress"),
                address.get("addressLocality", "London"),
                address.get("postalCode"),
            ]))

        # Geo
        geo = location.get("geo", {})
        lat = float(geo["latitude"])  if geo.get("latitude")  else None
        lng = float(geo["longitude"]) if geo.get("longitude") else None

        # Dates
        start = item.get("startDate", "")
        end   = item.get("endDate", "")
        date_str = format_date_range(start, end)
        time_str = format_time_from_iso(start)

        # Price
        offers = item.get("offers", {})
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        price_val  = offers.get("price", 0)
        price_cur  = offers.get("priceCurrency", "GBP")
        avail      = offers.get("availability", "")
        if "Free" in str(avail) or price_val == 0:
            price_str = "Free entry"
            price_num = 0
        else:
            price_str = f"£{price_val}"
            price_num = float(price_val) if price_val else 0

        description = item.get("description", "")[:200]
        image       = item.get("image")
        if isinstance(image, dict):
            image = image.get("url", "")
        elif isinstance(image, list):
            image = image[0] if image else ""

        # Classify type more precisely
        event_type = classify_from_jsonld(item, default_type)

        return {
            "source":      "timeout",
            "source_id":   item.get("url", "")[-40:],
            "type":        event_type,
            "label":       get_label(event_type),
            "title":       title,
            "artist":      item.get("performer", {}).get("name", "") if isinstance(item.get("performer"), dict) else "",
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
            "image":       image or "",
            "highlight":   False,
            "sponsored":   False,
        }
    except Exception:
        return None


def parse_timeout_card(card, default_type, source_url):
    """Fallback HTML parser for Time Out cards."""
    try:
        title_el = card.select_one("h2, h3, [class*='title']")
        title    = title_el.get_text(strip=True) if title_el else None
        if not title or len(title) < 5:
            return None

        venue_el  = card.select_one("[class*='venue'], [class*='location']")
        venue     = venue_el.get_text(strip=True) if venue_el else "London"

        price_el  = card.select_one("[class*='price']")
        price_str = price_el.get_text(strip=True) if price_el else "Free entry"

        desc_el   = card.select_one("p, [class*='description']")
        desc      = desc_el.get_text(strip=True)[:200] if desc_el else ""

        link_el   = card.select_one("a[href]")
        url       = link_el["href"] if link_el else source_url

        return {
            "source":      "timeout",
            "source_id":   url[-40:] if url else "",
            "type":        default_type,
            "label":       get_label(default_type),
            "title":       title,
            "artist":      "",
            "venue":       venue,
            "address":     venue,
            "lat":         None,
            "lng":         None,
            "time":        "See website",
            "date":        "Today",
            "price":       clean_price(price_str),
            "priceNum":    extract_price_num(price_str),
            "description": desc,
            "url":         url,
            "image":       "",
            "highlight":   False,
            "sponsored":   False,
        }
    except Exception:
        return None


def classify_from_jsonld(item, default_type):
    type_str = item.get("@type", "")
    name_l   = item.get("name", "").lower()

    if "Exhibition" in type_str:    return "exhibition"
    if "Theater"    in type_str:    return "performance"
    kw_map = {
        "gallery":     ["opening", "private view", "gallery"],
        "popup":       ["market", "fair", "pop-up", "open studios"],
        "performance": ["performance", "dance", "concert", "live"],
        "talk":        ["talk", "lecture", "workshop", "screening"],
    }
    for etype, kws in kw_map.items():
        if any(kw in name_l for kw in kws):
            return etype
    return default_type


def format_date_range(start, end):
    try:
        s     = datetime.fromisoformat(start.replace("Z", "+00:00"))
        today = datetime.now().date()
        delta = (s.date() - today).days
        if delta == 0:
            return "Today"
        if delta == 1:
            return "Tomorrow"
        if end:
            e = datetime.fromisoformat(end.replace("Z", "+00:00"))
            if (e.date() - today).days > 7:
                return f"Until {e.strftime('%-d %b')}"
        return s.strftime("%-d %b")
    except Exception:
        return "Upcoming"


def format_time_from_iso(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%H:%M")
    except Exception:
        return "See website"


def get_label(event_type):
    return {
        "gallery":     "Gallery Opening",
        "exhibition":  "Exhibition",
        "popup":       "Pop-up & Market",
        "performance": "Performance",
        "talk":        "Artist Talk",
    }.get(event_type, "Event")


def clean_price(p):
    if not p or "free" in p.lower():
        return "Free entry"
    return p[:20].strip()


def extract_price_num(p):
    import re
    if not p or "free" in p.lower():
        return 0
    nums = re.findall(r"[\d.]+", p)
    return float(nums[0]) if nums else 0
