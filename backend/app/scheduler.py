"""
Periodic task scheduler — runs data collectors on configurable intervals.

Currently schedules:
    - ADS-B collection: every 5 minutes (polls adsb.lol for aircraft data)
    - News collection: every 30 minutes (polls RSS feeds for GPS/EW headlines)
"""

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.collectors.adsb import ADSBCollector
from app.collectors.news import NewsCollector
from app.config import settings

logger = logging.getLogger(__name__)

# Instantiate collectors at module level so they persist across scheduler ticks.
# The ADSB collector holds an httpx client that reuses connections.
collector = ADSBCollector()
news_collector = NewsCollector()
scheduler = AsyncIOScheduler()


async def _run_collection():
    """Wrapper for the ADS-B collection job."""
    try:
        await collector.collect()
    except Exception:
        logger.exception("Scheduled ADS-B collection failed")


async def _run_news_collection():
    """Wrapper for the news RSS collection job."""
    try:
        await news_collector.collect()
    except Exception:
        logger.exception("Scheduled news collection failed")


def start_scheduler():
    """Configure and start both collection jobs."""
    # ADS-B: every 5 minutes (configurable via .env)
    scheduler.add_job(
        _run_collection,
        trigger=IntervalTrigger(seconds=settings.poll_interval_seconds),
        id="adsb_collection",
        name="ADS-B data collection",
        replace_existing=True,
        max_instances=1,
    )

    # News: every 30 minutes — RSS feeds don't update that fast,
    # and we don't want to hammer them
    scheduler.add_job(
        _run_news_collection,
        trigger=IntervalTrigger(minutes=30),
        id="news_collection",
        name="News RSS collection",
        replace_existing=True,
        max_instances=1,
    )

    scheduler.start()
    logger.info(
        f"Scheduler started — ADS-B every {settings.poll_interval_seconds}s, "
        f"news every 30min"
    )


def stop_scheduler():
    """Shutdown scheduler and clean up HTTP clients."""
    scheduler.shutdown(wait=False)
    asyncio.create_task(collector.close())
    logger.info("Scheduler stopped")
