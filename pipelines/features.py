"""Leakage-safe features for next-lap prediction (Task 1).

One row = one prediction origin: the end of lap t for one driver.
Target = that driver's lap t+1 time, conditional on staying out on the same stint.

Information rule: a feature for origin (driver, t) may use only
  * the driver's own laps 1..t,
  * other drivers' laps that ended at or before the end of lap t (session clock),
  * weather samples at or before the start of lap t,
  * facts fixed before the race (grid position, scheduled laps, season, circuit).

Flags that need hindsight (pace outlier, lap deleted, FastF1 IsAccurate) are used
only to choose which targets are scored, never as inputs. tests/test_leakage.py
checks this by changing the future and confirming that features do not move.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# Flags a pit wall would know by the end of the lap. Used to decide which past laps
# feed the pace features.
REALTIME_FLAGS = [
    "flag_pit_in", "flag_pit_out", "flag_first_lap", "flag_missing_time", "flag_sc",
    "flag_vsc", "flag_red", "flag_yellow", "flag_post_neutralisation", "flag_non_slick",
    "flag_rain", "flag_beyond_scheduled",
]
FIELD_WINDOW_S = 120.0  # other drivers' green laps that ended in the last 2 minutes

ID_COLUMNS = ["race_id", "season", "round", "event_name", "regulation_era", "driver",
              "team", "lap_number", "stint"]
FEATURE_COLUMNS = [
    # own recent pace
    "lt_lag0", "lt_lag1", "last_green_lt", "roll_mean_green_3", "roll_std_green_5",
    "trend_slope_green_5", "green_laps_in_stint",
    # tyre state
    "compound_relative", "tyre_life", "target_tyre_life", "fresh_tyre", "prev_stint_compound",
    "pit_stops_so_far",
    # race state
    "lap_number", "scheduled_laps", "race_progress", "laps_remaining_sched",
    "position_end_of_lap", "grid_position",
    "flag_sc", "flag_vsc", "flag_yellow", "flag_post_neutralisation",
    # environment
    "track_temp_c", "air_temp_c", "humidity_pct",
    # field context
    "field_green_median_recent", "rel_pace_to_field",
]
# Per-lap state known at the end of each lap, used to build lap sequences for the
# Phase 3 sequence models. Not used by the Phase 2 models (they list inputs explicitly).
SEQUENCE_COLUMNS = ["flag_pit_in", "flag_pit_out", "flag_red", "is_rt_green"]
TARGET_COLUMNS = ["y_next_lap_time_s", "target_lap_number", "target_valid", "target_valid_strict"]


def _rolling_on_valid(values: pd.Series, window: int, fn: str) -> pd.Series:
    """Rolling stat over the last `window` non-missing values, carried forward."""
    v = values.dropna()
    if v.empty:
        return pd.Series(np.nan, index=values.index)
    r = getattr(v.rolling(window, min_periods=1 if fn == "mean" else 2), fn)()
    return r.reindex(values.index).ffill()


def _rolling_slope(tl: pd.Series, lt: pd.Series, window: int = 5) -> pd.Series:
    ok = lt.notna() & tl.notna()
    x, y = tl[ok].to_numpy(float), lt[ok].to_numpy(float)
    out = np.full(len(x), np.nan)
    for i in range(len(x)):
        lo = max(0, i - window + 1)
        xs, ys = x[lo:i + 1], y[lo:i + 1]
        if len(xs) >= 3 and np.ptp(xs) > 0:
            out[i] = np.polyfit(xs, ys, 1)[0]
    s = pd.Series(out, index=lt[ok].index)
    return s.reindex(lt.index).ffill()


def _field_reference(race: pd.DataFrame, window_s: float = FIELD_WINDOW_S) -> pd.Series:
    """Median of other drivers' real-time-green laps that ended in (end_t - w, end_t]."""
    g = race[race["_rt_green"] & race["lap_end_session_s"].notna()].sort_values("lap_end_session_s")
    ends = g["lap_end_session_s"].to_numpy()
    times = g["lap_time_s"].to_numpy()
    drivers = g["driver"].astype(str).to_numpy()
    out = np.full(len(race), np.nan)
    end_t = race["lap_end_session_s"].to_numpy()
    me = race["driver"].astype(str).to_numpy()
    for i in range(len(race)):
        if np.isnan(end_t[i]):
            continue
        lo = np.searchsorted(ends, end_t[i] - window_s, side="right")
        hi = np.searchsorted(ends, end_t[i], side="right")
        sel = times[lo:hi][drivers[lo:hi] != me[i]]
        if len(sel):
            out[i] = np.median(sel)
    return pd.Series(out, index=race.index)


def build_race_features(race: pd.DataFrame) -> pd.DataFrame:
    race = race.sort_values(["driver", "lap_number"]).reset_index(drop=True).copy()
    race["_rt_green"] = ~race[REALTIME_FLAGS].any(axis=1)
    race["_rt_lt"] = race["lap_time_s"].where(race["_rt_green"])

    parts = []
    for (_, _), g in race.groupby(["driver", "stint"], sort=False, dropna=False):
        f = pd.DataFrame(index=g.index)
        f["last_green_lt"] = g["_rt_lt"].ffill()
        f["roll_mean_green_3"] = _rolling_on_valid(g["_rt_lt"], 3, "mean")
        f["roll_std_green_5"] = _rolling_on_valid(g["_rt_lt"], 5, "std")
        f["trend_slope_green_5"] = _rolling_slope(g["tyre_life"], g["_rt_lt"], 5)
        f["green_laps_in_stint"] = g["_rt_green"].cumsum()
        parts.append(f)
    race = race.join(pd.concat(parts))

    by_drv = race.groupby("driver", sort=False)
    race["lt_lag0"] = race["lap_time_s"]
    race["lt_lag1"] = by_drv["lap_time_s"].shift(1)
    race["pit_stops_so_far"] = (race["stint"].astype("float") - 1).clip(lower=0)

    stint_comp = (race.groupby(["driver", "stint"])["compound_relative"].first()
                  .groupby(level="driver").shift(1).rename("prev_stint_compound"))
    race = race.merge(stint_comp.reset_index(), on=["driver", "stint"], how="left")

    sched = pd.to_numeric(race["scheduled_laps"], errors="coerce")
    race["race_progress"] = race["lap_number"].astype(float) / sched
    race["laps_remaining_sched"] = sched - race["lap_number"].astype(float)

    race["field_green_median_recent"] = _field_reference(race)
    race["rel_pace_to_field"] = race["roll_mean_green_3"] - race["field_green_median_recent"]

    # target: next lap of the same driver, same stint, scored only if it is a clean green lap
    by_drv = race.groupby("driver", sort=False)
    nxt_lap = by_drv["lap_number"].shift(-1)
    nxt_stint = by_drv["stint"].shift(-1)
    race["y_next_lap_time_s"] = by_drv["lap_time_s"].shift(-1)
    race["target_lap_number"] = nxt_lap
    race["target_tyre_life"] = race["tyre_life"] + 1
    race["target_valid"] = (
        (nxt_lap == race["lap_number"] + 1).fillna(False)
        & (nxt_stint == race["stint"]).fillna(False)
        & by_drv["is_clean_green"].shift(-1).astype("boolean").fillna(False).astype(bool)
        & race["y_next_lap_time_s"].notna()
    ).astype(bool)
    race["target_valid_strict"] = race["target_valid"] & by_drv["is_clean_green_strict"].shift(-1) \
        .astype("boolean").fillna(False).astype(bool)
    race["is_rt_green"] = race["_rt_green"]
    return race.drop(columns=["_rt_green", "_rt_lt"])


def build_features(clean: pd.DataFrame) -> pd.DataFrame:
    out = [build_race_features(g) for _, g in clean.groupby("race_id", sort=True)]
    df = pd.concat(out, ignore_index=True)
    keep = ID_COLUMNS + [c for c in FEATURE_COLUMNS if c not in ID_COLUMNS] + \
        SEQUENCE_COLUMNS + TARGET_COLUMNS
    return df[keep]
