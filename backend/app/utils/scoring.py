"""NACp interpretation and interference severity scoring."""

NACP_ACCURACY_M: dict[int, float] = {
    11: 3.0,
    10: 10.0,
    9: 30.0,
    8: 93.0,
    7: 185.2,
    6: 370.4,
    5: 926.0,
    4: 1852.0,
    3: 3704.0,
    2: 7408.0,
    1: 14816.0,
    0: 18520.0,
}

INTERFERENCE_THRESHOLD = 8

NACP_LABELS: dict[int, str] = {
    11: "excellent",
    10: "good",
    9: "acceptable",
    8: "borderline",
    7: "degraded",
    6: "poor",
    5: "bad",
    4: "very_bad",
    3: "severe",
    2: "severe",
    1: "extreme",
    0: "unknown",
}


def is_interference(nac_p: int | None) -> bool:
    if nac_p is None:
        return False
    return nac_p < INTERFERENCE_THRESHOLD


def compute_severity(
    interference_ratio: float,
    avg_nac_p: float,
    aircraft_count: int,
) -> float:
    if aircraft_count == 0 or interference_ratio == 0.0:
        return 0.0

    base = interference_ratio * 7.0
    nacp_bonus = max(0.0, (9.0 - avg_nac_p) / 3.0)
    severity = base + nacp_bonus

    return round(min(10.0, max(0.0, severity)), 2)
