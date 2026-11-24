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

  * results/test_errors.json
        descriptive breakdown of the single pre-registered Task 1 test run (already
        stored predictions): error by tyre age, by race, quantiles and a histogram
        of signed errors per model. No model is refitted or rescored.
  * per race "context": weather medians and ranges, share of laps under SC/VSC/red,
        number of pit stops, lap completeness (aggregates of the lap table).

What is NOT published: lap times. mu is an average over up to 30 laps net of the
model, rounded to 1 ms; individual laps cannot be recovered from it.
"""
from __future__ import annotations

import json
import math
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


def _clean(o):
    """NaN/inf -> null: Python's json writes NaN, which browsers reject as JSON."""
    if isinstance(o, float):
        return o if math.isfinite(o) else None
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_clean(v) for v in o]
    return o


def copy_json(src: Path, dst: Path) -> None:
    text = src.read_text().replace("-Infinity", "null").replace("Infinity", "null")
    data = json.loads(text.replace("NaN", "null")) if "NaN" in text else json.loads(text)
    dst.write_text(json.dumps(_clean(data), indent=1))


def official_status(season: int, rnd: int, numbers: dict) -> dict:
    """driver code -> 'dnf' | 'dsq' | 'dns' | 'classified', from OpenF1 session results
    in the raw folder. Empty if the results file is not there (then nothing is marked)."""
    hits = sorted((config.RAW / str(season)).glob(f"R{rnd:02d}_*/results.parquet"))
    if not hits:
        return {}
    r = pd.read_parquet(hits[0])
    out = {}
    for _, row in r.iterrows():
        code = numbers.get(str(row.get("DriverNumber")))
        if code is None:
            continue
        status = "classified"
        for k in ("dsq", "dns", "dnf"):
            v = row.get(k)
            if v is not None and not (isinstance(v, float) and math.isnan(v)) and bool(v):
                status = k
        out[code] = status
    return out


def driver_export(p: dict, drv: str, status: str | None = None) -> dict:
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
            "last_lap": int(max(laps)), "status": status, "states": states}


def public_params(p: dict) -> dict:
    keep = ["race_id", "season", "round", "event_name", "total_laps", "dry_slick_share",
            "simulatable", "rules", "pace", "ar1", "circuit", "pit_loss", "safety_car",
            "estimation"]
    return {k: p[k] for k in keep if k in p}


def driver_numbers(laps_path: Path | None) -> dict:
    """race_id -> {driver number: driver code}, from the processed lap table."""
    laps_path = laps_path or config.PROCESSED / "laps_clean.parquet"
    if not laps_path.exists():
        return {}
    d = pd.read_parquet(laps_path, columns=["race_id", "driver", "driver_number"]).drop_duplicates()
    return {rid: {str(n): str(c) for n, c in zip(g["driver_number"], g["driver"])}
            for rid, g in d.groupby("race_id")}


def export_sim(sim_dir: Path, out: Path, log=print, laps_path: Path | None = None) -> int:
    index = json.loads((sim_dir / "index.json").read_text())
    numbers = driver_numbers(laps_path)
    lp = laps_path or config.PROCESSED / "laps_clean.parquet"
    cov = config.REPORTS / "coverage.json"
    completeness = {(r["season"], r["round"]): r["lap_completeness"]
                    for r in json.loads(cov.read_text()).get("lap_completeness", [])} if cov.exists() else {}
    context = race_context(pd.read_parquet(lp), completeness) if lp.exists() else {}
    (out / "sim" / "races").mkdir(parents=True, exist_ok=True)
    rows = []
    for r in index:
        p = json.loads((sim_dir / "races" / f"{r['race_id']}.json").read_text())
        web = public_params(p)
        status = official_status(p["season"], p["round"], numbers.get(p["race_id"], {}))
        web["drivers"] = {d: driver_export(p, d, status.get(d)) for d in sorted(p["drivers"])}
        web["context"] = context.get(p["race_id"])
        (out / "sim" / "races" / f"{r['race_id']}.json").write_text(
            json.dumps(_clean(web), separators=(",", ":"), default=float))
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
            copy_json(src, out / "results" / f"{name}.json")
        else:
            found["missing"].append(str(src.relative_to(ROOT)))
    preds = RESULTS / "final_test" / "predictions.parquet"
    if preds.exists():
        meta = json.loads(JSONS["final_test_meta"].read_text()) if JSONS["final_test_meta"].exists() else None
        (out / "results" / "test_errors.json").write_text(json.dumps(_clean(test_errors(pd.read_parquet(preds), meta))))
    else:
        found["missing"].append(str(preds.relative_to(ROOT)))
    curve = RESULTS / "task3" / "tyre_age_curves.csv"
    if curve.exists():
        (out / "results" / "tyre_curves.json").write_text(
            json.dumps(_clean(pd.read_csv(curve).to_dict(orient="records"))))
    else:
        found["missing"].append(str(curve.relative_to(ROOT)))
    for m in found["missing"]:
        log(f"missing (skipped): {m}")
    return found


TYRE_BINS = [0, 5, 10, 15, 20, 30, 80]
HIST_EDGES = [round(-3 + 0.1 * i, 1) for i in range(61)]


def test_errors(pred: pd.DataFrame, meta: dict | None = None) -> dict:
    """Aggregates of stored test predictions (columns pred_<model>, y, race_id,
    target_tyre_life). Nothing is refitted; no new comparisons or intervals."""
    import numpy as np
    models = [c[5:] for c in pred.columns if c.startswith("pred_")]
    err = {m: (pred[f"pred_{m}"] - pred["y"]).to_numpy(float) for m in models}
    out = {"source": "research/results/final_test/predictions.parquet",
           "run_finished_utc": (meta or {}).get("finished_utc"),
           "n_laps": int(len(pred)), "races": int(pred["race_id"].nunique()), "models": models}
    bins = pd.cut(pred["target_tyre_life"], TYRE_BINS)
    out["by_tyre_age"] = [{"bin": str(b), "lo": int(b.left), "hi": int(b.right), "n": int(len(g)),
                           "mae": {m: float(np.abs(err[m][g.index.to_numpy()]).mean()) for m in models}}
                          for b, g in pred.reset_index(drop=True).groupby(bins.reset_index(drop=True), observed=True)]
    out["by_race"] = [{"race_id": str(r), "n": int(len(g)),
                       "mae": {m: float(np.abs(err[m][g.index.to_numpy()]).mean()) for m in models}}
                      for r, g in pred.reset_index(drop=True).groupby("race_id")]
    qs = [0.1, 0.25, 0.5, 0.75, 0.9, 0.95]
    out["abs_error_quantiles"] = {m: dict(zip([f"p{int(q * 100)}" for q in qs],
                                              np.quantile(np.abs(err[m]), qs).tolist())) for m in models}
    edges = np.array(HIST_EDGES)
    out["signed_error_hist"] = {"edges": HIST_EDGES, "counts": {
        m: {"inside": np.histogram(err[m], edges)[0].tolist(),
            "below": int((err[m] < edges[0]).sum()), "above": int((err[m] > edges[-1]).sum())} for m in models}}
    return out


def race_context(laps: pd.DataFrame, completeness: dict) -> dict:
    """race_id -> weather and neutralisation aggregates (no lap times)."""
    out = {}
    for rid, g in laps.groupby("race_id"):
        def rng(col):
            v = pd.to_numeric(g[col], errors="coerce").dropna() if col in g else pd.Series(dtype=float)
            return None if v.empty else {"median": float(v.median()), "min": float(v.min()), "max": float(v.max())}
        share = lambda col: float(g[col].fillna(False).astype(bool).mean()) if col in g else None
        key = (int(g["season"].iloc[0]), int(g["round"].iloc[0]))
        out[rid] = {"track_temp_c": rng("track_temp_c"), "air_temp_c": rng("air_temp_c"),
                    "humidity_pct": rng("humidity_pct"), "wind_speed_ms": rng("wind_speed_ms"),
                    "rain_lap_share": share("rainfall") if "rainfall" in g else share("flag_rain"),
                    "sc_lap_share": share("flag_sc"), "vsc_lap_share": share("flag_vsc"),
                    "red_lap_share": share("flag_red"), "clean_green_share": share("is_clean_green"),
                    "drivers": int(g["driver"].nunique()), "pit_stops": int(g["flag_pit_in"].fillna(False).astype(bool).sum()),
                    "lap_completeness": completeness.get(key)}
    return out


def export_all(sim_dir: Path | None = None, out: Path | None = None, log=print) -> Path:
    out = out or WEB_DATA
    out.mkdir(parents=True, exist_ok=True)
    found = export_results(out, log)
    n = export_sim(sim_dir or SIM_PRIVATE, out, log)
    (out / "manifest.json").write_text(json.dumps(
        {"generated_utc": pd.Timestamp.now(tz="UTC").isoformat(timespec="seconds"),
         "races_simulator": n, **found}, indent=1))
    return out
