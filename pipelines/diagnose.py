"""Per-race diagnostics for checking the OpenF1 reconstruction by eye.

    python -m pipelines diagnose --seasons 2023

Writes data/reports/diagnostics.md from the raw extracts on disk (no network).
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

from . import config
from .ingest import iter_raw_sessions, load_raw_session

KEY_WORDS = ("SAFETY CAR", "RED FLAG", "RESUME", "STANDING START", "ROLLING START",
             "SUSPENDED", "CHEQUERED", "PIT EXIT")


def _md(df: pd.DataFrame) -> str:
    if df.empty:
        return "_none_"
    cols = list(df.columns)
    rows = ["| " + " | ".join(map(str, cols)) + " |", "|" + "---|" * len(cols)]
    for r in df.itertuples(index=False):
        rows.append("| " + " | ".join("" if pd.isna(v) else str(v).replace("|", "/") for v in r) + " |")
    return "\n".join(rows)


def race_section(raw: dict) -> str:
    meta, laps = raw["meta"], raw["laps"]
    out = [f"## {meta['season']} R{meta['round']:02d} {meta['event_name']} "
           f"(session {meta.get('openf1_session_key')})"]
    out.append(f"- scheduled_laps: {meta.get('scheduled_laps')} ({meta.get('scheduled_laps_source')})"
               f"; grid: {meta.get('grid_source')}")
    out.append(f"- endpoint rows: {meta.get('endpoint_rows', meta.get('rows'))}")
    if meta.get("errors"):
        out.append("- errors: " + "; ".join(meta["errors"]))

    ln = laps["LapNumber"].astype(int)
    per_driver = laps.assign(L=ln).groupby("Driver")["L"].max()
    out.append(f"- max lap {ln.max()}; drivers reaching it: {int((per_driver == ln.max()).sum())}; "
               f"lap counts (top 5): {per_driver.value_counts().sort_index(ascending=False).head(5).to_dict()}")
    sched = meta.get("scheduled_laps")
    if sched:
        beyond = laps[ln > sched]
        if len(beyond):
            out.append(f"\n**Laps beyond scheduled_laps ({sched})**\n")
            out.append(_md(pd.DataFrame({
                "driver": beyond["Driver"], "lap": beyond["LapNumber"].astype(int),
                "lap_time_s": beyond["LapTime"].dt.total_seconds().round(3),
                "pit_in": beyond["PitInTime"].notna(), "status": beyond["TrackStatus"]})))

    nos = laps[laps["Stint"].isna()]
    if len(nos):
        prev = laps.sort_values(["Driver", "LapNumber"]).groupby("Driver")["Stint"]
        nos = nos.assign(stint_before=prev.shift(1).loc[nos.index],
                         stint_after=prev.shift(-1).loc[nos.index])
        out.append("\n**Laps without a stint**\n")
        out.append(_md(pd.DataFrame({
            "driver": nos["Driver"], "lap": nos["LapNumber"].astype(int),
            "stint_before": nos["stint_before"], "stint_after": nos["stint_after"],
            "pit_out": nos["PitOutTime"].notna(), "lap_time_s": nos["LapTime"].dt.total_seconds().round(3)})))

    rc = raw.get("race_control")
    if rc is not None and len(rc):
        msg = rc["message"].astype("string").str.upper().fillna("")
        cat = rc.get("category", pd.Series("", index=rc.index)).astype("string").str.upper().fillna("")
        flag = rc.get("flag", pd.Series("", index=rc.index)).astype("string").str.upper().fillna("")
        scope = rc.get("scope", pd.Series("", index=rc.index)).astype("string").str.upper().fillna("")
        keep = (cat.eq("SAFETYCAR") | (scope.eq("TRACK") & flag.isin(["RED", "GREEN", "CLEAR"]))
                | msg.str.contains("|".join(KEY_WORDS), regex=True))
        sel = rc[keep]
        out.append("\n**Race-control messages used for SC / VSC / red periods**\n")
        out.append(_md(pd.DataFrame({
            "date_utc": sel["date"].astype(str).str[11:19],
            "lap": sel.get("lap_number"), "category": sel.get("category"),
            "flag": sel.get("flag"), "scope": sel.get("scope"), "message": sel["message"]})))

    ts = raw.get("track_status")
    if ts is not None and len(ts):
        t = ts[ts["code"].astype(str) != "2"].copy()
        out.append("\n**Rebuilt SC / VSC / red periods (session seconds)**\n")
        t["minutes"] = ((t["end_s"] - t["start_s"]) / 60).round(1)
        out.append(_md(t[["source", "start_s", "end_s", "minutes"]].round(1)))
        codes = laps["TrackStatus"].astype("string").fillna("")
        out.append("\nLaps (any driver) flagged: SC {}, VSC {}, red {}, yellow {}".format(
            *(int(codes.str.contains(c).sum()) for c in ("4", "6", "5", "2"))))
    return "\n".join(out)


WATCH = ("sc_unpaired", "vsc_unpaired", "red_unpaired", "safetycar_msgs_unmatched")


def watchlist(raws: list[dict]) -> str:
    rows = []
    for r in raws:
        m, c = r["meta"], r["meta"].get("checks", {})
        bad = {k: c.get(k, 0) for k in WATCH if c.get(k, 0)}
        if bad:
            rows.append({"season": m["season"], "round": m["round"], "event": m["event_name"], **bad})
    return "## Races to look at\n\nNonzero unpaired or unmatched safety-car / VSC / red messages.\n\n" + \
        _md(pd.DataFrame(rows).fillna(0))


def grid_table(raws: list[dict], season: int, rnd: int) -> str:
    for r in raws:
        if r["meta"]["season"] == season and r["meta"]["round"] == rnd:
            res = r.get("results")
            if res is None or res.empty:
                return "_no grid_"
            drv = r["laps"][["DriverNumber", "Driver"]].drop_duplicates()
            g = res.merge(drv, on="DriverNumber", how="left").sort_values("GridPosition")
            return (f"## Grid check: {season} R{rnd:02d} {r['meta']['event_name']} "
                    f"(source: {r['meta'].get('grid_source')})\n\nCompare with the official grid.\n\n"
                    + _md(g[["GridPosition", "Driver", "DriverNumber"]]))
    return ""


def diagnose(seasons: Iterable[int] | None = None, raw_root: Path | None = None,
             out: Path | None = None) -> Path:
    raws = [load_raw_session(d) for d in iter_raw_sessions(raw_root, seasons)]
    first = min(((r["meta"]["season"], r["meta"]["round"]) for r in raws), default=None)
    head = [watchlist(raws)] + ([grid_table(raws, *first)] if first else [])
    sections = head + [race_section(r) for r in raws]
    out = out or config.REPORTS / "diagnostics.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("# STINT THEORY per-race diagnostics\n\nBuilt from data/raw. For checking the "
                   "OpenF1 reconstruction by eye; not a results file.\n\n" + "\n\n".join(sections) + "\n")
    return out
