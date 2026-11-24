"""Checks of the simulator against what actually happened (leave-race-out params).

1. Next-stint pace: standing just before a real pit stop, forecast the clean laps of
   the stint that follows (new compound, fresh tyres), and compare with repeating
   the last clean lap before the stop.
2. Remaining race time: from a decision lap one third into the race, the expected
   time of the strategy the driver actually ran, against the time they actually
   took, for drivers with no safety car, VSC or red flag after the decision lap.
3. Pit loss: predicted mean loss (other races) against each green-flag stop.

These test the parts a strategy comparison is built from. They cannot test the
counterfactual itself: no race was run twice.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from models.run import _md
from .engine import Pace, decision_state, expected_time, observed_strategy
from .params import OUT


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


def remaining_rows(p: dict) -> list[dict]:
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
        rows.append({"race_id": p["race_id"], "driver": drv, "decision_lap": L,
                     "laps": N - L, "stops": len(s.stop_laps),
                     "model_s": expected_time(p, st, s), "actual_s": actual})
    return rows


def run_backtest(root: Path | None = None) -> Path:
    root = root or OUT
    index = json.loads((root / "index.json").read_text())
    ns, rem, pit = [], [], []
    stops = pd.read_csv(root / "pit_stops.csv")
    for r in index:
        if not r["simulatable"]:
            continue
        p = load_params(r["race_id"], root)
        ns += next_stint_rows(p)
        rem += remaining_rows(p)
        g = stops[(stops["race_id"] == r["race_id"]) & ~stops["neutralised"]]
        for loss in g["loss_s"]:
            pit.append({"race_id": r["race_id"], "pred": p["pit_loss"]["mean_s"], "actual": loss})
    ns, rem, pit = pd.DataFrame(ns), pd.DataFrame(rem), pd.DataFrame(pit)
    parts = ["# Simulator backtest (leave-race-out parameters)",
             "Each race is checked with parameters estimated without it. These checks cover "
             "the building blocks; a counterfactual strategy outcome itself cannot be checked."]
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
                  "Strategy differences smaller than these errors are not separable by the model."]
    if not pit.empty:
        e = pit["pred"] - pit["actual"]
        parts += ["## 3. Pit loss of green-flag stops (s)",
                  _md(pd.DataFrame([{"stops": len(pit), "MAE": e.abs().mean(),
                                     "median abs": e.abs().median(), "bias": e.mean()}]))]
    (root / "backtest.md").write_text("\n\n".join(parts) + "\n")
    for name, df in (("backtest_next_stint", ns), ("backtest_remaining", rem)):
        if not df.empty:
            df.drop(columns=[c for c in ("bin",) if c in df.columns]).to_csv(root / f"{name}.csv",
                                                                              index=False)
    return root / "backtest.md"
