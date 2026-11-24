"""OpenF1 client and adapter.

The client throttles requests and caches every response on disk, so a rebuild
never re-downloads. The adapter turns OpenF1 endpoints into the same raw table
layout the rest of the pipeline expects (FastF1-style column names), so cleaning,
features and validation do not depend on the source.

Field names follow https://openf1.org/docs. OpenF1 has no per-lap track status,
no FastF1 accuracy flag and no scheduled distance; how each is replaced is
documented next to the code below and in docs/methodology.md.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import logging
import re
import time
from pathlib import Path
from urllib.parse import urlencode

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

BASE_URL = "https://api.openf1.org/v1/"


# --------------------------------------------------------------------------- client
class OpenF1Client:
    """GET wrapper with a minimum gap between calls, retries and a JSON disk cache.

    OpenF1's free tier is reported to allow about 3 requests/s and 30/min; the
    default 2.1 s gap keeps under 30/min.
    """

    def __init__(self, cache_dir: Path, min_interval_s: float = 2.1, max_retries: int = 6,
                 http=None):
        self.cache_dir = Path(cache_dir) / "openf1"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.min_interval_s = min_interval_s
        self.max_retries = max_retries
        self._last = 0.0
        if http is None:
            import requests
            http = requests.Session()
            http.headers["User-Agent"] = "stint-theory research pipeline"
        self.http = http
        self.calls = 0
        self.cache_hits = 0

    def _path(self, url: str) -> Path:
        return self.cache_dir / f"{hashlib.sha1(url.encode()).hexdigest()}.json"

    def get(self, endpoint: str, **params) -> list[dict]:
        url = BASE_URL + endpoint + ("?" + urlencode(sorted(params.items())) if params else "")
        path = self._path(url)
        if path.exists():
            self.cache_hits += 1
            return json.loads(path.read_text())["data"]
        delay = 5.0
        for attempt in range(self.max_retries):
            wait = self.min_interval_s - (time.monotonic() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()
            resp = self.http.get(url, timeout=60)
            self.calls += 1
            if resp.status_code == 404:  # OpenF1 answers 404 "No results found." for empty queries
                data = []
                break
            if resp.status_code in (429, 500, 502, 503, 504):
                ra = resp.headers.get("Retry-After")
                sleep = float(ra) if ra and ra.isdigit() else delay
                log.warning("OpenF1 %s on %s, retry in %.0fs", resp.status_code, url, sleep)
                time.sleep(sleep)
                delay *= 2
                continue
            resp.raise_for_status()
            data = resp.json()
            break
        else:
            raise RuntimeError(f"OpenF1 request failed after {self.max_retries} tries: {url}")
        path.write_text(json.dumps({
            "url": url,
            "retrieved_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "data": data}))
        return data


# ------------------------------------------------------------------------ helpers
def _df(rows: list[dict], cols: list[str]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    for c in cols:
        if c not in df.columns:
            df[c] = np.nan
    return df


def to_session_seconds(dates: pd.Series, t0: pd.Timestamp) -> pd.Series:
    """ISO-8601 UTC strings -> seconds since t0 (session scheduled start)."""
    ts = pd.to_datetime(dates, utc=True, errors="coerce", format="ISO8601")
    return (ts - t0).dt.total_seconds()


def race_sessions(client: OpenF1Client, year: int) -> pd.DataFrame:
    """Grand Prix race sessions of a year, with an ordinal round and the meeting name.

    `round` is the order of the races that were held, by start date. It can differ
    from the official round number if a cancelled event kept its number.
    """
    sess = _df(client.get("sessions", year=year, session_name="Race"),
               ["session_key", "meeting_key", "session_name", "session_type", "date_start",
                "date_end", "is_cancelled", "circuit_short_name", "country_name", "location"])
    if sess.empty:
        return sess
    sess = sess[sess["session_name"] == "Race"]
    if "is_cancelled" in sess:
        sess = sess[~sess["is_cancelled"].fillna(False).astype(bool)]
    meet = _df(client.get("meetings", year=year), ["meeting_key", "meeting_name"])
    sess = sess.merge(meet[["meeting_key", "meeting_name"]], on="meeting_key", how="left")
    sess = sess.sort_values("date_start").reset_index(drop=True)
    sess["round"] = np.arange(1, len(sess) + 1)
    sess["event_name"] = sess["meeting_name"].fillna(sess["country_name"] + " Grand Prix")
    return sess


# --------------------------------------------------------------- race control
_SC_DEPLOYED = re.compile(r"(?<!VIRTUAL )SAFETY CAR DEPLOYED")
_SC_END = re.compile(r"(?<!VIRTUAL )SAFETY CAR IN THIS LAP|(?<!VIRTUAL )SAFETY CAR ENDING")
_VSC_DEPLOYED = re.compile(r"VIRTUAL SAFETY CAR DEPLOYED|\bVSC DEPLOYED")
_VSC_END = re.compile(r"VIRTUAL SAFETY CAR ENDING|\bVSC ENDING")
# Restarts behind the safety car after a red flag or at a wet start. They come as
# "Other" messages, not as "SAFETY CAR DEPLOYED" (checked on 2023-2025 data).
_SC_RESTART_START = re.compile(
    r"RACE WILL (?:START|RESUME) BEHIND THE SAFETY CAR|ROLLING START PROCEDURE|SAFETY CAR WILL STAY OUT")
_SC_RESTART_END = re.compile(r"SAFETY CAR WILL ENTER PITS|^ROLLING START$")
# SafetyCar-category messages that carry no start or end of a period
_SC_INFO = re.compile(r"SAFETY CAR THROUGH THE PIT LANE")
_CAR = re.compile(r"\bCAR\s+(\d+)\b")
_LAP = re.compile(r"\bLAP\s+(\d+)\b")
YELLOW_MAX_S = 300.0  # cap for a sector yellow with no matching clear message


def race_control_intervals(rc: list[dict], t0: pd.Timestamp, session_end_s: float) -> tuple[pd.DataFrame, dict]:
    """Rebuild neutralisation periods from race-control messages.

    Returns intervals with FastF1-compatible codes (2 yellow, 4 SC, 5 red, 6 VSC)
    and a dict of counts used for auditing the reconstruction.
    """
    df = _df(rc, ["date", "category", "flag", "scope", "sector", "message"])
    stats = {"rc_messages": len(df), "sc_unpaired": 0, "vsc_unpaired": 0, "red_unpaired": 0,
             "yellow_capped": 0, "safetycar_msgs_unmatched": 0, "sc_restart_periods": 0,
             "vsc_upgraded_to_sc": 0, "closed_by_chequered": 0}
    if df.empty:
        return pd.DataFrame(columns=["start_s", "end_s", "code", "source"]), stats
    df["t"] = to_session_seconds(df["date"], t0)
    df = df.sort_values("t").reset_index(drop=True)
    msg = df["message"].astype("string").str.upper().fillna("")
    flag = df["flag"].astype("string").str.upper().fillna("")
    scope = df["scope"].astype("string").str.upper().fillna("")
    out = []

    msg = msg.str.strip()
    sc_s, sc_e = msg.str.contains(_SC_DEPLOYED), msg.str.contains(_SC_END)
    vsc_s, vsc_e = msg.str.contains(_VSC_DEPLOYED), msg.str.contains(_VSC_END)
    rs_e = msg.str.contains(_SC_RESTART_END)
    rs_s = msg.str.contains(_SC_RESTART_START) & ~rs_e
    is_sc_cat = df["category"].astype("string").str.upper().eq("SAFETYCAR").fillna(False)
    info = msg.str.contains(_SC_INFO)
    stats["safetycar_msgs_unmatched"] = int(
        (is_sc_cat & ~(sc_s | sc_e | vsc_s | vsc_e | info)).sum())
    track = scope.eq("TRACK")
    red_s = flag.eq("RED") & track
    red_e = flag.isin(["GREEN", "CLEAR"]) & track
    chequered = flag.eq("CHEQUERED")

    # One pass in time order. Rules, each seen in 2023-2025 races:
    # - a red flag closes a running SC or VSC (Australia 2023, Mexico 2023);
    # - a SC deployment closes a running VSC: the VSC was upgraded (British 2023,
    #   China 2024, Qatar 2024);
    # - a SC deployment or a behind-the-safety-car restart closes a red flag;
    # - the chequered flag closes everything, and nothing opens after it
    #   (Azerbaijan 2024, Australia 2024, Canada 2025; red after the flag in
    #   Australia 2023).
    opened = {"sc": None, "vsc": None, "red": None}
    codes = {"sc": "4", "vsc": "6", "red": "5"}

    def close(key, t):
        if opened[key] is not None:
            out.append((opened[key], t, codes[key], key))
            opened[key] = None

    finished = False
    for i in df.index:
        t = df.at[i, "t"]
        if chequered[i]:
            for key in opened:
                if opened[key] is not None:
                    stats["closed_by_chequered"] += 1
                    close(key, t)
            finished = True
            continue
        if finished:
            continue
        if red_s[i]:
            close("sc", t)
            close("vsc", t)
            if opened["red"] is None:
                opened["red"] = t
        elif red_e[i]:
            close("red", t)
        if (sc_s[i] or rs_s[i]) and opened["sc"] is None:
            close("red", t)
            if opened["vsc"] is not None:
                stats["vsc_upgraded_to_sc"] += 1
                close("vsc", t)
            stats["sc_restart_periods"] += int(bool(rs_s[i]))
            opened["sc"] = t
        elif sc_e[i] or rs_e[i]:
            close("sc", t)
        if vsc_s[i] and opened["vsc"] is None and opened["red"] is None and opened["sc"] is None:
            opened["vsc"] = t
        elif vsc_e[i]:
            close("vsc", t)
    for key in opened:
        if opened[key] is not None:
            stats[f"{key}_unpaired"] += 1
            close(key, session_end_s)

    # sector yellows: open per sector, closed by CLEAR/GREEN in that sector or track-wide
    open_y: dict = {}
    for i in df.index:
        f, s, sec, t = flag[i], scope[i], df.at[i, "sector"], df.at[i, "t"]
        if f in ("YELLOW", "DOUBLE YELLOW"):
            open_y.setdefault(sec if s == "SECTOR" else "track", t)
        elif f in ("CLEAR", "GREEN"):
            keys = list(open_y) if s == "TRACK" else [sec]
            for k in keys:
                if k in open_y:
                    st = open_y.pop(k)
                    if t - st > YELLOW_MAX_S:
                        stats["yellow_capped"] += 1
                    out.append((st, min(t, st + YELLOW_MAX_S), "2", "yellow"))
    for st in open_y.values():
        stats["yellow_capped"] += 1
        out.append((st, min(st + YELLOW_MAX_S, session_end_s), "2", "yellow"))

    iv = pd.DataFrame(out, columns=["start_s", "end_s", "code", "source"])
    return iv.sort_values("start_s").reset_index(drop=True), stats


def lap_track_status(start_s: pd.Series, end_s: pd.Series, intervals: pd.DataFrame) -> pd.Series:
    """FastF1-style status string per lap: '1' plus every code whose interval overlaps the lap."""
    out = []
    iv = intervals.to_numpy() if len(intervals) else np.empty((0, 4))
    for a, b in zip(start_s.to_numpy(float), end_s.to_numpy(float)):
        if np.isnan(a) or np.isnan(b):
            out.append(None)
            continue
        codes = {str(c) for s, e, c, _ in iv if s < b and e > a}
        out.append("1" + "".join(sorted(codes)))
    return pd.Series(out, index=start_s.index, dtype="string")


def deleted_laps(rc: list[dict]) -> set[tuple[str, int]]:
    """(driver_number, lap) pairs deleted by race control and not later reinstated."""
    gone: set[tuple[str, int]] = set()
    for r in sorted(rc, key=lambda r: r.get("date") or ""):
        m = str(r.get("message") or "").upper()
        car, lap = _CAR.search(m), _LAP.search(m)
        if not (car and lap):
            continue
        key = (car.group(1), int(lap.group(1)))
        if "REINSTATED" in m:
            gone.discard(key)
        elif "DELETED" in m:
            gone.add(key)
    return gone


# --------------------------------------------------------------------- laps
def build_laps(laps: list[dict], stints: list[dict], drivers: list[dict], pits: list[dict],
               positions: list[dict], status_iv: pd.DataFrame, deleted: set, t0: pd.Timestamp
               ) -> tuple[pd.DataFrame, dict]:
    L = _df(laps, ["driver_number", "lap_number", "date_start", "lap_duration",
                   "duration_sector_1", "duration_sector_2", "duration_sector_3",
                   "is_pit_out_lap"])
    if L.empty:
        return pd.DataFrame(), {"laps_without_stint": 0}
    n_in = len(L)
    L = L.dropna(subset=["driver_number", "lap_number"])
    n_no_key = n_in - len(L)
    L["DriverNumber"] = L["driver_number"].astype(int).astype(str)
    L["LapNumber"] = L["lap_number"].astype(float)
    # exact repeats of the same driver-lap are API duplicates, not laps
    n_before = len(L)
    L = L.drop_duplicates(subset=["DriverNumber", "LapNumber"], keep="first")
    n_dupes = n_before - len(L)
    L = L.sort_values(["DriverNumber", "LapNumber"]).reset_index(drop=True)

    start = to_session_seconds(L["date_start"], t0)
    dur = pd.to_numeric(L["lap_duration"], errors="coerce")
    next_start = start.groupby(L["DriverNumber"]).shift(-1)
    end = (start + dur).fillna(next_start)

    D = _df(drivers, ["driver_number", "name_acronym", "team_name"]).dropna(
        subset=["driver_number"]).drop_duplicates("driver_number")
    D["DriverNumber"] = D["driver_number"].astype(int).astype(str)
    L = L.merge(D[["DriverNumber", "name_acronym", "team_name"]], on="DriverNumber", how="left")

    # stints: one row per (driver, stint) with lap_start..lap_end
    S = _df(stints, ["driver_number", "stint_number", "lap_start", "lap_end", "compound",
                     "tyre_age_at_start"])
    stint = pd.Series(np.nan, index=L.index)
    comp = pd.Series(pd.NA, index=L.index, dtype="string")
    tyre = pd.Series(np.nan, index=L.index)
    fresh = pd.Series(pd.NA, index=L.index, dtype="boolean")
    S = S.dropna(subset=["driver_number"])
    if not S.empty:
        S["DriverNumber"] = S["driver_number"].astype(int).astype(str)
        for _, s in S.iterrows():
            if pd.isna(s["lap_start"]) or pd.isna(s["lap_end"]):
                continue
            m = ((L["DriverNumber"] == s["DriverNumber"]) & (L["LapNumber"] >= s["lap_start"])
                 & (L["LapNumber"] <= s["lap_end"]))
            stint[m] = s["stint_number"]
            comp[m] = str(s["compound"]).upper() if pd.notna(s["compound"]) else pd.NA
            age0 = s["tyre_age_at_start"]
            if pd.notna(age0):
                # FastF1 convention: first lap on a new set has TyreLife 1
                tyre[m] = age0 + (L.loc[m, "LapNumber"] - s["lap_start"]) + 1
                fresh[m] = bool(age0 == 0)

    # A lap right after a stint's lap_end, with no later stint covering it, is given
    # to that stint (OpenF1 stints sometimes stop one lap short at the flag).
    extended = 0
    if not S.empty:
        for i in L.index[stint.isna()]:
            dn, ln = L.at[i, "DriverNumber"], L.at[i, "LapNumber"]
            prev = S[(S["DriverNumber"] == dn) & (S["lap_end"] == ln - 1)]
            later = S[(S["DriverNumber"] == dn) & (S["lap_start"] >= ln)]
            if len(prev) == 1 and later.empty:
                s = prev.iloc[0]
                stint[i] = s["stint_number"]
                comp[i] = str(s["compound"]).upper() if pd.notna(s["compound"]) else pd.NA
                if pd.notna(s["tyre_age_at_start"]):
                    tyre[i] = s["tyre_age_at_start"] + (ln - s["lap_start"]) + 1
                    fresh[i] = bool(s["tyre_age_at_start"] == 0)
                extended += 1

    out_lap = L["is_pit_out_lap"].astype("boolean").fillna(False).astype(bool)
    # in-lap = the lap before an out-lap (same driver); lap 1 out-laps are pit-lane starts
    in_lap = out_lap.groupby(L["DriverNumber"]).shift(-1).astype("boolean").fillna(False).astype(bool)
    P = _df(pits, ["driver_number", "lap_number"])
    pit_pairs = set()
    if not P.empty:
        pit_pairs = {(str(int(a)), int(b)) for a, b in P[["driver_number", "lap_number"]].dropna().to_numpy()}

    pos = pd.Series(np.nan, index=L.index)
    PO = _df(positions, ["date", "driver_number", "position"])
    if not PO.empty:
        PO = PO.dropna(subset=["driver_number"])
        PO["t"] = to_session_seconds(PO["date"], t0)
        PO["DriverNumber"] = PO["driver_number"].astype(int).astype(str)
        PO = PO.dropna(subset=["t"]).sort_values("t")
        left = pd.DataFrame({"t": end, "DriverNumber": L["DriverNumber"], "_i": L.index})
        ok = left["t"].notna()
        m = pd.merge_asof(left[ok].sort_values("t"), PO[["t", "DriverNumber", "position"]],
                          on="t", by="DriverNumber", direction="backward")
        pos[m["_i"].to_numpy()] = m["position"].to_numpy()

    keys = list(zip(L["DriverNumber"], L["LapNumber"].astype(int)))
    td = lambda s: pd.to_timedelta(s, unit="s")
    raw = pd.DataFrame({
        "Time": td(end), "Driver": L["name_acronym"].astype("string"),
        "DriverNumber": L["DriverNumber"], "LapTime": td(dur), "LapNumber": L["LapNumber"],
        "Stint": stint, "PitOutTime": td(start.where(out_lap)), "PitInTime": td(end.where(in_lap)),
        "Sector1Time": td(pd.to_numeric(L["duration_sector_1"], errors="coerce")),
        "Sector2Time": td(pd.to_numeric(L["duration_sector_2"], errors="coerce")),
        "Sector3Time": td(pd.to_numeric(L["duration_sector_3"], errors="coerce")),
        "Compound": comp, "TyreLife": tyre, "FreshTyre": fresh,
        "Team": L["team_name"].astype("string"), "LapStartTime": td(start),
        "TrackStatus": lap_track_status(start, end, status_iv), "Position": pos,
        "Deleted": pd.Series([k in deleted for k in keys], dtype="boolean"),
        "FastF1Generated": False,
    })
    raw["Driver"] = raw["Driver"].fillna("#" + raw["DriverNumber"])
    checks = {
        "lap_rows_without_driver_or_lap": int(n_no_key),
        "duplicate_lap_rows_dropped": int(n_dupes),
        "laps_without_stint": int(raw["Stint"].isna().sum()),
        "laps_stint_extended_by_one": int(extended),
        "in_laps_inferred": int(in_lap.sum()),
        "pit_table_rows": len(pit_pairs),
        "pit_rows_on_inferred_in_lap": int(sum(k in pit_pairs for k, f in zip(keys, in_lap) if f)),
        "pit_rows_on_out_lap": int(sum(k in pit_pairs for k, f in zip(keys, out_lap) if f)),
        "deleted_laps": int(raw["Deleted"].sum()),
        "laps_missing_start_time": int(start.isna().sum()),
    }
    return raw, checks


def weather_table(rows: list[dict], t0: pd.Timestamp) -> pd.DataFrame:
    W = _df(rows, ["date", "air_temperature", "track_temperature", "humidity", "pressure",
                   "rainfall", "wind_speed", "wind_direction"])
    if W.empty:
        return pd.DataFrame()
    return pd.DataFrame({
        "Time": pd.to_timedelta(to_session_seconds(W["date"], t0), unit="s"),
        "AirTemp": pd.to_numeric(W["air_temperature"], errors="coerce"),
        "TrackTemp": pd.to_numeric(W["track_temperature"], errors="coerce"),
        "Humidity": pd.to_numeric(W["humidity"], errors="coerce"),
        "Pressure": pd.to_numeric(W["pressure"], errors="coerce"),
        "Rainfall": pd.to_numeric(W["rainfall"], errors="coerce").fillna(0) > 0,
        "WindSpeed": pd.to_numeric(W["wind_speed"], errors="coerce"),
        "WindDirection": pd.to_numeric(W["wind_direction"], errors="coerce"),
    }).sort_values("Time").reset_index(drop=True)


def grid_from_positions(positions: list[dict]) -> list[dict]:
    """Fallback grid: each driver's first position record of the session.

    Used only when OpenF1 starting_grid is empty. It approximates the grid order
    (pit-lane starters and grid penalties applied late may differ).
    """
    PO = _df(positions, ["date", "driver_number", "position"]).dropna(
        subset=["driver_number", "position", "date"])
    if PO.empty:
        return []
    PO["_t"] = pd.to_datetime(PO["date"], utc=True, errors="coerce", format="ISO8601")
    first = PO.sort_values("_t").groupby("driver_number", as_index=False).first()
    return first[["driver_number", "position"]].to_dict(orient="records")


def results_table(grid: list[dict], result: list[dict]) -> pd.DataFrame:
    G = _df(grid, ["driver_number", "position"]).rename(columns={"position": "GridPosition"})
    R = _df(result, ["driver_number", "position", "number_of_laps", "dnf", "dns", "dsq"])
    if G.empty and R.empty:
        return pd.DataFrame()
    base = R if not R.empty else G[["driver_number"]]
    out = base.merge(G[["driver_number", "GridPosition"]], on="driver_number", how="outer") \
        if not G.empty else base.assign(GridPosition=np.nan)
    out = out.dropna(subset=["driver_number"])
    out["DriverNumber"] = out["driver_number"].astype(int).astype(str)
    return out.rename(columns={"position": "Position", "number_of_laps": "Laps"}).drop(
        columns=["driver_number"])


def scheduled_laps(result: list[dict], override: int | None) -> tuple[int | None, str]:
    """OpenF1 has no planned race distance. Use the reference file if given, else the
    winner's lap count (equals the actual distance; wrong for shortened races)."""
    if override:
        return int(override), "reference_file"
    R = _df(result, ["position", "number_of_laps"])
    win = R[pd.to_numeric(R["position"], errors="coerce") == 1]
    if len(win) and pd.notna(win["number_of_laps"].iloc[0]):
        return int(win["number_of_laps"].iloc[0]), "winner_laps_actual"
    return None, "missing"
