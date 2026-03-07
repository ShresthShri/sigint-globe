from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.aircraft_obs import AircraftObservation
from app.models.snapshot import CollectionSnapshot
from app.regions import ACTIVE_REGIONS
from app.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(CollectionSnapshot.timestamp)
        .order_by(CollectionSnapshot.id.desc())
        .limit(1)
    )
    last = result.scalar_one_or_none()

    snap_count = await session.scalar(
        select(func.count()).select_from(CollectionSnapshot)
    )
    obs_count = await session.scalar(
        select(func.count()).select_from(AircraftObservation)
    )

    return HealthResponse(
        status="ok",
        last_collection=last,
        total_snapshots=snap_count or 0,
        total_observations=obs_count or 0,
        active_regions=[r.name for r in ACTIVE_REGIONS],
    )
