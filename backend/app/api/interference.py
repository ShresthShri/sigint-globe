from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.cell import InterferenceCell
from app.models.snapshot import CollectionSnapshot

router = APIRouter()


class CellResponse(BaseModel):
    h3_index: str
    lat: float
    lon: float
    severity: float
    aircraft_count: int
    low_nac_count: int
    interference_ratio: float
    avg_nac_p: float
    timestamp: datetime
    snapshot_id: int

    model_config = {"from_attributes": True}


class TimelineResponse(BaseModel):
    timestamps: list[datetime]
    snapshot_ids: list[int]


@router.get("/interference", response_model=list[CellResponse])
async def get_interference(
    start: datetime | None = Query(default=None),
    end: datetime | None = Query(default=None),
    min_severity: float = Query(default=0.0),
    region: str | None = Query(default=None),
    snapshot_id: int | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(InterferenceCell, CollectionSnapshot.timestamp)
        .join(CollectionSnapshot, InterferenceCell.snapshot_id == CollectionSnapshot.id)
        .where(InterferenceCell.severity >= min_severity)
    )
    if snapshot_id:
        stmt = stmt.where(InterferenceCell.snapshot_id == snapshot_id)
    if start:
        stmt = stmt.where(CollectionSnapshot.timestamp >= start)
    if end:
        stmt = stmt.where(CollectionSnapshot.timestamp <= end)
    if region:
        stmt = stmt.where(CollectionSnapshot.region_name == region)

    stmt = stmt.order_by(CollectionSnapshot.timestamp.desc()).limit(500)

    result = await session.execute(stmt)
    rows = result.all()

    return [
        CellResponse(
            h3_index=cell.h3_index,
            lat=cell.lat,
            lon=cell.lon,
            severity=cell.severity,
            aircraft_count=cell.aircraft_count,
            low_nac_count=cell.low_nac_count,
            interference_ratio=cell.interference_ratio,
            avg_nac_p=cell.avg_nac_p,
            timestamp=timestamp,
            snapshot_id=cell.snapshot_id,
        )
        for cell, timestamp in rows
    ]


@router.get("/interference/timeline", response_model=TimelineResponse)
async def get_timeline(
    region: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(CollectionSnapshot.id, CollectionSnapshot.timestamp)
        .order_by(CollectionSnapshot.timestamp.asc())
    )
    if region:
        stmt = stmt.where(CollectionSnapshot.region_name == region)

    result = await session.execute(stmt)
    rows = result.all()

    return TimelineResponse(
        snapshot_ids=[r[0] for r in rows],
        timestamps=[r[1] for r in rows],
    )
