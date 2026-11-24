"""Task 2 experiment runner (development races).

    python -m models horizon            # development run, 2025 R1-12
    python -m models horizon --quick    # smoke test

Writes research/results/task2_dev/.
"""
from __future__ import annotations

import datetime as dt
import json
import logging
import time
from pathlib import Path

import numpy as np
import pandas as pd

from pipelines import config
from . import data
from .deep import build_sequences
from .horizon import H, MODELS, NEURAL, SIMPLE, MultiHorizonNet, add_horizon_targets, origin_sample
from .run import _md

log = logging.getLogger(__name__)
OUT = config.ROOT / "research" / "results" / "task2_dev"
P2_TUNING = config.ROOT / "research" / "results" / "phase2_dev" / "tuning.json"
P3_TUNING = config.ROOT / "research" / "results" / "phase3_dev" / "tuning.json"
KEY = ["race_id", "driver", "lap_number"]


def load(features_path=None, include_test=False, **kw):
    full = data.load_features(features_path, include_test=include_test, **kw)
    full = add_horizon_targets(full)
    return full, build_sequences(full)


def predict_folds(full, seq, split, xgb_params, net_params, n_seeds=3, quick=False,
                  max_epochs=40):
    o = origin_sample(full)
    folds = list(data.rolling_folds(o, o["split"] == split))
    if quick:
        folds = folds[:2]
    frames, runtime = [], {m: 0.0 for m in MODELS}
    for tr, ev, race_id in folds:
        train, test = o.loc[tr], o.loc[ev]
        assert train["race_order"].max() < test["race_order"].min()
        f = test[KEY + ["compound_relative", "tyre_life"]].copy()
        for h in range(1, H + 1):
            f[f"y_h{h}"] = test[f"y_h{h}"].to_numpy()
            f[f"valid_h{h}"] = test[f"valid_h{h}"].to_numpy()
        for name, cls in SIMPLE.items():
            t0 = time.perf_counter()
            kw = xgb_params if name == "xgboost_direct" else {}
            P = cls(**kw).fit(train).predict(test)
            runtime[name] += time.perf_counter() - t0
            for h in range(1, H + 1):
                f[f"{name}_h{h}"] = P[:, h - 1]
        for arch in NEURAL:
            t0 = time.perf_counter()
            Ps = [MultiHorizonNet(arch, seed=s, max_epochs=max_epochs, **net_params[arch])
                  .fit(train, seq[tr]).predict(test, seq[ev]) for s in range(n_seeds)]
            runtime[f"{arch}_multi"] += time.perf_counter() - t0
            P = np.mean(Ps, axis=0)
            for h in range(1, H + 1):
                f[f"{arch}_multi_h{h}"] = P[:, h - 1]
        frames.append(f)
        log.info("%s race %s done (%d origins)", split, race_id, len(test))
    return pd.concat(frames, ignore_index=True), runtime


def long_format(pred):
    """One row per scored (origin, horizon) pair."""
    rows = []
    for h in range(1, H + 1):
        v = pred[f"valid_h{h}"]
        part = pred.loc[v, ["race_id", "driver", "lap_number", "tyre_life"]].copy()
        part["h"] = h
        part["y"] = pred.loc[v, f"y_h{h}"]
        for m in MODELS:
            part[f"pred_{m}"] = pred.loc[v, f"{m}_h{h}"]
        rows.append(part)
    return pd.concat(rows, ignore_index=True)


def race_boot(frame, fn, b=2000, seed=7):
    """Race-clustered bootstrap of a statistic fn(frame) -> float."""
    races = frame["race_id"].unique()
    groups = {r: g for r, g in frame.groupby("race_id")}
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(b):
        pick = rng.choice(races, len(races), replace=True)
        vals.append(fn(pd.concat([groups[r] for r in pick], ignore_index=True)))
    return np.percentile(vals, [2.5, 97.5])


def horizon_tables(lf, b=2000):
    mae = lambda fr, m: float((fr[f"pred_{m}"] - fr["y"]).abs().mean())
    by_h = lf.groupby("h").apply(lambda fr: pd.Series({"n": len(fr), **{m: mae(fr, m) for m in MODELS}}),
                                 include_groups=False).reset_index()
    best_ml = "xgboost_direct"
    rows = []
    for h in range(1, H + 1):
        fr = lf[lf["h"] == h]
        if fr.empty:
            continue
        sk = race_boot(fr, lambda x: 1 - mae(x, best_ml) / mae(x, "persistence"), b)
        dl = race_boot(fr, lambda x: mae(x, "lstm_multi") - mae(x, best_ml), b)
        rows.append({"h": h, "n": len(fr),
                     "xgb skill": 1 - mae(fr, best_ml) / mae(fr, "persistence"),
                     "skill 95% low": sk[0], "skill 95% high": sk[1],
                     "lstm minus xgb (s)": mae(fr, "lstm_multi") - mae(fr, best_ml),
                     "diff 95% low": dl[0], "diff 95% high": dl[1]})
    return by_h, pd.DataFrame(rows)


def cumulative(pred, k=H):
    """Error in the total time of the next k laps, for origins where all k are scored."""
    ok = pred[[f"valid_h{h}" for h in range(1, k + 1)]].all(axis=1)
    p = pred[ok]
    if p.empty:
        return pd.DataFrame(), p
    actual = p[[f"y_h{h}" for h in range(1, k + 1)]].sum(axis=1)
    rows = []
    for m in MODELS:
        tot = p[[f"{m}_h{h}" for h in range(1, k + 1)]].sum(axis=1)
        e = tot - actual
        rows.append({"model": m, "origins": len(p), "MAE of total (s)": e.abs().mean(),
                     "median abs (s)": e.abs().median(), "bias (s)": e.mean()})
    return pd.DataFrame(rows).sort_values("MAE of total (s)"), p


def frozen_settings(p2=None, p3=None):
    t2 = json.loads((p2 or P2_TUNING).read_text())
    t3 = json.loads((p3 or P3_TUNING).read_text())
    xgb = dict(t2["xgboost"]["best"])
    nets = {a: t3[a]["best"] for a in NEURAL}
    return xgb, nets


def report(pred, runtime, title, note, out: Path, n_seeds, b=2000):
    lf = long_format(pred)
    by_h, h_ci = horizon_tables(lf, b)
    cum, _ = cumulative(pred)
    parts = [f"# {title}", note,
             f"- Origins: {len(pred)} from {pred['race_id'].nunique()} races; scored "
             f"(origin, horizon) pairs: {len(lf)}. Every model forecasts the same pairs.",
             f"- Neural models: mean of {n_seeds} seeds, one network forecasting all {H} laps.",
             "## MAE by horizon (s)",
             "The sample shrinks with the horizon: long horizons need long stints without a "
             "neutralisation.",
             _md(by_h),
             "## XGBoost skill and LSTM vs XGBoost by horizon (race-clustered 95% intervals)",
             _md(h_ci, 4),
             f"## Total time of the next {H} laps",
             "Origins where all ten laps are scored. This is the quantity a strategy "
             "simulator adds up.",
             _md(cum) if not cum.empty else "_no origin with all ten laps scored_",
             "## Compute (seconds, summed over folds)",
             _md(pd.DataFrame([runtime]), 1)]
    (out / "report.md").write_text("\n\n".join(parts) + "\n")
    return out / "report.md"


def run_horizon_dev(features_path=None, out=None, quick=False, n_seeds=3, p2=None, p3=None,
                    boot_b=2000):
    out = out or OUT
    out.mkdir(parents=True, exist_ok=True)
    started = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    full, seq = load(features_path)
    xgb, nets = frozen_settings(p2, p3)
    n_seeds = 1 if quick else n_seeds
    pred, runtime = predict_folds(full, seq, "dev", xgb, nets, n_seeds=n_seeds, quick=quick,
                                  max_epochs=5 if quick else 40)
    pred.to_parquet(out / "predictions.parquet", index=False)
    (out / "run_meta.json").write_text(json.dumps({
        "started_utc": started, "quick": quick, "n_seeds": n_seeds, "horizon": H,
        "xgb_settings": xgb, "net_settings": nets, "runtime_s": runtime}, indent=2))
    return report(pred, runtime, "Task 2: multi-lap forecasts on the development races",
                  "2025 rounds 1-12, one race at a time from all earlier races. Test set not "
                  "loaded. Settings carried over from Task 1, not retuned.",
                  out, n_seeds, b=200 if quick else boot_b)
