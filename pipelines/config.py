"""Shared paths and constants for the STINT THEORY data pipeline."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw"              # per-race extracts in FastF1-style layout (git-ignored)
PROCESSED = DATA / "processed"  # harmonised lap tables (git-ignored)
MANIFESTS = DATA / "manifests"  # provenance records (committed)
REPORTS = DATA / "reports"      # validation and coverage reports (committed)
SCHEMAS = DATA / "schemas"

REFERENCE = DATA / "reference"  # hand-checked reference tables (committed)
CACHE = Path(os.environ.get("STINT_CACHE", ROOT / ".cache"))

# OpenF1 historical data starts in 2023. 2026 is a new rules era and is held out.
DEFAULT_SEASONS = [2023, 2024, 2025]

# Track status codes, FastF1 convention. With OpenF1 they are rebuilt from
# race-control messages (pipelines/openf1.py).
TRACK_STATUS = {
    "1": "green",
    "2": "yellow",
    "3": "unused",
    "4": "safety_car",
    "5": "red_flag",
    "6": "vsc_deployed",
    "7": "vsc_ending",
}

SLICK_RELATIVE = ("SOFT", "MEDIUM", "HARD")
WET_COMPOUNDS = ("INTERMEDIATE", "WET")
# 2018 used named compounds (softest to hardest). Not needed for OpenF1 (2023+),
# kept so the compound mapper stays general.
NAMED_2018_ORDER = (
    "HYPERSOFT", "ULTRASOFT", "SUPERSOFT", "SOFT", "MEDIUM", "HARD", "SUPERHARD",
)


def regulation_era(season: int) -> str:
    """Technical-regulation era. 2022 introduced ground-effect cars and 18-inch tyres."""
    if season <= 2021:
        return "2017_2021_wide_cars"
    if season <= 2025:
        return "2022_2025_ground_effect"
    return "2026_onward"
