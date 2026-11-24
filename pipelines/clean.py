"""Turn raw race extracts (FastF1-style layout) into one harmonised driver-lap table.

Rule: no row is ever dropped for being slow or unusual. Every exclusion is a
boolean flag, and `is_clean_green` combines them. Models and analyses choose
which flags to apply, so each exclusion can be reported and varied.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config

# Robust z-score cut-off for the pace-outlier flag. A sensitivity parameter, not a
# truth: analyses should report results at more than one value (see docs/methodology.md).
OUTLIER_Z = 4.0


EXCLUSION_FLAGS = [
    "flag_pit_in", "flag_pit_out", "flag_first_lap", "flag_missing_time", "flag_sc",
    "flag_vsc", "flag_red", "flag_yellow", "flag_post_neutralisation", "flag_deleted",
    "flag_not_accurate", "flag_fastf1_generated", "flag_non_slick", "flag_rain",
    "flag_beyond_scheduled",
]
# The pace-outlier flag is NOT in the default sample. On 2023-2025 data its own
# effect was tied to tyre age (highest on the first five laps of a stint, rising
# again past 30 laps), and slow laps in traffic are real laps a forecaster must
# predict. It is kept as a sensitivity sample: is_clean_green_strict.
STRICT_FLAGS = EXCLUSION_FLAGS + ["flag_pace_outlier"]


def _secs(s: pd.Series) -> pd.Series:
    if pd.api.types.is_timedelta64_dtype(s):
        return s.dt.total_seconds()
    return pd.to_numeric(s, errors="coerce")


def _bool(s: pd.Series | None, n: int, default: bool = False) -> pd.Series:
    if s is None:
        return pd.Series([default] * n)
    return s.astype("boolean").fillna(default).astype(bool).reset_index(drop=True)


def parse_track_status(status: pd.Series) -> pd.DataFrame:
    """FastF1 lap TrackStatus is a string of every status code seen during the lap, e.g. '41'."""
    s = status.astype("string").fillna("")
    return pd.DataFrame({
        "flag_yellow": s.str.contains("2", regex=False),
        "flag_sc": s.str.contains("4", regex=False),
        "flag_red": s.str.contains("5", regex=False),
        "flag_vsc": s.str.contains("6", regex=False) | s.str.contains("7", regex=False),
        "flag_track_status_missing": s.eq(""),
    }).astype(bool)


def map_compounds(season: int, compound_raw: pd.Series) -> pd.DataFrame:
    """Map raw compound labels to a class (slick/intermediate/wet) and a relative
    SOFT/MEDIUM/HARD label.

    From 2019 FastF1 reports relative labels directly. For 2018 it may report the
    named compounds (HYPERSOFT ... SUPERHARD). Then the relative label is the rank
    among the named slicks seen at that event, which works only when exactly three
    are observed. Otherwise the relative label stays missing and is flagged.
    """
    c = compound_raw.astype("string").str.upper()
    cls = pd.Series(pd.NA, index=c.index, dtype="string")
    cls[c.isin(config.SLICK_RELATIVE) | c.isin(config.NAMED_2018_ORDER)] = "SLICK"
    cls[c == "INTERMEDIATE"] = "INTERMEDIATE"
    cls[c == "WET"] = "WET"

    rel = pd.Series(pd.NA, index=c.index, dtype="string")
    method = pd.Series("missing", index=c.index, dtype="string")

    named_only = set(c.dropna()) & (set(config.NAMED_2018_ORDER) - set(config.SLICK_RELATIVE))
    if season == 2018 and named_only:
        observed = [x for x in config.NAMED_2018_ORDER if x in set(c.dropna())]
        if len(observed) == 3:
            lut = dict(zip(observed, config.SLICK_RELATIVE))
            hit = c.isin(lut.keys())
            rel[hit] = c[hit].map(lut)
            method[hit] = "rank_of_observed_2018"
        else:
            method[c.isin(config.NAMED_2018_ORDER)] = f"ambiguous_{len(observed)}_named_observed"
    else:
        hit = c.isin(config.SLICK_RELATIVE)
        rel[hit] = c[hit]
        method[hit] = "reported"
    wet = c.isin(config.WET_COMPOUNDS)
    rel[wet] = c[wet]
    method[wet] = "reported"
    return pd.DataFrame({"compound_raw": c, "compound_class": cls,
                         "compound_relative": rel, "compound_map_method": method})


def robust_outlier_flag(df: pd.DataFrame, z: float = OUTLIER_Z) -> pd.Series:
    """Flag laps far from their driver-stint trend among otherwise usable laps.

    Uses the whole stint, so it is a retrospective sample-selection flag. It must
    never be used as a model feature.
    """
    cand = ~(df["flag_pit_in"] | df["flag_pit_out"] | df["flag_first_lap"] | df["flag_sc"]
             | df["flag_vsc"] | df["flag_red"] | df["flag_yellow"]
             | df["flag_post_neutralisation"] | df["flag_beyond_scheduled"]
             | df["lap_time_s"].isna())
    flag = pd.Series(False, index=df.index)
    sub = df[cand]
    if sub.empty:
        return flag
    # Residuals from a robust (Theil-Sen) line on lap number within each stint, so the
    # spread is measured from lap-to-lap noise, not from the pace trend (tyre wear,
    # fuel burn). Laps already excluded for another reason (pit, SC/VSC/red, yellow,
    # restart lap) are left out of the fit.
    resid = pd.Series(np.nan, index=sub.index)
    for _, g in sub.groupby(["driver", "stint"]):
        if len(g) < 5:
            continue
        x = g["lap_number"].to_numpy(float)
        y = g["lap_time_s"].to_numpy(float)
        i, j = np.triu_indices(len(x), k=1)
        dx = x[j] - x[i]
        ok = dx != 0
        slope = np.median((y[j] - y[i])[ok] / dx[ok]) if ok.any() else 0.0
        r = y - slope * x
        r = r - np.median(r)
        mad = np.median(np.abs(r))
        if mad == 0:
            continue
        resid.loc[g.index] = np.abs(r) / (1.4826 * mad)
    flag.loc[sub.index] = resid > z
    return flag.fillna(False).astype(bool)


def merge_weather_backward(laps: pd.DataFrame, weather: pd.DataFrame | None) -> pd.DataFrame:
    """Attach the latest weather sample taken at or before each lap's start."""
    cols = {"AirTemp": "air_temp_c", "TrackTemp": "track_temp_c", "Humidity": "humidity_pct",
            "Pressure": "pressure_mbar", "Rainfall": "rainfall", "WindSpeed": "wind_speed_ms"}
    if weather is None or weather.empty or "Time" not in weather.columns:
        out = laps.copy()
        for v in cols.values():
            out[v] = np.nan
        out["weather_age_s"] = np.nan
        return out
    w = weather.copy()
    w["weather_time_s"] = _secs(w["Time"])
    w = w.rename(columns=cols)
    keep = ["weather_time_s"] + [v for v in cols.values() if v in w.columns]
    w = w[keep].dropna(subset=["weather_time_s"]).sort_values("weather_time_s")
    left = laps.reset_index().rename(columns={"index": "_row"})
    has_t = left["lap_start_session_s"].notna()
    merged = pd.merge_asof(left[has_t].sort_values("lap_start_session_s"), w,
                           left_on="lap_start_session_s", right_on="weather_time_s",
                           direction="backward")
    merged = pd.concat([merged, left[~has_t]], ignore_index=True).sort_values("_row")
    merged["weather_age_s"] = merged["lap_start_session_s"] - merged["weather_time_s"]
    for v in cols.values():
        if v not in merged.columns:
            merged[v] = np.nan
    return merged.drop(columns=["_row", "weather_time_s"]).reset_index(drop=True)


def clean_session(raw: dict, outlier_z: float = OUTLIER_Z) -> pd.DataFrame:
    meta = raw["meta"]
    laps = raw["laps"].reset_index(drop=True)
    n = len(laps)
    season, rnd = int(meta["season"]), int(meta["round"])

    df = pd.DataFrame({
        "season": season,
        "round": rnd,
        "race_id": f"{season}_{rnd:02d}",
        "event_name": meta["event_name"],
        "regulation_era": config.regulation_era(season),
        "scheduled_laps": meta.get("scheduled_laps"),
        "scheduled_laps_source": meta.get("scheduled_laps_source", "unknown"),
        "driver": laps["Driver"].astype("string"),
        "driver_number": laps["DriverNumber"].astype("string"),
        "team": laps["Team"].astype("string"),
        "lap_number": pd.to_numeric(laps["LapNumber"], errors="coerce").astype("Int64"),
        "stint": pd.to_numeric(laps["Stint"], errors="coerce").astype("Int64"),
        "tyre_life": pd.to_numeric(laps["TyreLife"], errors="coerce"),
        "fresh_tyre": laps["FreshTyre"].astype("boolean") if "FreshTyre" in laps else pd.NA,
        "lap_time_s": _secs(laps["LapTime"]),
        "s1_s": _secs(laps["Sector1Time"]) if "Sector1Time" in laps else np.nan,
        "s2_s": _secs(laps["Sector2Time"]) if "Sector2Time" in laps else np.nan,
        "s3_s": _secs(laps["Sector3Time"]) if "Sector3Time" in laps else np.nan,
        "lap_start_session_s": _secs(laps["LapStartTime"]),
        "lap_end_session_s": _secs(laps["Time"]),
        "position_end_of_lap": pd.to_numeric(laps.get("Position"), errors="coerce"),
        "track_status_raw": laps["TrackStatus"].astype("string"),
    })
    df = pd.concat([df, map_compounds(season, laps["Compound"]).reset_index(drop=True)], axis=1)
    df = pd.concat([df, parse_track_status(laps["TrackStatus"])], axis=1)

    df["flag_pit_in"] = laps["PitInTime"].notna().to_numpy()
    df["flag_pit_out"] = laps["PitOutTime"].notna().to_numpy()
    df["flag_first_lap"] = (df["lap_number"] == 1).fillna(False).to_numpy()
    df["flag_missing_time"] = df["lap_time_s"].isna()
    df["flag_deleted"] = _bool(laps.get("Deleted"), n).to_numpy()
    df["flag_not_accurate"] = ~_bool(laps.get("IsAccurate"), n, default=True).to_numpy()
    df["flag_fastf1_generated"] = _bool(laps.get("FastF1Generated"), n).to_numpy()
    df["flag_non_slick"] = df["compound_class"].ne("SLICK").fillna(True).astype(bool)
    df["flag_compound_relative_missing"] = df["compound_relative"].isna()
    sched = pd.to_numeric(df["scheduled_laps"], errors="coerce")
    df["flag_beyond_scheduled"] = (df["lap_number"].astype(float) > sched).fillna(False).astype(bool)

    df = df.sort_values(["driver", "lap_number"]).reset_index(drop=True)
    neutral = df["flag_sc"] | df["flag_vsc"] | df["flag_red"]
    df["flag_post_neutralisation"] = (
        neutral.groupby(df["driver"]).shift(1).astype("boolean").fillna(False).astype(bool) & ~neutral)

    # Grid position is known before the start; final results are deliberately not joined.
    res = raw.get("results")
    if res is not None and len(res) and "GridPosition" in res.columns:
        grid = res[["DriverNumber", "GridPosition"]].astype({"DriverNumber": "string"})
        grid = grid.rename(columns={"DriverNumber": "driver_number", "GridPosition": "grid_position"})
        df = df.merge(grid, on="driver_number", how="left")
    else:
        df["grid_position"] = np.nan

    df = merge_weather_backward(df, raw.get("weather"))
    df["flag_rain"] = df["rainfall"].astype("boolean").fillna(False).astype(bool)

    df["flag_pace_outlier"] = robust_outlier_flag(df, outlier_z)
    exclusion = STRICT_FLAGS
    df["is_clean_green"] = ~df[EXCLUSION_FLAGS].any(axis=1)
    df["is_clean_green_strict"] = ~df[STRICT_FLAGS].any(axis=1)
    df["exclusion_reason"] = df[exclusion].apply(
        lambda r: ";".join(c.removeprefix("flag_") for c in exclusion if r[c]), axis=1)
    return df.sort_values(["driver", "lap_number"]).reset_index(drop=True)

