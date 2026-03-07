import logging
from collections import defaultdict

import h3
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.aircraft_obs import AircraftObservation
from app.models.cell import InterferenceCell
from app.utils.scoring import INTERFERENCE_THRESHOLD, compute_severity

logger = logging.getLogger(__name__)

DEFAULT_H3_RESOLUTION = 4
MIN_AIRCRAFT_PER_CELL = 2


async def aggregate_snapshot(
    session: AsyncSession,
    snapshot_id: int,
    resolution: int = DEFAULT_H3_RESOLUTION,
) -> list[InterferenceCell]:
    result = await session.execute(
        select(AircraftObservation).where(
            AircraftObservation.snapshot_id == snapshot_id
        )
    )
    observations = result.scalars().all()

    if not observations:
        logger.warning(f"No observations for snapshot {snapshot_id}")
        return []

    cells: dict[str, list[int | None]] = defaultdict(list)

    for obs in observations:
        h3_index = h3.latlng_to_cell(obs.lat, obs.lon, resolution)
        cells[h3_index].append(obs.nac_p)

    created: list[InterferenceCell] = []

    for h3_index, nac_p_values in cells.items():
        aircraft_count = len(nac_p_values)

        if aircraft_count < MIN_AIRCRAFT_PER_CELL:
            continue

        known_nacp = [n for n in nac_p_values if n is not None]
        if not known_nacp:
            continue

        low_nac_count = sum(1 for n in known_nacp if n < INTERFERENCE_THRESHOLD)
        interference_ratio = low_nac_count / len(known_nacp)
        avg_nac_p = sum(known_nacp) / len(known_nacp)

        severity = compute_severity(interference_ratio, avg_nac_p, aircraft_count)

        cell_lat, cell_lon = h3.cell_to_latlng(h3_index)

        cell = InterferenceCell(
            snapshot_id=snapshot_id,
            h3_index=h3_index,
            h3_resolution=resolution,
            lat=cell_lat,
            lon=cell_lon,
            aircraft_count=aircraft_count,
            low_nac_count=low_nac_count,
            interference_ratio=round(interference_ratio, 4),
            avg_nac_p=round(avg_nac_p, 2),
            severity=severity,
        )
        session.add(cell)
        created.append(cell)

    await session.commit()

    if created:
        max_sev = max(c.severity for c in created)
        affected = sum(1 for c in created if c.severity > 0)
        logger.info(
            f"Snapshot {snapshot_id}: {len(created)} cells, "
            f"{affected} with interference, max severity={max_sev:.1f}"
        )
    else:
        logger.info(f"Snapshot {snapshot_id}: no cells met minimum aircraft threshold")

    return created
