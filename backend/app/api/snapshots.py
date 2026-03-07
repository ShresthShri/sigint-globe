from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.aircraft_obs import AircraftObservation
from app.models.snapshot import CollectionSnapshot
from app.schemas import AircraftObservationResponse, SnapshotSummary

router = APIRouter()


@router.get("/snapshots", response_model=list[SnapshotSummary])
async def list_snapshots(
    region: str | None = None,
    limit: int = Query(default=20, le=100),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(CollectionSnapshot).order_by(CollectionSnapshot.id.desc()).limit(limit)
    if region:
        stmt = stmt.where(CollectionSnapshot.region_name == region)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.get("/snapshots/{snapshot_id}/aircraft", response_model=list[AircraftObservationResponse])
async def get_snapshot_aircraft(
    snapshot_id: int,
    nac_p_max: int | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(AircraftObservation)
        .where(AircraftObservation.snapshot_id == snapshot_id)
    )
    if nac_p_max is not None:
        stmt = stmt.where(AircraftObservation.nac_p <= nac_p_max)
    result = await session.execute(stmt)
    return result.scalars().all()
