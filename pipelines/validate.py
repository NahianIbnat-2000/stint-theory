"""Checks on raw race extracts (FastF1-style layout). Nothing here changes data; it only reports.

Severity levels:
  error   - the session should not enter the research sample until fixed
  warning - usable, but the affected rows are flagged downstream
  info    - descriptive coverage facts
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd

from . import config

REQUIRED_LAP_COLUMNS = [
    "Driver", "DriverNumber", "Team", "LapNumber", "LapTime", "Stint",
    "Compound", "TyreLife", "PitInTime", "PitOutTime", "TrackStatus",
    "LapStartTime", "Time",
]
OPTIONAL_LAP_COLUMNS = [
    "Sector1Time", "Sector2Time", "Sector3Time", "FreshTyre", "Position",
    "Deleted", "FastF1Generated",
]
KNOWN_COMPOUNDS = set(config.SLICK_RELATIVE) | set(config.WET_COMPOUNDS) | set(
    config.NAMED_2018_ORDER) | {"UNKNOWN", "TEST_UNKNOWN"}


@dataclass
class Issue:
    check: str
    severity: str
    count: int
    detail: str = ""


def _secs(s: pd.Series) -> pd.Series:
    if pd.api.types.is_timedelta64_dtype(s):
        return s.dt.total_seconds()
    return pd.to_numeric(s, errors="coerce")


def validate_laps(laps: pd.DataFrame | None, scheduled_laps: int | None = None) -> list[Issue]:
    issues: list[Issue] = []
    if laps is None or laps.empty:
        return [Issue("laps_present", "error", 0, "no lap rows")]

    missing = [c for c in REQUIRED_LAP_COLUMNS if c not in laps.columns]
    if missing:
        issues.append(Issue("required_columns", "error", len(missing), ", ".join(missing)))
        return issues
    absent_opt = [c for c in OPTIONAL_LAP_COLUMNS if c not in laps.columns]
    if absent_opt:
        issues.append(Issue("optional_columns", "warning", len(absent_opt), ", ".join(absent_opt)))

    n = len(laps)
    issues.append(Issue("lap_rows", "info", n))

    dup = laps.duplicated(subset=["Driver", "LapNumber"], keep=False).sum()
    if dup:
        issues.append(Issue("duplicate_driver_lap", "error", int(dup)))

    ln = pd.to_numeric(laps["LapNumber"], errors="coerce")
    bad_ln = int((ln.isna() | (ln < 1) | (ln % 1 != 0)).sum())
    if bad_ln:
        issues.append(Issue("lap_number_invalid", "error", bad_ln))

    lt = _secs(laps["LapTime"])
    n_missing = int(lt.isna().sum())
    issues.append(Issue("lap_time_missing", "warning" if n_missing else "info", n_missing,
                        f"{n_missing / n:.1%} of rows"))
    nonpos = int((lt <= 0).sum())
    if nonpos:
        issues.append(Issue("lap_time_nonpositive", "error", nonpos))

    if all(c in laps.columns for c in ("Sector1Time", "Sector2Time", "Sector3Time")):
        ssum = sum(_secs(laps[c]) for c in ("Sector1Time", "Sector2Time", "Sector3Time"))
        both = ssum.notna() & lt.notna()
        gap = (ssum[both] - lt[both]).abs()
        bad = int((gap > 0.1).sum())
        if bad:
            issues.append(Issue("sector_sum_mismatch_gt_0.1s", "warning", bad))

    comp = laps["Compound"].astype("string").str.upper()
    n_nocomp = int(comp.isna().sum())
    if n_nocomp:
        issues.append(Issue("compound_missing", "warning", n_nocomp))
    unknown = comp.dropna()[~comp.dropna().isin(KNOWN_COMPOUNDS)]
    if len(unknown):
        issues.append(Issue("compound_unrecognised", "warning", int(len(unknown)),
                            ", ".join(sorted(unknown.unique())[:10])))
    n_unk = int(comp.isin(["UNKNOWN", "TEST_UNKNOWN"]).sum())
    if n_unk:
        issues.append(Issue("compound_unknown_label", "warning", n_unk))

    tl = pd.to_numeric(laps["TyreLife"], errors="coerce")
    if tl.isna().any():
        issues.append(Issue("tyre_life_missing", "warning", int(tl.isna().sum())))

    # Tyre life should rise by exactly one lap per lap within a driver-stint.
    d = laps.assign(_ln=ln, _tl=tl).sort_values(["Driver", "_ln"])
    g = d.groupby(["Driver", "Stint"], dropna=True)
    step_ln = g["_ln"].diff()
    step_tl = g["_tl"].diff()
    jumps = int(((step_ln == 1) & step_tl.notna() & (step_tl != 1)).sum())
    if jumps:
        issues.append(Issue("tyre_life_step_not_one", "warning", jumps))

    stint_back = int((d.groupby("Driver")["Stint"].diff() < 0).sum())
    if stint_back:
        issues.append(Issue("stint_decreasing", "error", stint_back))

    multi_team = int((laps.groupby("Driver")["Team"].nunique() > 1).sum())
    if multi_team:
        issues.append(Issue("driver_multiple_teams", "warning", multi_team))

    status = laps["TrackStatus"].astype("string")
    if status.isna().all():
        issues.append(Issue("track_status_missing", "error", n))

    if scheduled_laps:
        leader = int(ln.max())
        if leader < scheduled_laps:
            issues.append(Issue("race_shorter_than_scheduled", "warning", scheduled_laps - leader,
                                f"leader laps {leader} vs scheduled {scheduled_laps}"))
        elif leader > scheduled_laps:
            # warning, not error: those laps get flag_beyond_scheduled and leave the
            # clean sample; the cause (extra lap rows or a short distance) is checked
            # with `python -m pipelines diagnose`
            n_rows = int((ln > scheduled_laps).sum())
            issues.append(Issue("laps_exceed_scheduled", "warning", n_rows,
                                f"max lap {leader} vs scheduled {scheduled_laps}"))
    else:
        issues.append(Issue("scheduled_laps_missing", "warning", 1))

    return issues


def validate_weather(weather: pd.DataFrame | None) -> list[Issue]:
    if weather is None or weather.empty:
        return [Issue("weather_present", "warning", 0, "no weather rows")]
    issues = [Issue("weather_rows", "info", len(weather))]
    for col in ("AirTemp", "TrackTemp", "Rainfall", "Humidity"):
        if col not in weather.columns:
            issues.append(Issue(f"weather_{col}_absent", "warning", 1))
        elif weather[col].isna().any():
            issues.append(Issue(f"weather_{col}_missing", "warning", int(weather[col].isna().sum())))
    return issues


# Share of the laps the results say were driven that must exist as lap rows.
# Below this the race is excluded: field-pace and position features need the
# whole field. Set after Miami 2025 arrived with about half its laps missing.
MIN_LAP_COMPLETENESS = 0.9


def lap_completeness(laps: pd.DataFrame | None, results: pd.DataFrame | None) -> float | None:
    """Lap rows present / laps driven according to the classification (per driver,
    capped at the classified lap count). None if the results have no lap counts."""
    if laps is None or results is None or "Laps" not in results.columns or laps.empty:
        return None
    exp = pd.to_numeric(results.set_index(results["DriverNumber"].astype(str))["Laps"],
                        errors="coerce").dropna()
    if exp.sum() <= 0:
        return None
    have = laps.assign(DN=laps["DriverNumber"].astype(str)).groupby("DN")["LapNumber"].nunique()
    got = sum(min(have.get(d, 0), n) for d, n in exp.items())
    return float(got / exp.sum())


def validate_session(raw: dict) -> dict:
    meta = raw["meta"]
    issues = validate_laps(raw.get("laps"), meta.get("scheduled_laps"))
    comp = lap_completeness(raw.get("laps"), raw.get("results"))
    if comp is not None:
        sev = "error" if comp < MIN_LAP_COMPLETENESS else ("warning" if comp < 0.98 else "info")
        issues.append(Issue("lap_completeness", sev, int(round(comp * 1000)),
                            f"{comp:.1%} of classified laps present"))
    issues += validate_weather(raw.get("weather"))
    if raw.get("results") is None or len(raw["results"]) == 0:
        issues.append(Issue("results_present", "warning", 0))
    errors = [i for i in issues if i.severity == "error"]
    return {
        "season": meta["season"],
        "round": meta["round"],
        "event_name": meta["event_name"],
        "passed": not errors,
        "lap_completeness": comp,
        "issues": [asdict(i) for i in issues],
    }


def summarise(reports: list[dict]) -> pd.DataFrame:
    rows = []
    for r in reports:
        for i in r["issues"]:
            rows.append({"season": r["season"], "round": r["round"],
                         "event_name": r["event_name"], **i})
    return pd.DataFrame(rows)


def sessions_passing(reports: list[dict]) -> set[tuple[int, int]]:
    return {(r["season"], r["round"]) for r in reports if r["passed"]}


__all__ = ["Issue", "validate_laps", "validate_weather", "validate_session", "summarise",
           "sessions_passing"]
