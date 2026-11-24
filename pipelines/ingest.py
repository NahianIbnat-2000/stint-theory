"""Download Grand Prix race sessions from OpenF1 and store per-race raw extracts.

Each race is written to data/raw/<season>/R<round>_<slug>/ as Parquet tables in
the FastF1-style layout the cleaning step expects, plus session_meta.json with
provenance and reconstruction checks. Raw OpenF1 responses are cached as JSON
under the cache folder, so re-running never re-downloads.

Raw extracts are git-ignored. Only manifests and reports are committed.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from . import config, openf1

log = logging.getLogger(__name__)

TABLES = ("laps", "weather", "track_status", "race_control", "results")
ENDPOINTS = ("laps", "stints", "drivers", "pit", "position", "race_control", "weather",
             "starting_grid", "session_result")


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(name).lower()).strip("_")


def session_dir(season: int, rnd: int, event_name: str, raw_root: Path | None = None) -> Path:
    return (raw_root or config.RAW) / str(season) / f"R{rnd:02d}_{slugify(event_name)}"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_scheduled_laps_reference(path: Path | None = None) -> dict:
    """Optional hand-checked race distances: data/reference/scheduled_laps.csv."""
    path = path or config.REFERENCE / "scheduled_laps.csv"
    if not path.exists():
        return {}
    ref = pd.read_csv(path, comment="#").dropna(subset=["scheduled_laps"])
    return {(int(r.season), int(r["round"])): int(r.scheduled_laps) for _, r in ref.iterrows()}


def _to_parquet(df: pd.DataFrame, path: Path) -> None:
    out = df.copy()
    for col in out.columns:
        if out[col].dtype == object:
            out[col] = out[col].astype("string")
    out.to_parquet(path, index=False)


@dataclass
class SessionRecord:
    season: int
    round: int
    event_name: str
    session_key: int | None
    status: str  # "downloaded" | "skipped_existing" | "failed"
    path: str | None = None
    rows: dict = field(default_factory=dict)
    sha256: dict = field(default_factory=dict)
    checks: dict = field(default_factory=dict)
    errors: list = field(default_factory=list)


def fetch_race(client: openf1.OpenF1Client, sess: dict, *, force: bool = False,
               raw_root: Path | None = None, sched_ref: dict | None = None) -> SessionRecord:
    season, rnd = int(sess["year"]), int(sess["round"])
    name, key = sess["event_name"], int(sess["session_key"])
    out = session_dir(season, rnd, name, raw_root)
    meta_path = out / "session_meta.json"
    if meta_path.exists() and not force:
        m = json.loads(meta_path.read_text())
        return SessionRecord(season, rnd, name, key, "skipped_existing", str(out),
                             m.get("rows", {}), m.get("sha256", {}), m.get("checks", {}),
                             m.get("errors", []))
    rec = SessionRecord(season, rnd, name, key, "failed", str(out))

    data = {}
    for ep in ENDPOINTS:
        try:
            data[ep] = client.get(ep, session_key=key)
        except Exception as exc:
            data[ep] = []
            rec.errors.append(f"{ep}: {type(exc).__name__}: {exc}")
    if not data["laps"]:
        rec.errors.append("laps: no rows")
        return rec

    t0 = pd.Timestamp(sess["date_start"]).tz_convert("UTC") if pd.Timestamp(
        sess["date_start"]).tzinfo else pd.Timestamp(sess["date_start"], tz="UTC")
    # session end for open-ended periods: the later of the scheduled end and the
    # last lap start + 10 min (races with red flags can overrun the schedule)
    lap_starts = openf1.to_session_seconds(pd.Series([r.get("date_start") for r in data["laps"]]), t0)
    rough_end = np.nanmax([openf1.to_session_seconds(pd.Series([sess.get("date_end")]), t0).iloc[0],
                           lap_starts.max() + 600])
    sched, sched_src = openf1.scheduled_laps(data["session_result"],
                                             (sched_ref or {}).get((season, rnd)))
    intervals, rc_stats = openf1.race_control_intervals(
        data["race_control"], t0, rough_end if pd.notna(rough_end) else 1e9)
    laps, lap_checks = openf1.build_laps(
        data["laps"], data["stints"], data["drivers"], data["pit"], data["position"],
        intervals, openf1.deleted_laps(data["race_control"]), t0)
    grid_rows, grid_src = data["starting_grid"], "starting_grid"
    if not grid_rows:
        grid_rows, grid_src = openf1.grid_from_positions(data["position"]), "position_first_record"
    rec.checks = {**lap_checks, **rc_stats,
                  "starting_grid_rows": len(data["starting_grid"]),
                  "session_result_rows": len(data["session_result"])}

    tables = {
        "laps": laps,
        "weather": openf1.weather_table(data["weather"], t0),
        "track_status": intervals,
        "race_control": pd.DataFrame(data["race_control"]),
        "results": openf1.results_table(grid_rows, data["session_result"]),
    }
    out.mkdir(parents=True, exist_ok=True)
    for tname, df in tables.items():
        rec.rows[tname] = int(len(df))
        if df is None or df.empty:
            continue
        p = out / f"{tname}.parquet"
        _to_parquet(df, p)
        rec.sha256[tname] = sha256_file(p)

    meta = {
        "season": season, "round": rnd, "event_name": name, "session": "Race",
        "openf1_session_key": key, "openf1_meeting_key": sess.get("meeting_key"),
        "circuit_short_name": sess.get("circuit_short_name"),
        "session_date_start_utc": str(sess["date_start"]),
        "session_clock_origin": "seconds since OpenF1 session date_start (scheduled start)",
        "scheduled_laps": sched, "scheduled_laps_source": sched_src,
        "grid_source": grid_src if grid_rows else "missing",
        "source": "OpenF1 historical API (https://openf1.org), free tier, no authentication",
        "endpoints": list(ENDPOINTS),
        "endpoint_rows": {ep: len(data[ep]) for ep in ENDPOINTS},
        "retrieved_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "rows": rec.rows, "sha256": rec.sha256, "checks": rec.checks, "errors": rec.errors,
    }
    meta_path.write_text(json.dumps(meta, indent=2, default=str))
    rec.status = "downloaded"
    return rec


def run_ingest(seasons: Iterable[int], rounds: Iterable[int] | None = None, *,
               force: bool = False, client: openf1.OpenF1Client | None = None,
               raw_root: Path | None = None, manifest_root: Path | None = None) -> list[Path]:
    client = client or openf1.OpenF1Client(config.CACHE)
    manifest_root = manifest_root or config.MANIFESTS
    manifest_root.mkdir(parents=True, exist_ok=True)
    rounds = set(rounds) if rounds else None
    sched_ref = load_scheduled_laps_reference()
    written = []
    for season in seasons:
        races = openf1.race_sessions(client, season)
        records = []
        for _, s in races.iterrows():
            if rounds and int(s["round"]) not in rounds:
                continue
            log.info("Season %s round %s %s (session %s)", season, s["round"], s["event_name"],
                     s["session_key"])
            rec = fetch_race(client, {**s.to_dict(), "year": season}, force=force,
                             raw_root=raw_root, sched_ref=sched_ref)
            records.append(rec.__dict__)
        manifest = {
            "season": season, "source": "OpenF1",
            "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "races_listed": int(len(races)),
            "rounds_requested": sorted(rounds) if rounds else "all",
            "sessions": records,
        }
        path = manifest_root / f"ingest_{season}.json"
        if path.exists() and rounds:
            old = json.loads(path.read_text())
            keep = {r["round"]: r for r in old.get("sessions", [])}
            keep.update({r["round"]: r for r in records})
            manifest["sessions"] = [keep[k] for k in sorted(keep)]
            manifest["rounds_requested"] = "merged"
        path.write_text(json.dumps(manifest, indent=2, default=str))
        written.append(path)
        log.info("OpenF1 calls so far: %s network, %s cache hits", client.calls, client.cache_hits)
    return written


def load_raw_session(path: Path) -> dict:
    path = Path(path)
    out = {"meta": json.loads((path / "session_meta.json").read_text())}
    for name in TABLES:
        p = path / f"{name}.parquet"
        out[name] = pd.read_parquet(p) if p.exists() else None
    return out


def iter_raw_sessions(raw_root: Path | None = None, seasons: Iterable[int] | None = None):
    root = raw_root or config.RAW
    seasons = set(seasons) if seasons else None
    for meta in sorted(root.glob("*/R*/session_meta.json")):
        if seasons and int(meta.parent.parent.name) not in seasons:
            continue
        yield meta.parent
