from datetime import datetime

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    last_collection: datetime | None
    total_snapshots: int
    total_observations: int
    active_regions: list[str]


class SnapshotSummary(BaseModel):
    id: int
    timestamp: datetime
    region_name: str
    aircraft_total: int
    aircraft_with_nacp: int
    aircraft_low_nacp: int
    duration_ms: float

    model_config = {"from_attributes": True}


class AircraftObservationResponse(BaseModel):
    hex: str
    flight: str | None
    reg: str | None
    ac_type: str | None
    lat: float
    lon: float
    alt_baro: int | None
    nac_p: int | None
    nic: int | None
    rc: int | None
    gs: float | None
    tas: int | None
    is_military: bool
    squawk: str | None

    model_config = {"from_attributes": True}
