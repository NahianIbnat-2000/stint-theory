"""Checks of the simulator against what actually happened (leave-race-out params).

1. Next-stint pace: standing just before a real pit stop, forecast the clean laps of
   the stint that follows (new compound, fresh tyres), and compare with repeating
   the last clean lap before the stop.
2. Remaining race time: from a decision lap one third into the race, the expected
   time of the strategy the driver actually ran, against the time they actually
   took, for drivers with no safety car, VSC or red flag after the decision lap.
3. Pit loss: predicted mean loss (other races) against each green-flag stop.
4. Calibration (added after the simulator was frozen; a check only, nothing was
   changed in response): for the drivers in check 2, how often the actual remaining
   time falls inside the simulator's own 50% and 90% ranges (no safety car drawn,
   since those drivers had none).

These test the parts a strategy comparison is built from. They cannot test the
counterfactual itself: no race was run twice.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from models.run import _md
from .engine import Pace, decision_state, expected_time, observed_strategy, simulate
from .params import OUT, PUBLIC


def load_params(rid: str, root: Path | None = None) -> dict:
    return json.loads(((root or OUT) / "races" / f"{rid}.json").read_text())


def next_stint_rows(p: dict) -> list[dict]:
    rows = []
    pace = Pace(p)
    for drv, h in p["drivers"].items():
        laps = h["lap_number"]
        for k, ln in enumerate(laps):
            if not h["flag_pit_in"][k] or ln < 5:
                continue
            try:
                st = decision_state(p, drv, ln - 1)
            except ValueError:
                continue
            prev = [h["lap_time_s"][i] for i in range(k) if h["is_clean_green"][i]]
            if not prev:
                continue
            last_green = prev[-1]
            for i in range(k + 1, len(laps)):
                if h["flag_pit_in"][i]:
                    break
                if not h["is_clean_green"][i] or h["compound_relative"][i] not in ("SOFT", "MEDIUM", "HARD"):
                    continue
                pred = float(pace.lap_mean(st.mu, laps[i], h["compound_relative"][i],
                                           h["tyre_life"][i]))
                rows.append({"race_id": p["race_id"], "driver": drv, "stop_lap": ln,
                             "laps_after_stop": laps[i] - ln, "actual": h["lap_time_s"][i],
                             "model": pred, "persistence": last_green})
    return rows


CAL_DRAWS = 300
CAL_SEED = 2026


def remaining_rows(p: dict, calibrate: bool = True) -> list[dict]:
    N = p["total_laps"]
    L = max(5, N // 3)
    rows = []
    for drv, h in p["drivers"].items():
        s = observed_strategy(p, drv, L)
        if s is None:
            continue
        idx = [i for i, ln in enumerate(h["lap_number"]) if L < ln <= N]
        if len(idx) != N - L:
            continue
        if any(h["flag_sc"][i] or h["flag_vsc"][i] or h["flag_red"][i] for i in idx):
            continue
        if any(h["lap_time_s"][i] is None for i in idx):
            continue
        try:
            st = decision_state(p, drv, L)
        except ValueError:
            continue
        actual = float(sum(h["lap_time_s"][i] for i in idx))
        row = {"race_id": p["race_id"], "driver": drv, "decision_lap": L,
               "laps": N - L, "stops": len(s.stop_laps),
               "model_s": expected_time(p, st, s), "actual_s": actual}
        if calibrate:
            t = simulate(p, st, [s], n=CAL_DRAWS, seed=CAL_SEED, sc_mode="none")["times"][:, 0]
            q = np.quantile(t, [0.05, 0.25, 0.75, 0.95])
            row |= {"in50": bool(q[1] <= actual <= q[2]), "in90": bool(q[0] <= actual <= q[3]),
                    "below90": bool(actual < q[0]), "above90": bool(actual > q[3]),
                    "width90": float(q[3] - q[0])}
        rows.append(row)
    return rows


def run_backtest(root: Path | None = None, public: Path | None = None) -> Path:
    root = root or OUT
    public = public or (PUBLIC if root == OUT else root)
    index = json.loads((root / "index.json").read_text())
    ns, rem, pit, coefs = [], [], [], []
    stops = pd.read_csv(root / "pit_stops.csv")
    for r in index:
        if not r["simulatable"]:
            continue
        p = load_params(r["race_id"], root)
        coefs.append({k: p["pace"]["coef"][k] for k in p["pace"]["coef"]} |
                     {f"tail_{k}": v for k, v in (p["pace"].get("tail_slope") or {}).items()} |
                     {"circuit_scale": p["circuit"]["scale"], "pit_loss": p["pit_loss"]["mean_s"]})
        ns += next_stint_rows(p)
        rem += remaining_rows(p)
        g = stops[(stops["race_id"] == r["race_id"]) & ~stops["neutralised"]]
        for loss in g["loss_s"]:
            pit.append({"race_id": r["race_id"], "pred": p["pit_loss"]["mean_s"], "actual": loss})
    ns, rem, pit = pd.DataFrame(ns), pd.DataFrame(rem), pd.DataFrame(pit)
    parts = ["# Simulator backtest (leave-race-out parameters)",
             "Each race is checked with parameters estimated without it. These checks cover "
             "the building blocks; a counterfactual strategy outcome itself cannot be checked."]
    if coefs:
        c = pd.DataFrame(coefs)
        summ = c.agg(["mean", "min", "max"]).T.reset_index().rename(columns={"index": "parameter"})
        parts += ["## Pace-model parameters across the leave-race-out fits",
                  "`lap_number` is the common per-lap trend (fuel burn + track evolution; Task 3 "
                  "implied about -0.065 s/lap). `k_*` are compound offsets against medium; "
                  "`age_*`, `age2_*` the tyre-age curve (Task 3 spec); `tail_*` the linear "
                  "Task 3 slopes used as the minimum slope beyond the curve's cap; "
                  "`circuit_scale` should average about 1.", _md(summ, 4)]
    if not ns.empty:
        ns["err_model"] = ns["model"] - ns["actual"]
        ns["err_persist"] = ns["persistence"] - ns["actual"]
        ns["bin"] = pd.cut(ns["laps_after_stop"], [0, 3, 6, 10, 15, 20, 30, 80])
        t = ns.groupby("bin", observed=True).agg(
            laps=("actual", "size"), model_mae=("err_model", lambda x: x.abs().mean()),
            model_bias=("err_model", "mean"), persistence_mae=("err_persist", lambda x: x.abs().mean()),
            persistence_bias=("err_persist", "mean")).reset_index()
        t["bin"] = t["bin"].astype(str)
        parts += ["## 1. Pace of the next stint after a real pit stop (clean laps, s)",
                  f"{len(ns)} laps after {ns.groupby(['race_id','driver','stop_lap']).ngroups} "
                  f"stops. Overall MAE: model {ns['err_model'].abs().mean():.3f}, persistence "
                  f"{ns['err_persist'].abs().mean():.3f}; bias: model {ns['err_model'].mean():+.3f}, "
                  f"persistence {ns['err_persist'].mean():+.3f}.", _md(t)]
    if not rem.empty:
        rem["err"] = rem["model_s"] - rem["actual_s"]
        rem["err_per_lap"] = rem["err"] / rem["laps"]
        parts += ["## 2. Remaining race time of the strategy actually run (s)",
                  f"{len(rem)} drivers in {rem['race_id'].nunique()} races, decision lap at one "
                  "third distance, no neutralisation afterwards for that driver.",
                  _md(pd.DataFrame([{
                      "MAE (s)": rem["err"].abs().mean(), "median abs (s)": rem["err"].abs().median(),
                      "bias (s)": rem["err"].mean(), "MAE per lap (s)": rem["err_per_lap"].abs().mean(),
                      "90% of errors within (s)": rem["err"].abs().quantile(0.9)}])),
                  "These are errors in absolute race time. They are not an interval for the gap between two strategies: "
                  "much of the error (the driver's pace level, the per-lap trend) is shared by every plan for the same "
                  "driver and cancels in a comparison. The part that does not cancel is strategy-specific, mainly the "
                  "fresh-tyre bias in section 1, which charges each extra stop about 1-2 s too much."]
    if not pit.empty:
        e = pit["pred"] - pit["actual"]
        parts += ["## 3. Pit loss of green-flag stops (s)",
                  _md(pd.DataFrame([{"stops": len(pit), "MAE": e.abs().mean(),
                                     "median abs": e.abs().median(), "bias": e.mean()}]))]
    summary = {"generated_by": "python -m simulation backtest", "races": int(sum(r["simulatable"] for r in index))}
    if coefs:
        summary["parameters"] = summ.to_dict(orient="records")
    if not ns.empty:
        summary["next_stint"] = {"laps": int(len(ns)), "stops": int(ns.groupby(["race_id", "driver", "stop_lap"]).ngroups),
                                 "model_mae": float(ns["err_model"].abs().mean()), "model_bias": float(ns["err_model"].mean()),
                                 "persistence_mae": float(ns["err_persist"].abs().mean()),
                                 "persistence_bias": float(ns["err_persist"].mean()), "by_laps_after_stop": t.to_dict(orient="records")}
    if not rem.empty:
        summary["remaining"] = {"drivers": int(len(rem)), "races": int(rem["race_id"].nunique()),
                                "decision": "one third distance; no SC, VSC or red flag afterwards for that driver",
                                "mae_s": float(rem["err"].abs().mean()), "median_abs_s": float(rem["err"].abs().median()),
                                "bias_s": float(rem["err"].mean()), "mae_per_lap_s": float(rem["err_per_lap"].abs().mean()),
                                "abs_p90_s": float(rem["err"].abs().quantile(0.9))}
        if "in90" in rem:
            cal = {"draws": CAL_DRAWS, "seed": CAL_SEED, "drivers": int(len(rem)),
                   "coverage50": float(rem["in50"].mean()), "coverage90": float(rem["in90"].mean()),
                   "below90": float(rem["below90"].mean()), "above90": float(rem["above90"].mean()),
                   "median_width90_s": float(rem["width90"].median())}
            summary["calibration"] = cal
            parts += ["## 4. Calibration of the simulated range (added after the freeze; check only)",
                      f"For the {cal['drivers']} drivers above, {CAL_DRAWS} simulated races each (no safety car). "
                      f"Share of actual remaining times inside the simulator's 50% range: {cal['coverage50']:.1%} "
                      f"(nominal 50%); inside its 90% range: {cal['coverage90']:.1%} (nominal 90%). "
                      f"Below the range (faster than simulated): {cal['below90']:.1%}; above: {cal['above90']:.1%}. "
                      f"Median width of the 90% range: {cal['median_width90_s']:.1f} s. The simulator was not changed "
                      "in response to this check."]
    if not pit.empty:
        summary["pit_loss"] = {"stops": int(len(pit)), "mae_s": float(e.abs().mean()),
                               "median_abs_s": float(e.abs().median()), "bias_s": float(e.mean())}
    public.mkdir(parents=True, exist_ok=True)
    (public / "backtest.md").write_text("\n\n".join(parts) + "\n")
    (public / "backtest.json").write_text(json.dumps(summary, indent=1, default=float))
    # row-level backtest tables contain lap times: processed (git-ignored) folder only
    for name, df in (("backtest_next_stint", ns), ("backtest_remaining", rem)):
        if not df.empty:
            df.drop(columns=[c for c in ("bin",) if c in df.columns]).to_csv(root / f"{name}.csv",
                                                                              index=False)
    return public / "backtest.md"
