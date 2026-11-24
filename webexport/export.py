"""Export derived results and compact simulator inputs for the website.

What is published (web/public/data, committed):
  * reports/*.md      the generated reports and the docs, copied as they are
  * results/*.json    metrics files from the result folders, the Task 3 curve
  * sim/index.json    simulatable races
  * sim/races/<id>.json
        leave-race-out model parameters (as in research/results/simulator) plus,
        per driver: stints (compound, first lap, last lap), pit stops with the
        compound fitted, whether the car finished, and a decision state for each
        lap (compound, tyre age, stops so far, compounds used, pace intercept mu
        and its standard error, number of clean laps behind mu).

What is NOT published: lap times. mu is an average over up to 30 laps net of the
model, rounded to 1 ms; individual laps cannot be recovered from it.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd

from pipelines import config
from simulation.constraints import SLICKS
from simulation.engine import decision_state

ROOT = config.ROOT
WEB_DATA = ROOT / "web" / "public" / "data"
RESULTS = ROOT / "research" / "results"
SIM_PRIVATE = config.PROCESSED / "simulator"

REPORTS = {
    "coverage": config.REPORTS / "coverage_report.md",
    "phase2_dev": RESULTS / "phase2_dev" / "report.md",
    "phase3_dev": RESULTS / "phase3_dev" / "report.md",
    "final_test": RESULTS / "final_test" / "report.md",
    "task2_dev": RESULTS / "task2_dev" / "report.md",
    "task2_test": RESULTS / "task2_test" / "report.md",
    "task3": RESULTS / "task3" / "report.md",
    "sim_backtest": RESULTS / "simulator" / "backtest.md",
}
DOCS = ["methodology", "methodology_models", "methodology_tyre", "methodology_simulator",
        "model_changes", "preregistration", "preregistration_task2", "limitations",
        "data_dictionary"]
JSONS = {
    "final_test": RESULTS / "final_test" / "metrics.json",
    "final_test_meta": RESULTS / "final_test" / "run_meta.json",
    "task2_test_meta": RESULTS / "task2_test" / "run_meta.json",
    "task3": RESULTS / "task3" / "estimates.json",
    "phase2_dev": RESULTS / "phase2_dev" / "metrics.json",
    "phase3_dev": RESULTS / "phase3_dev" / "metrics.json",
    "coverage": config.REPORTS / "coverage.json",
}
STATE_KEYS = ["lap", "comp", "age", "stops", "used", "mu", "mu_se", "n"]


def _none(v):
    return None if v is None or (isinstance(v, float) and v != v) else v


def driver_export(p: dict, drv: str) -> dict:
    h = p["drivers"][drv]
    laps, comps, stints = h["lap_number"], h["compound_relative"], h["stint"]
    st_rows, cur = [], None
    for ln, c, s in zip(laps, comps, stints):
        if cur is None or s != cur["stint"]:
            cur = {"stint": s, "comp": c, "from": ln, "to": ln}
            st_rows.append(cur)
        cur["to"] = ln
    stops = []
    for k, ln in enumerate(laps):
        if h["flag_pit_in"][k]:
            nxt = comps[k + 1] if k + 1 < len(laps) else None
            stops.append([int(ln), nxt])
    states = {k: [] for k in STATE_KEYS}
    for ln, c in zip(laps, comps):
        if c not in SLICKS or ln >= p["total_laps"] - 3:
            continue
        try:
            s = decision_state(p, drv, int(ln))
        except ValueError:
            continue
        for k, v in zip(STATE_KEYS, [int(ln), s.current_compound, s.current_age, s.stops_so_far,
                                     "".join(x[0] for x in s.compounds_used),
                                     round(s.mu, 3), round(s.mu_se, 3), s.n_pace_laps]):
            states[k].append(v)
    return {"stints": [[r["comp"], int(r["from"]), int(r["to"])] for r in st_rows],
            "stops": stops, "finished": bool(max(laps) >= p["total_laps"]),
            "last_lap": int(max(laps)), "states": states}


def public_params(p: dict) -> dict:
    keep = ["race_id", "season", "round", "event_name", "total_laps", "dry_slick_share",
            "simulatable", "rules", "pace", "ar1", "circuit", "pit_loss", "safety_car",
            "estimation"]
    return {k: p[k] for k in keep if k in p}


def export_sim(sim_dir: Path, out: Path, log=print) -> int:
    index = json.loads((sim_dir / "index.json").read_text())
    (out / "sim" / "races").mkdir(parents=True, exist_ok=True)
    rows = []
    for r in index:
        p = json.loads((sim_dir / "races" / f"{r['race_id']}.json").read_text())
        web = public_params(p)
        web["drivers"] = {d: driver_export(p, d) for d in sorted(p["drivers"])}
        (out / "sim" / "races" / f"{r['race_id']}.json").write_text(
            json.dumps(web, separators=(",", ":"), default=float))
        rows.append({k: r[k] for k in ("race_id", "season", "event_name", "total_laps",
                                        "simulatable")} | {"round": p["round"]})
        log(f"sim {r['race_id']}")
    (out / "sim" / "index.json").write_text(json.dumps(rows, indent=1))
    return len(rows)


def export_results(out: Path, log=print) -> dict:
    found = {"reports": [], "missing": []}
    (out / "reports").mkdir(parents=True, exist_ok=True)
    (out / "results").mkdir(parents=True, exist_ok=True)
    for name, src in list(REPORTS.items()) + [(d, ROOT / "docs" / f"{d}.md") for d in DOCS]:
        if src.exists():
            shutil.copyfile(src, out / "reports" / f"{name}.md")
            found["reports"].append(name)
        else:
            found["missing"].append(str(src.relative_to(ROOT)))
    for name, src in JSONS.items():
        if src.exists():
            shutil.copyfile(src, out / "results" / f"{name}.json")
        else:
            found["missing"].append(str(src.relative_to(ROOT)))
    curve = RESULTS / "task3" / "tyre_age_curves.csv"
    if curve.exists():
        pd.read_csv(curve).to_json(out / "results" / "tyre_curves.json", orient="records")
    else:
        found["missing"].append(str(curve.relative_to(ROOT)))
    for m in found["missing"]:
        log(f"missing (skipped): {m}")
    return found


def export_all(sim_dir: Path | None = None, out: Path | None = None, log=print) -> Path:
    out = out or WEB_DATA
    out.mkdir(parents=True, exist_ok=True)
    found = export_results(out, log)
    n = export_sim(sim_dir or SIM_PRIVATE, out, log)
    (out / "manifest.json").write_text(json.dumps(
        {"generated_utc": pd.Timestamp.now(tz="UTC").isoformat(timespec="seconds"),
         "races_simulator": n, **found}, indent=1))
    return out
