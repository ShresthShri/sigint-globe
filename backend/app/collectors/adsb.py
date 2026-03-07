import logging
import time
from datetime import datetime, timezone

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.collectors.base import BaseCollector
from app.collectors.aggregator import aggregate_snapshot
from app.config import settings
from app.database import async_session
from app.models.aircraft_obs import AircraftObservation
from app.models.snapshot import CollectionSnapshot
from app.regions import ACTIVE_REGIONS, Region

logger = logging.getLogger(__name__)

INTERFERENCE_THRESHOLD = 8


class ADSBCollector(BaseCollector):

    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=settings.adsb_base_url,
            timeout=30.0,
            headers={"Accept": "application/json"},
        )

    async def collect(self) -> None:
        for region in ACTIVE_REGIONS:
            try:
                await self._collect_region(region)
            except Exception:
                logger.exception(f"Failed to collect region: {region.name}")

    async def _collect_region(self, region: Region) -> None:
        start = time.monotonic()

        url = f"/lat/{region.lat}/lon/{region.lon}/dist/{region.radius_nm}"
        logger.info(f"Polling {region.name}: {settings.adsb_base_url}{url}")

        response = await self.client.get(url)
        response.raise_for_status()
        data = response.json()

        aircraft_list = data.get("ac", [])
        if not aircraft_list:
            logger.warning(f"No aircraft returned for {region.name}")
            return

        async with async_session() as session:
            snapshot, observations = self._parse_response(
                region.name, aircraft_list
            )
            snapshot.duration_ms = (time.monotonic() - start) * 1000

            session.add(snapshot)
            for obs in observations:
                obs.snapshot = snapshot
                session.add(obs)

            await session.commit()

            logger.info(
                f"[{region.name}] Stored {snapshot.aircraft_total} aircraft "
                f"({snapshot.aircraft_with_nacp} with NACp, "
                f"{snapshot.aircraft_low_nacp} low NACp < {INTERFERENCE_THRESHOLD}) "
                f"in {snapshot.duration_ms:.0f}ms"
            )

            await aggregate_snapshot(session, snapshot.id)

    def _parse_response(
        self, region_name: str, aircraft_list: list[dict]
    ) -> tuple[CollectionSnapshot, list[AircraftObservation]]:
        observations: list[AircraftObservation] = []
        with_nacp = 0
        low_nacp = 0

        for ac in aircraft_list:
            lat = ac.get("lat")
            lon = ac.get("lon")
            if lat is None or lon is None:
                continue

            nac_p = ac.get("nac_p")
            if nac_p is not None:
                with_nacp += 1
                if nac_p < INTERFERENCE_THRESHOLD:
                    low_nacp += 1

            db_flags = ac.get("dbFlags", 0) or 0
            is_military = bool(db_flags & 1)

            obs = AircraftObservation(
                hex=ac.get("hex", "unknown"),
                flight=(ac.get("flight") or "").strip() or None,
                reg=ac.get("r"),
                ac_type=ac.get("t"),
                lat=lat,
                lon=lon,
                alt_baro=ac.get("alt_baro") if isinstance(ac.get("alt_baro"), int) else None,
                nac_p=nac_p,
                nic=ac.get("nic"),
                rc=ac.get("rc"),
                sil=ac.get("sil"),
                gs=ac.get("gs"),
                tas=ac.get("tas"),
                is_military=is_military,
                squawk=ac.get("squawk"),
            )
            observations.append(obs)

        snapshot = CollectionSnapshot(
            timestamp=datetime.now(timezone.utc),
            region_name=region_name,
            aircraft_total=len(observations),
            aircraft_with_nacp=with_nacp,
            aircraft_low_nacp=low_nacp,
        )

        return snapshot, observations

    async def close(self):
        await self.client.aclose()
