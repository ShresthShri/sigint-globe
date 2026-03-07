import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base
from app.models.aircraft_obs import AircraftObservation
from app.models.cell import InterferenceCell
from app.models.snapshot import CollectionSnapshot
from app.collectors.aggregator import aggregate_snapshot


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


def _make_observation(snapshot_id, lat, lon, nac_p, **kwargs):
    return AircraftObservation(
        snapshot_id=snapshot_id,
        hex=kwargs.get("hex", "abc123"),
        lat=lat,
        lon=lon,
        nac_p=nac_p,
        nic=kwargs.get("nic"),
        rc=kwargs.get("rc"),
        is_military=kwargs.get("is_military", False),
    )


@pytest.mark.asyncio
async def test_aggregation_basic(db_session):
    snapshot = CollectionSnapshot(
        region_name="test", aircraft_total=5, aircraft_with_nacp=5, aircraft_low_nacp=2
    )
    db_session.add(snapshot)
    await db_session.flush()

    observations = [
        _make_observation(snapshot.id, 34.70, 33.50, nac_p=10, hex="aaa001"),
        _make_observation(snapshot.id, 34.71, 33.51, nac_p=9, hex="aaa002"),
        _make_observation(snapshot.id, 34.72, 33.52, nac_p=9, hex="aaa003"),
        _make_observation(snapshot.id, 34.69, 33.49, nac_p=6, hex="aaa004"),
        _make_observation(snapshot.id, 34.68, 33.48, nac_p=0, hex="aaa005"),
    ]
    for obs in observations:
        db_session.add(obs)
    await db_session.commit()

    cells = await aggregate_snapshot(db_session, snapshot.id)

    assert len(cells) >= 1
    affected = [c for c in cells if c.severity > 0]
    assert len(affected) >= 1

    cell = affected[0]
    assert cell.aircraft_count >= 2
    assert cell.low_nac_count >= 1
    assert cell.interference_ratio > 0
    assert cell.severity > 0


@pytest.mark.asyncio
async def test_aggregation_clean_cell(db_session):
    snapshot = CollectionSnapshot(
        region_name="test", aircraft_total=4, aircraft_with_nacp=4, aircraft_low_nacp=0
    )
    db_session.add(snapshot)
    await db_session.flush()

    observations = [
        _make_observation(snapshot.id, 34.70, 33.50, nac_p=10, hex="bbb001"),
        _make_observation(snapshot.id, 34.71, 33.51, nac_p=9, hex="bbb002"),
        _make_observation(snapshot.id, 34.72, 33.52, nac_p=10, hex="bbb003"),
        _make_observation(snapshot.id, 34.69, 33.49, nac_p=9, hex="bbb004"),
    ]
    for obs in observations:
        db_session.add(obs)
    await db_session.commit()

    cells = await aggregate_snapshot(db_session, snapshot.id)

    for cell in cells:
        assert cell.severity == 0.0
        assert cell.low_nac_count == 0


@pytest.mark.asyncio
async def test_aggregation_skips_sparse_cells(db_session):
    snapshot = CollectionSnapshot(
        region_name="test", aircraft_total=1, aircraft_with_nacp=1, aircraft_low_nacp=1
    )
    db_session.add(snapshot)
    await db_session.flush()

    obs = _make_observation(snapshot.id, 60.0, 25.0, nac_p=3, hex="ccc001")
    db_session.add(obs)
    await db_session.commit()

    cells = await aggregate_snapshot(db_session, snapshot.id)
    assert len(cells) == 0


@pytest.mark.asyncio
async def test_aggregation_multiple_cells(db_session):
    snapshot = CollectionSnapshot(
        region_name="test", aircraft_total=6, aircraft_with_nacp=6, aircraft_low_nacp=2
    )
    db_session.add(snapshot)
    await db_session.flush()

    observations = [
        _make_observation(snapshot.id, 34.70, 33.50, nac_p=10, hex="ddd001"),
        _make_observation(snapshot.id, 34.71, 33.51, nac_p=9, hex="ddd002"),
        _make_observation(snapshot.id, 34.72, 33.52, nac_p=6, hex="ddd003"),
        _make_observation(snapshot.id, 50.00, 14.00, nac_p=10, hex="ddd004"),
        _make_observation(snapshot.id, 50.01, 14.01, nac_p=10, hex="ddd005"),
        _make_observation(snapshot.id, 50.02, 14.02, nac_p=3, hex="ddd006"),
    ]
    for obs in observations:
        db_session.add(obs)
    await db_session.commit()

    cells = await aggregate_snapshot(db_session, snapshot.id)
    unique_h3 = {c.h3_index for c in cells}
    assert len(unique_h3) >= 2
