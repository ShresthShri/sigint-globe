"""
Events API — serves news/NOTAM events to the frontend.

Events can be filtered by time range and region. The frontend
uses this to populate the EventPanel sidebar alongside the globe.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.event import Event

router = APIRouter()


class EventResponse(BaseModel):
    """Shape of an event returned to the frontend."""
    id: int
    timestamp: datetime
    source: str
    headline: str
    url: str | None
    summary: str | None
    lat: float | None
    lon: float | None
    region_name: str | None
    keywords_matched: str | None

    model_config = {"from_attributes": True}


@router.get("/events", response_model=list[EventResponse])
async def get_events(
    start: datetime | None = Query(default=None, description="Filter events after this time"),
    end: datetime | None = Query(default=None, description="Filter events before this time"),
    region: str | None = Query(default=None, description="Filter by region name"),
    limit: int = Query(default=50, le=200, description="Max events to return"),
    session: AsyncSession = Depends(get_session),
):
    """Return recent events, newest first.

    Used by the frontend EventPanel to show correlated news
    alongside the interference data on the globe.
    """
    stmt = select(Event).order_by(Event.timestamp.desc()).limit(limit)

    if start:
        stmt = stmt.where(Event.timestamp >= start)
    if end:
        stmt = stmt.where(Event.timestamp <= end)
    if region:
        stmt = stmt.where(Event.region_name == region)

    result = await session.execute(stmt)
    return result.scalars().all()
