"""Synthetic race in FastF1's raw table shapes.

TEST FIXTURE ONLY. These numbers are invented to exercise the code paths. They are
never written to data/ and must never appear in reports or on the website.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

SC_LAPS = (12, 13)


def make_raw_race(season: int = 2023, rnd: int = 1, n_drivers: int = 4, n_laps: int = 30,
                  seed: int = 0, compounds=("MEDIUM", "HARD")) -> dict:
    rng = np.random.default_rng(seed)
    rows = []
    for d in range(n_drivers):
        code = f"D{d:02d}"
        pit_lap = 10 + 3 * d          # each driver stops once, on a different lap
        t = 5.0 + 0.4 * d              # grid stagger on the session clock
        stint, tyre = 1, 0
        for lap in range(1, n_laps + 1):
            tyre += 1
            base = 90 + 0.5 * d + 0.06 * tyre - 0.05 * lap
            lt = base + rng.normal(0, 0.15)
            if lap == 1:
                lt += 6
            if lap in SC_LAPS:
                lt += 25
            if lap == pit_lap:
                lt += 18
            if lap == pit_lap + 1:
                lt += 4
            start = t
            t = t + lt
            rows.append({
                "Time": pd.Timedelta(seconds=t), "Driver": code, "DriverNumber": str(10 + d),
                "LapTime": pd.Timedelta(seconds=lt), "LapNumber": float(lap), "Stint": float(stint),
                "PitOutTime": pd.Timedelta(seconds=start) if (lap == pit_lap + 1) else pd.NaT,
                "PitInTime": pd.Timedelta(seconds=t - 2) if lap == pit_lap else pd.NaT,
                "Sector1Time": pd.Timedelta(seconds=lt * 0.3),
                "Sector2Time": pd.Timedelta(seconds=lt * 0.4),
                "Sector3Time": pd.Timedelta(seconds=lt * 0.3),
                "Compound": compounds[stint - 1], "TyreLife": float(tyre), "FreshTyre": True,
                "Team": f"Team{d // 2}", "LapStartTime": pd.Timedelta(seconds=start),
                "TrackStatus": "4" if lap in SC_LAPS else "1", "Position": float(d + 1),
                "Deleted": False, "IsAccurate": lap not in SC_LAPS and lap != 1,
                "FastF1Generated": False,
            })
            if lap == pit_lap:
                stint, tyre = 2, 0
    laps = pd.DataFrame(rows)
    end = laps["Time"].max().total_seconds()
    wt = np.arange(0, end + 60, 60.0)
    weather = pd.DataFrame({
        "Time": pd.to_timedelta(wt, unit="s"), "AirTemp": 25 + wt / 3600,
        "TrackTemp": 40 + wt / 1800, "Humidity": 50.0, "Pressure": 1010.0,
        "Rainfall": False, "WindDirection": 0, "WindSpeed": 1.0,
    })
    results = pd.DataFrame({"DriverNumber": [str(10 + d) for d in range(n_drivers)],
                            "GridPosition": [float(d + 1) for d in range(n_drivers)],
                            "Position": [float(n_drivers - d) for d in range(n_drivers)]})
    meta = {"season": season, "round": rnd, "event_name": "Test Grand Prix",
            "scheduled_laps": n_laps,
            "scheduled_laps_source": "fixture"}
    return {"meta": meta, "laps": laps, "weather": weather, "results": results,
            "track_status": None, "race_control": None}
