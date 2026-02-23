"""
London Art Venue RSS Feeds
===========================
Scrapes RSS/Atom feeds from major London art venues.
These are 100% reliable - venues publish them for press/aggregators.
No API key needed, no blocking.
"""

import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; GlobeArtLondon/1.0; +https://globeartorg.com)",
    "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
}

# (venue_name, event_type, rss_url)
VENUE_FEEDS = [
    ("Barbican",                "exhibition", "https://www.barbican.org.uk/rss/whats-on"),
    ("Tate Modern",             "exhibition", "https://www.tate.org.uk/whats-on/rss"),
    ("Serpentine",              "exhibition", "https://www.serpentinegalleries.org/whats-on/rss"),
    ("Royal Academy",           "exhibition", "https://www.royalacademy.org.uk/rss/exhibitions"),
    ("Whitechapel Gallery",     "gallery",    "https://www.whitechapelgallery.org/rss/exhibitions"),
    ("South London Gallery",    "gallery",    "https://www.southlondongallery.org/rss"),
    ("ICA London",              "performance","https://www.ica.art/rss"),
    ("Hayward Gallery",         "exhibition", "https://www.southbankcentre.co.uk/rss/whats-on"),
    ("Victoria & Albert Museum","exhibition", "https://www.vam.ac.uk/rss/exhibitions"),
    ("Design Museum",           "exhibition", "https://designmuseum.org/rss"),
    ("Camden Arts Centre",      "gallery",    "https://camdenartscentre.org/rss"),
    ("Saatchi Gallery",         "exhibition", "https://www.saatchigallery.com/rss"),
    ("Photographers Gallery",   "exhibition", "https://thephotographersgallery.org.uk/rss"),
    ("Frieze",                  "gallery",    "https://www.frieze.com/rss.xml"),
]

# Pre-cached coords for these venues
VENUE_COORDS = {
    "Barbican":                 (51.5202, -0.0944),
    "Tate Modern":              (51.5076, -0.0994),
    "Serpentine":               (51.5053, -0.1759),
    "Royal Academy":            (51.5096, -0.1393),
    "Whitechapel Gallery":      (51.5154, -0.0726),
    "South London Gallery":     (51.4710, -0.0643),
    "ICA London":               (51.5072, -0.1310),
    "Hayward Gallery":          (51.5054, -0.1144),
    "Victoria & Albert Museum": (51.4966, -0.1722),
    "Design Museum":            (51.4997, -0.2013),
    "Camden Arts Centre":       (51.5494, -0.1858),
    "Saatchi Gallery":          (51.4897, -0.1594),
    "Photographers Gallery":    (51.5148, -0.1386),
    "Frieze":                   (51.5076, -0.1761),
}

TYPE_KEYWORDS = {
    "gallery":     ["opening", "private view", "vernissage", "launch"],
    "popup":       ["market", "fair", "pop-up", "open studios"],
    "performance": ["performance", "dance", "live", "concert", "theatre"],
    "talk":        ["talk", "lecture", "workshop", "screening", "panel", "symposium"],
}


def scrape_venues_rss():
    events = []
    for venue_name, default_type, url in VENUE_FEEDS:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=12)
            if resp.status_code != 200:
                continue
            items = parse_feed(resp.text, venue_name, default_type)
            events.extend(items)
            print(f"  {venue_name}: {len(items)} events")
        except Exception as e:
            print(f"  {venue_name} RSS error: {e}")
    return events


def parse_feed(xml_text, venue_name, default_type):
    events = []
    try:
        root = ET.fromstring(xml_text)
        # Handle both RSS and Atom
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        
        # RSS items
        items = root.findall(".//item")
        # Atom entries
        if not items:
            items = root.findall(".//atom:entry", ns) or root.findall(".//entry")

        coords = VENUE_COORDS.get(venue_name, (None, None))

        for item in items[:10]:  # max 10 per venue
            ev = parse_item(item, venue_name, default_type, coords, ns)
            if ev:
                events.append(ev)
    except Exception as e:
        print(f"  Parse error for {venue_name}: {e}")
    return events


def parse_item(item, venue_name, default_type, coords, ns):
    try:
        # Get title
        title = (
            gettext(item, "title") or
            gettext(item, "atom:title", ns) or ""
        ).strip()
        if not title or len(title) < 4:
            return None

        # Get link
        link = (
            gettext(item, "link") or
            item.get("href") or
            (item.find("atom:link", ns) or item.find("link") or ET.Element("x")).get("href", "") or ""
        ).strip()

        # Get description
        desc = strip_html(
            gettext(item, "description") or
            gettext(item, "summary") or
            gettext(item, "atom:summary", ns) or ""
        )[:300]

        # Get date
        pub = (
            gettext(item, "pubDate") or
            gettext(item, "published") or
            gettext(item, "atom:published", ns) or
            gettext(item, "dc:date") or ""
        )

        event_type = classify_type(title + " " + desc, default_type)

        return {
            "source":      "venue_rss",
            "source_id":   link[-50:] if link else title[:30],
            "type":        event_type,
            "label":       get_label(event_type),
            "title":       title,
            "artist":      "",
            "venue":       venue_name,
            "address":     venue_name + ", London",
            "lat":         coords[0],
            "lng":         coords[1],
            "time":        "See website",
            "date":        format_date(pub),
            "price":       extract_price(desc),
            "priceNum":    extract_price_num(desc),
            "description": desc,
            "url":         link,
            "highlight":   False,
            "sponsored":   False,
        }
    except Exception as e:
        return None


def gettext(el, tag, ns=None):
    found = el.find(tag, ns) if ns else el.find(tag)
    if found is not None and found.text:
        return found.text.strip()
    return None

def strip_html(text):
    if not text: return ""
    return re.sub(r"<[^>]+>", " ", text).strip()

def classify_type(text, default_type):
    t = text.lower()
    for etype, kws in TYPE_KEYWORDS.items():
        if any(kw in t for kw in kws):
            return etype
    return default_type

def get_label(event_type):
    return {"gallery":"Gallery Opening","exhibition":"Exhibition","popup":"Pop-up & Market",
            "performance":"Performance","talk":"Artist Talk"}.get(event_type, "Event")

def extract_price(text):
    if not text: return "Free entry"
    if "free" in text.lower(): return "Free entry"
    m = re.search(r"£[\d.]+", text)
    return m.group(0) if m else "Free entry"

def extract_price_num(text):
    if not text or "free" in text.lower(): return 0
    m = re.search(r"£([\d.]+)", text)
    return float(m.group(1)) if m else 0

def format_date(date_str):
    if not date_str: return "Upcoming"
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S GMT",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            today = datetime.now(timezone.utc).date()
            delta = (dt.date() - today).days
            if delta < 0:   return "On Now"
            if delta == 0:  return "Today"
            if delta == 1:  return "Tomorrow"
            if delta <= 7:  return "This Week"
            return dt.strftime("%-d %b")
        except:
            continue
    return "Upcoming"
