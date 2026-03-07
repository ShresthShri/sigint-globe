import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.interference import router as interference_router
from app.api.snapshots import router as snapshots_router
from app.config import settings
from app.database import init_db
from app.scheduler import collector, start_scheduler, stop_scheduler

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")
    await init_db()

    logger.info("Running initial collection...")
    asyncio.create_task(collector.collect())

    start_scheduler()

    yield

    stop_scheduler()


app = FastAPI(
    title="sigint-globe",
    description="GPS interference mapper using ADS-B data from adsb.lol",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health_router, tags=["health"])
app.include_router(interference_router, tags=["interference"])
app.include_router(snapshots_router, tags=["snapshots"])


@app.get("/")
async def root():
    return {"name": "sigint-globe", "version": "0.1.0"}
