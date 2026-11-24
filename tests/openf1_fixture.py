"""Turn the synthetic race (fixtures.make_raw_race) into fake OpenF1 API payloads.

TEST FIXTURE ONLY. Lets the adapter be checked against a race whose true laps,
stints, pit stops and safety-car laps are known exactly.
"""
from __future__ import annotations

import pandas as pd

from fixtures import SC_LAPS, make_raw_race

T0 = pd.Timestamp("2023-03-05T15:00:00Z")
DELETED = ("11", 20)  # driver number, lap


def iso(seconds: float) -> str:
    return (T0 + pd.Timedelta(seconds=float(seconds))).isoformat()


def openf1_payloads(season=2023, rnd=1, session_key=9000, seed=0) -> dict:
    raw = make_raw_race(season, rnd, seed=seed)
    L = raw["laps"]
    s = lambda col: L[col].dt.total_seconds()
    start, end, dur = s("LapStartTime"), s("Time"), s("LapTime")

    laps = [{
        "session_key": session_key, "driver_number": int(r.DriverNumber),
        "lap_number": int(r.LapNumber), "date_start": iso(start[i]),
        "lap_duration": float(dur[i]),
        "duration_sector_1": r.Sector1Time.total_seconds(),
        "duration_sector_2": r.Sector2Time.total_seconds(),
        "duration_sector_3": r.Sector3Time.total_seconds(),
        "is_pit_out_lap": bool(pd.notna(r.PitOutTime)),
    } for i, r in L.iterrows()]

    stints = []
    for (dn, st), g in L.groupby(["DriverNumber", "Stint"]):
        stints.append({"driver_number": int(dn), "stint_number": int(st),
                       "lap_start": int(g.LapNumber.min()), "lap_end": int(g.LapNumber.max()),
                       "compound": g.Compound.iloc[0], "tyre_age_at_start": 0})
    drivers = [{"driver_number": int(dn), "name_acronym": g.Driver.iloc[0],
                "team_name": g.Team.iloc[0]} for dn, g in L.groupby("DriverNumber")]
    pits = [{"driver_number": int(r.DriverNumber), "lap_number": int(r.LapNumber),
             "date": iso(end[i]), "lane_duration": 22.0}
            for i, r in L.iterrows() if pd.notna(r.PitInTime)]
    positions = [{"driver_number": int(r.DriverNumber), "position": int(r.Position),
                  "date": iso(end[i] - 0.5)} for i, r in L.iterrows()]

    lap_start = lambda n: start[L.LapNumber == n]
    lap_end = lambda n: end[L.LapNumber == n]
    sc_on = lap_start(SC_LAPS[0]).max() + 0.01
    sc_in = lap_end(SC_LAPS[-1]).min() - 0.01
    rc = [
        {"date": iso(sc_on), "category": "SafetyCar", "flag": None, "scope": "Track",
         "sector": None, "message": "SAFETY CAR DEPLOYED"},
        {"date": iso(sc_in), "category": "SafetyCar", "flag": None, "scope": "Track",
         "sector": None, "message": "SAFETY CAR IN THIS LAP"},
        {"date": iso(sc_in + 200), "category": "Other", "flag": None, "scope": None,
         "sector": None,
         "message": f"CAR {DELETED[0]} (D01) TIME 1:30.123 DELETED - TRACK LIMITS AT TURN 4 "
                    f"LAP {DELETED[1]} 15:40:00"},
    ]
    weather = raw["weather"]
    wx = [{"date": iso(t.total_seconds()), "air_temperature": a, "track_temperature": tt,
           "humidity": h, "pressure": p, "rainfall": 0, "wind_speed": ws, "wind_direction": 0}
          for t, a, tt, h, p, ws in zip(weather.Time, weather.AirTemp, weather.TrackTemp,
                                        weather.Humidity, weather.Pressure, weather.WindSpeed)]
    n = L.LapNumber.max()
    result = [{"driver_number": int(dn), "position": int(raw["results"].Position[k]),
               "number_of_laps": int(n), "dnf": False, "dns": False, "dsq": False}
              for k, dn in enumerate(raw["results"].DriverNumber)]
    grid = [{"driver_number": int(dn), "position": int(gp)}
            for dn, gp in zip(raw["results"].DriverNumber, raw["results"].GridPosition)]
    return {"laps": laps, "stints": stints, "drivers": drivers, "pit": pits,
            "position": positions, "race_control": rc, "weather": wx,
            "session_result": result, "starting_grid": grid, "_raw": raw}


class FakeClient:
    """Stands in for OpenF1Client; serves payloads for two races per season."""

    def __init__(self, seasons=(2023,), rounds=(1, 2)):
        self.calls = 0
        self.cache_hits = 0
        self.races = {}
        for season in seasons:
            for rnd in rounds:
                key = season * 100 + rnd
                self.races[key] = (season, rnd, openf1_payloads(season, rnd, key, seed=rnd))

    def get(self, endpoint, **params):
        self.calls += 1
        if endpoint == "sessions":
            return [{"session_key": k, "meeting_key": k, "session_name": "Race",
                     "session_type": "Race", "year": s,
                     "date_start": (T0 + pd.Timedelta(days=14 * r)).isoformat(),
                     "date_end": (T0 + pd.Timedelta(days=14 * r, hours=2)).isoformat(),
                     "is_cancelled": False, "circuit_short_name": f"C{r}",
                     "country_name": "Testland", "location": "X"}
                    for k, (s, r, _) in self.races.items() if s == params["year"]] + [
                {"session_key": 1, "meeting_key": 1, "session_name": "Sprint",
                 "session_type": "Race", "year": params["year"],
                 "date_start": T0.isoformat(), "is_cancelled": False}]
        if endpoint == "meetings":
            return [{"meeting_key": k, "meeting_name": f"Test {r} Grand Prix"}
                    for k, (s, r, _) in self.races.items() if s == params["year"]]
        key = params["session_key"]
        s, r, p = self.races[key]
        if endpoint in ("laps", "stints", "drivers", "pit", "position", "race_control",
                        "weather", "session_result", "starting_grid"):
            # every race's clock starts at its own session date_start
            if endpoint in ("laps", "pit", "position", "race_control", "weather"):
                shift = pd.Timedelta(days=14 * r)
                field = "date_start" if endpoint == "laps" else "date"
                return [{**row, field: (pd.Timestamp(row[field]) + shift).isoformat()}
                        for row in p[endpoint]]
            return p[endpoint]
        return []
