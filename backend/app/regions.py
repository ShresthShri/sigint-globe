from dataclasses import dataclass


@dataclass(frozen=True)
class Region:
    name: str
    lat: float
    lon: float
    radius_nm: int
    description: str = ""


REGIONS: list[Region] = [
    Region(
        name="eastern_med",
        lat=34.7,
        lon=33.5,
        radius_nm=200,
        description="Eastern Mediterranean — Cyprus, Lebanon, Syria. Chronic GPS jamming zone.",
    ),
    Region(
        name="ukraine",
        lat=48.5,
        lon=35.0,
        radius_nm=250,
        description="Black Sea / Ukraine — active conflict zone with heavy EW activity.",
    ),
    Region(
        name="persian_gulf",
        lat=27.0,
        lon=51.0,
        radius_nm=200,
        description="Persian Gulf / Strait of Hormuz — military GPS interference.",
    ),
    Region(
        name="baltic",
        lat=57.0,
        lon=24.0,
        radius_nm=150,
        description="Baltic states — Russian electronic warfare spillover.",
    ),
]

ACTIVE_REGIONS = [r for r in REGIONS if r.name == "eastern_med"]


def get_region(name: str) -> Region | None:
    return next((r for r in REGIONS if r.name == name), None)
