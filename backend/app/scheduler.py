import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.collectors.adsb import ADSBCollector
from app.config import settings

logger = logging.getLogger(__name__)

collector = ADSBCollector()
scheduler = AsyncIOScheduler()


async def _run_collection():
    try:
        await collector.collect()
    except Exception:
        logger.exception("Scheduled collection failed")


def start_scheduler():
    scheduler.add_job(
        _run_collection,
        trigger=IntervalTrigger(seconds=settings.poll_interval_seconds),
        id="adsb_collection",
        name="ADS-B data collection",
        replace_existing=True,
        max_instances=1,
    )
    scheduler.start()
    logger.info(
        f"Scheduler started — collecting every {settings.poll_interval_seconds}s"
    )


def stop_scheduler():
    scheduler.shutdown(wait=False)
    asyncio.create_task(collector.close())
    logger.info("Scheduler stopped")
