"""
Time Out London — RSS Feed Scraper
====================================
Uses Time Out's public RSS feeds which work reliably from any IP.
Much more reliable than scraping their HTML pages.
"""

import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

# Time Out RSS feeds - these are public and reliable
FEEDS = [
    ("exhibition", "https://www.timeout.com/london/art/rss.xml"),
    ("talk",       "https://www.timeout.com/london/art/art-events-in-london/rss.xml"),
    ("popup",      "https://www.timeout.com/london/things-to-do/london-markets/rss.xml"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; RSSReader/1.0)",
    "Accept": "application/rss+xml, application/xml, text/xml",
}

TYPE_KEYWORDS = {
    "gallery":     ["gallery", "private view", "opening", "vernissage"],
    "popup":       ["market", "fair", "pop-up", "popup", "open studios"],
    "performance": ["performance", "dance", "live", "concert"],
    "talk":        ["talk", "lecture", "workshop", "screening", "panel"],
}


def scrape_timeout():
    events = []
    for default_type, url in FEEDS:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            feed_events = parse_rss(resp.text, default_type)
            events.extend(feed_events)
        except Exception as e:
            print(f"  Time Out RSS error ({url}): {e}")
    return events


def parse_rss(xml_text, default_type):
    events = []
    try:
        root = ET.fromstring(xml_text)
        channel = root.find("channel")
        if channel is None:
            return events

        for item in channel.findall("item"):
            ev = parse_item(item, default_type)
            if ev:
                events.append(ev)
    except Exception as e:
        print(f"  Time Out RSS parse error: {e}")
    return events


def parse_item(item, default_type):
    try:
        title = (item.findtext("title") or "").strip()
        if not title:
            return None

        link        = (item.findtext("link") or "").strip()
        description = strip_html(item.findtext("description") or "")
        pub_date    = item.findtext("pubDate") or ""

        # Classify type from title
        event_type = classify_type(title + " " + description, default_type)

        return {
            "source":      "timeout",
            "source_id":   link[-40:],
            "type":        event_type,
            "label":       get_label(event_type),
            "title":       title,
            "artist":      "",
            "venue":       "London",
            "address":     "London",
            "lat":         None,
            "lng":         None,
            "time":        "See website",
            "date":        format_pub_date(pub_date),
            "price":       extract_price(description),
            "priceNum":    extract_price_num(description),
            "description": description[:300],
            "url":         link,
            "highlight":   False,
            "sponsored":   False,
        }
    except Exception as e:
        print(f"  Time Out item parse error: {e}")
        return None


def strip_html(text):
    return re.sub(r"<[^>]+>", "", text).strip()

def classify_type(text, default_type):
    t = text.lower()
    for etype, kws in TYPE_KEYWORDS.items():
        if any(kw in t for kw in kws):
            return etype
    return default_type

def get_label(event_type):
    return {"gallery":"Gallery Opening","exhibition":"Exhibition","popup":"Pop-up & Market",
            "performance":"Performance","talk":"Artist Talk"}.get(event_type,"Event")

def extract_price(text):
    if not text or "free" in text.lower():
        return "Free entry"
    m = re.search(r"£[\d.]+", text)
    return m.group(0) if m else "See website"

def extract_price_num(text):
    if not text or "free" in text.lower():
        return 0
    m = re.search(r"£([\d.]+)", text)
    return float(m.group(1)) if m else 0

def format_pub_date(pub_date):
    try:
        dt    = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
        today = datetime.now(timezone.utc).date()
        delta = (dt.date() - today).days
        if delta == 0:  return "Today"
        if delta == 1:  return "Tomorrow"
        if delta <= 7:  return "This Week"
        return dt.strftime("%-d %b")
    except:
        return "Upcoming"
