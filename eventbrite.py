"""
Eventbrite London Art Events Scraper
=====================================
Uses Eventbrite's public search API (no key needed for basic searches).
Targets art/visual-arts categories in London.

Eventbrite category IDs:
  105 = Arts
  103 = Music (excluded)
  110 = Food & Drink (excluded)
"""

import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Eventbrite category for Arts & Theatre & Comedy is 105
EVENTBRITE_URL = (
    "https://www.eventbrite.co.uk/d/united-kingdom--london/art-events/"
    "?page={page}"
)

# Subcategory keywords that match our event types
TYPE_KEYWORDS = {
    "gallery":     ["gallery", "private view", "opening night", "vernissage", "preview"],
    "exhibition":  ["exhibition", "exhibit", "show", "retrospective", "survey", "collection"],
    "popup":       ["pop-up", "popup", "market", "fair", "festival", "open studios"],
    "performance": ["performance", "dance", "live art", "durational", "theatre", "concert"],
    "talk":        ["talk", "lecture", "conversation", "workshop", "panel", "screening", "symposium"],
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-GB,en;q=0.9",
}


def scrape_eventbrite(max_pages=5):
    events = []

    for page in range(1, max_pages + 1):
        url = EVENTBRITE_URL.format(page=page)
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            print(f"  Eventbrite page {page} error: {e}")
            break

        soup = BeautifulSoup(resp.text, "lxml")

        # Eventbrite renders event cards in <li> elements with data attributes
        cards = soup.select("li[data-event-id], article.eds-event-card")

        if not cards:
            # Try alternate selectors for their newer layout
            cards = soup.select("[class*='event-card'], [data-testid='event-card']")

        if not cards:
            break

        for card in cards:
            ev = parse_eventbrite_card(card)
            if ev:
                events.append(ev)

    return events


def parse_eventbrite_card(card):
    try:
        title_el = (
            card.select_one("[class*='title'], h2, h3, [data-testid='event-title']")
        )
        title = title_el.get_text(strip=True) if title_el else None
        if not title:
            return None

        # Determine event type from title/description keywords
        event_type = classify_type(title)

        venue_el = card.select_one("[class*='venue'], [class*='location'], [data-testid*='venue']")
        venue = venue_el.get_text(strip=True) if venue_el else "London"

        date_el = card.select_one("time, [class*='date'], [datetime]")
        if date_el:
            date_str = date_el.get("datetime") or date_el.get_text(strip=True)
            date = format_date(date_str)
        else:
            date = "Today"

        price_el = card.select_one("[class*='price'], [class*='cost']")
        price = price_el.get_text(strip=True) if price_el else "Free entry"

        link_el = card.select_one("a[href*='eventbrite']")
        url = link_el["href"] if link_el else None

        img_el = card.select_one("img")
        image = img_el.get("src") or img_el.get("data-src") if img_el else None

        desc_el = card.select_one("[class*='description'], [class*='summary'], p")
        description = desc_el.get_text(strip=True)[:200] if desc_el else ""

        return {
            "source":      "eventbrite",
            "source_id":   card.get("data-event-id", ""),
            "type":        event_type,
            "label":       get_label(event_type),
            "title":       title,
            "artist":      "",
            "venue":       venue,
            "address":     venue,  # geocoder will resolve
            "lat":         None,
            "lng":         None,
            "time":        extract_time(date_str if date_el else ""),
            "date":        date,
            "price":       clean_price(price),
            "priceNum":    extract_price_num(price),
            "description": description,
            "url":         url,
            "image":       image,
            "highlight":   False,
            "sponsored":   False,
        }
    except Exception:
        return None


def classify_type(text):
    text_lower = text.lower()
    for event_type, keywords in TYPE_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return event_type
    return "exhibition"  # default for art events


def get_label(event_type):
    labels = {
        "gallery":     "Gallery Opening",
        "exhibition":  "Exhibition",
        "popup":       "Pop-up & Market",
        "performance": "Performance",
        "talk":        "Artist Talk",
    }
    return labels.get(event_type, "Event")


def format_date(date_str):
    if not date_str:
        return "Today"
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        today = datetime.now().date()
        if dt.date() == today:
            return "Today"
        elif (dt.date() - today).days == 1:
            return "Tomorrow"
        else:
            return dt.strftime("%-d %b")
    except Exception:
        return date_str[:10] if len(date_str) >= 10 else "Today"


def extract_time(date_str):
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%H:%M")
    except Exception:
        return "See website"


def clean_price(price_str):
    if not price_str or "free" in price_str.lower():
        return "Free entry"
    price_str = re.sub(r"\s+", " ", price_str).strip()
    return price_str[:20]


def extract_price_num(price_str):
    if not price_str or "free" in price_str.lower():
        return 0
    nums = re.findall(r"[\d.]+", price_str)
    return float(nums[0]) if nums else 0
