"""
News RSS collector — polls public news feeds for GPS/jamming-related headlines
and stores them as Event records with optional region tagging.

Flow:
    1. Parse each RSS feed (Reuters, BBC, Al Jazeera, defense outlets)
    2. For each entry, check title + summary against GPS/EW keywords
    3. If matched, try to associate with a monitored region (eastern_med, etc.)
    4. Skip duplicates (same headline + source already in DB)
    5. Store as Event with timestamp, source, matched keywords, and region
"""

import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.collectors.base import BaseCollector
from app.database import async_session
from app.models.event import Event

logger = logging.getLogger(__name__)

# Headlines must contain at least one of these to be stored.
# Kept broad enough to catch EW activity but narrow enough to avoid noise.
# Two tiers of keywords:
# - PRIMARY: directly about GPS/EW interference (always store)
# - CONTEXT: conflict/military activity in monitored regions (store if region matches too)
PRIMARY_KEYWORDS = [
    "gps", "gnss", "jamming", "spoofing", "electronic warfare",
    "navigation interference", "gps disruption", "signal jamming",
    "ew system", "radar jamming",
]

CONTEXT_KEYWORDS = [
    "missile", "strike", "military", "air defense", "airspace",
    "no-fly zone", "drone", "bombing", "air raid",
]

# RSS feeds — removed Reuters and Defense One (broken XML)
FEEDS = [
    {"name": "BBC World", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
    {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml"},
    {"name": "The War Zone", "url": "https://www.thedrive.com/the-war-zone/feed"},
]

# Maps region names to location keywords and center coordinates.
# When a headline mentions "Cyprus", we tag it as eastern_med and
# place the marker at that region's center on the globe.
REGION_KEYWORDS = {
    "eastern_med": {
        "keywords": ["cyprus", "lebanon", "syria", "mediterranean", "crete", "aegean", "turkey"],
        "lat": 34.7,
        "lon": 33.5,
    },
    "ukraine": {
        "keywords": ["ukraine", "black sea", "crimea", "donbas", "kyiv", "odesa"],
        "lat": 48.5,
        "lon": 35.0,
    },
    "persian_gulf": {
        "keywords": ["iran", "persian gulf", "hormuz", "iraq", "saudi", "gulf of oman"],
        "lat": 27.0,
        "lon": 51.0,
    },
    "baltic": {
        "keywords": ["baltic", "estonia", "latvia", "lithuania", "kaliningrad", "finland"],
        "lat": 57.0,
        "lon": 24.0,
    },
}


def _match_keywords(text: str) -> list[str]:
    """Check text against both keyword tiers.

    Returns matched keywords. Primary keywords always count.
    Context keywords only count if the text also mentions a monitored region.
    This prevents storing every generic "military" headline.
    """
    text_lower = text.lower()

    # Primary keywords — always relevant
    primary_hits = [kw for kw in PRIMARY_KEYWORDS if kw in text_lower]
    if primary_hits:
        return primary_hits

    # Context keywords — only relevant if a monitored region is also mentioned
    context_hits = [kw for kw in CONTEXT_KEYWORDS if kw in text_lower]
    if context_hits:
        region_name, _, _ = _match_region(text)
        if region_name:
            return context_hits

    return []

def _match_region(text: str) -> tuple[str | None, float | None, float | None]:
    """Try to associate text with a monitored region based on location keywords.

    Returns (region_name, lat, lon) or (None, None, None) if no match.
    First match wins — a headline mentioning both "Syria" and "Baltic"
    would get tagged as eastern_med because it's checked first.
    """
    text_lower = text.lower()
    for region_name, info in REGION_KEYWORDS.items():
        for kw in info["keywords"]:
            if kw in text_lower:
                return region_name, info["lat"], info["lon"]
    return None, None, None


def _parse_pub_date(entry) -> datetime:
    """Extract publication date from an RSS entry.

    RSS feeds are inconsistent with date formats — some use
    published_parsed (struct_time), some use published (string).
    Falls back to now() if neither works.
    """
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        except Exception:
            pass
    if hasattr(entry, "published") and entry.published:
        try:
            return parsedate_to_datetime(entry.published)
        except Exception:
            pass
    return datetime.now(timezone.utc)


class NewsCollector(BaseCollector):
    """Collects GPS/EW-related news from RSS feeds."""

    async def collect(self) -> None:
        """Poll all configured feeds."""
        for feed_info in FEEDS:
            try:
                await self._collect_feed(feed_info["name"], feed_info["url"])
            except Exception:
                logger.exception(f"Failed to collect feed: {feed_info['name']}")

    async def _collect_feed(self, source: str, url: str) -> None:
        """Parse a single RSS feed and store keyword-matched entries.

        Only the 20 most recent entries are checked per feed per cycle.
        Duplicates are detected by (headline, source) uniqueness.
        """
        feed = feedparser.parse(url)

        if not feed.entries:
            logger.debug(f"No entries from {source}")
            return

        new_count = 0
        async with async_session() as session:
            for entry in feed.entries[:20]:
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                # Search both title and summary for keywords
                search_text = f"{title} {summary}"

                matched = _match_keywords(search_text)
                if not matched:
                    continue

                entry_url = entry.get("link", "")

                # Skip if we already have this exact headline from this source
                existing = await session.execute(
                    select(Event).where(
                        Event.headline == title,
                        Event.source == source,
                    ).limit(1)
                )
                if existing.scalar_one_or_none():
                    continue

                # Try to associate with a monitored region
                region_name, lat, lon = _match_region(search_text)
                pub_date = _parse_pub_date(entry)

                event = Event(
                    timestamp=pub_date,
                    source=source,
                    headline=title,
                    url=entry_url,
                    summary=summary[:500] if summary else None,
                    lat=lat,
                    lon=lon,
                    region_name=region_name,
                    keywords_matched=", ".join(matched),
                )
                session.add(event)
                new_count += 1

            await session.commit()

        if new_count > 0:
            logger.info(f"[{source}] Stored {new_count} new events")
