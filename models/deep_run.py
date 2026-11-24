"""Phase 3 experiment: neural models on the Phase 2 development design.

    python -m models deep            # full run
    python -m models deep --quick    # smoke test

Uses the same scored laps, rolling-origin folds and 2024 tuning blocks as Phase 2,
and puts the frozen Phase 2 predictions (research/results/phase2_dev/predictions.parquet)
next to the neural ones, so every model is compared on the same laps.
Writes research/results/phase3_dev/.
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
from . import data, evaluate
from .deep import ARCHS, GRID, NeuralModel, build_sequences
from .run import _md, MODELS as P2_MODELS

log = logging.getLogger(__name__)
OUT = config.ROOT / "research" / "results" / "phase3_dev"
P2_PRED = config.ROOT / "research" / "results" / "phase2_dev" / "predictions.parquet"
KEY = ["race_id", "driver", "lap_number"]
N_SEEDS = 5


def _mae(y, p):
    return float(np.mean(np.abs(np.asarray(p) - np.asarray(y))))


def tune(s, seq, quick=False, max_epochs=40):
    out = {}
    grid = GRID[:1] if quick else GRID
    for arch in ARCHS:
        rows = []
        for params in grid:
            maes = []
            for tr, va, _ in data.tuning_blocks(s):
                if len(tr) == 0:
                    continue
                m = NeuralModel(arch, seed=0, max_epochs=max_epochs, **params)
                m.fit(s.loc[tr], seq[tr])
                maes.append(_mae(s.loc[va, "y_next_lap_time_s"], m.predict(s.loc[va], seq[va])))
            rows.append({"params": params, "mean_mae": float(np.mean(maes)), "fold_mae": maes})
            log.info("tune %s %s -> %.4f", arch, params, rows[-1]["mean_mae"])
        out[arch] = {"best": min(rows, key=lambda r: r["mean_mae"])["params"], "grid": rows}
    return out


def dev(s, seq, best, n_seeds=N_SEEDS, quick=False, max_epochs=40, split="dev"):
    folds = list(data.rolling_folds(s, s["split"] == split))
    if quick:
        folds = folds[:2]
    frames, runtime = [], {a: {"fit_s": 0.0, "predict_s": 0.0, "epochs": []} for a in ARCHS}
    for tr, ev, race_id in folds:
        train, test = s.loc[tr], s.loc[ev]
        assert train["race_order"].max() < test["race_order"].min()
        f = test[KEY].copy()
        for arch in ARCHS:
            preds = []
            for sd in range(n_seeds):
                t0 = time.perf_counter()
                m = NeuralModel(arch, seed=sd, max_epochs=max_epochs, **best[arch]).fit(train, seq[tr])
                t1 = time.perf_counter()
                p = m.predict(test, seq[ev])
                runtime[arch]["fit_s"] += t1 - t0
                runtime[arch]["predict_s"] += time.perf_counter() - t1
                runtime[arch]["epochs"].append(m.epochs_run)
                f[f"pred_{arch}_s{sd}"] = p
                preds.append(p)
            f[f"pred_{arch}"] = np.mean(preds, axis=0)   # seed ensemble
        frames.append(f)
        log.info("dev race %s done", race_id)
    return pd.concat(frames, ignore_index=True), runtime


def seed_table(pred, n_seeds):
    rows = []
    ref = (pred["pred_persistence"] - pred["y"]).abs().mean()
    for arch in ARCHS:
        maes = [(pred[f"pred_{arch}_s{s}"] - pred["y"]).abs().mean() for s in range(n_seeds)]
        rows.append({"model": arch, "seeds": n_seeds, "mae_mean": np.mean(maes),
                     "mae_sd": np.std(maes, ddof=1) if n_seeds > 1 else np.nan,
                     "mae_min": np.min(maes), "mae_max": np.max(maes),
                     "skill_mean": 1 - np.mean(maes) / ref,
                     "ensemble_mae": (pred[f"pred_{arch}"] - pred["y"]).abs().mean()})
    return pd.DataFrame(rows)


def run_deep(features_path: Path | None = None, p2_pred_path: Path | None = None,
             out: Path | None = None, quick: bool = False, n_seeds: int = N_SEEDS,
             boot_b: int = evaluate.B_DEFAULT) -> Path:
    out = out or OUT
    out.mkdir(parents=True, exist_ok=True)
    started = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    full = data.load_features(features_path)
    assert not (full["split"] == "test").any()
    t0 = time.perf_counter()
    seq_full = build_sequences(full)                  # aligned with full's RangeIndex
    seq_build_s = time.perf_counter() - t0
    s = data.scored_sample(full)
    seq = seq_full                                      # index labels == positions
    max_epochs = 5 if quick else 40
    n_seeds = 1 if quick else n_seeds
    tuning = tune(s, seq, quick=quick, max_epochs=max_epochs)
    best = {a: v["best"] for a, v in tuning.items()}
    dl, runtime = dev(s, seq, best, n_seeds=n_seeds, quick=quick, max_epochs=max_epochs)

    p2 = pd.read_parquet(p2_pred_path or P2_PRED)
    pred = p2.merge(dl, on=KEY, how="inner", validate="one_to_one")
    if len(pred) != len(dl):
        raise RuntimeError("Phase 2 and Phase 3 scored different laps; rerun Phase 2 first.")
    if not quick and len(pred) != len(p2):
        raise RuntimeError("Phase 3 did not score every Phase 2 lap.")
    models = P2_MODELS + ARCHS
    boot = evaluate.bootstrap(pred, models, "persistence", b=boot_b)
    summary = evaluate.summary_table(pred, models, boot, "persistence")
    seeds = seed_table(pred, n_seeds)
    strict = pred[pred["target_valid_strict"]]
    summary_strict = evaluate.summary_table(
        strict, models, evaluate.bootstrap(strict, models, "persistence", b=200), "persistence")

    def diff(a, c):
        k = f"{a}|{c}" if f"{a}|{c}" in boot["pairs"] else f"{c}|{a}"
        lo, hi = boot["pairs"][k]["mae_diff_ci"]
        if not k.startswith(a + "|"):
            lo, hi = -hi, -lo
        w = evaluate.per_race_wins(pred, a, c)
        return {"comparison": f"{a} minus {c}", "MAE diff CI low (s)": lo, "CI high": hi,
                "verdict": ("a better" if hi < 0 else "c better" if lo > 0 else "no clear difference"),
                "races a better": f"{w['a_better']}/{w['races']}"}

    comps = pd.DataFrame([diff(a, "xgboost") for a in ARCHS] +
                         [diff("lstm", "mlp"), diff("tcn", "mlp"), diff("lstm", "tcn")])
    comps["verdict"] = [v.replace("a better", r.split(" minus ")[0] + " better")
                         .replace("c better", r.split(" minus ")[1] + " better")
                        for v, r in zip(comps["verdict"], comps["comparison"])]
    pred = pred.assign(tyre_age_bin=pd.cut(pred["target_tyre_life"], [0, 5, 10, 15, 20, 30, 80]))
    rt = pd.DataFrame([{"model": a, "fit_s": v["fit_s"], "predict_s": v["predict_s"],
                        "median_epochs": float(np.median(v["epochs"]))} for a, v in runtime.items()])
    finished = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    parts = [
        "# Phase 3: neural models on the development races",
        f"Generated {finished}. Same scored laps, folds and tuning blocks as Phase 2; the "
        "Phase 2 models are the frozen run. The 2025 R13-24 test set was not loaded. "
        "Development results, not final test results.",
        f"- Scored laps: {len(pred)} from {pred['race_id'].nunique()} races.",
        f"- Neural predictions are the mean of {n_seeds} seeds; single-seed spread is shown below.",
        "- Intervals: 95% race-clustered bootstrap; approximate with this few races.",
        "## Accuracy, all models (default clean sample)",
        _md(summary[["model", "n", "mae", "mae_ci_low", "mae_ci_high", "rmse", "median_ae",
                     "bias", "skill_vs_persistence", "skill_ci_low", "skill_ci_high"]]),
        "## Key comparisons",
        "Neural models against XGBoost, then the temporal-history ablation: LSTM and TCN "
        "see the lap sequence, the MLP does not; all three see the same tabular inputs.",
        _md(comps),
        "## Seed variability (single seeds, not the ensemble)",
        _md(seeds, 4),
        "## Sensitivity: strict sample",
        _md(summary_strict[["model", "n", "mae", "rmse", "skill_vs_persistence"]]),
        "## MAE by tyre age of the predicted lap (s)",
        _md(evaluate.breakdown(pred, models, "tyre_age_bin")),
        "## MAE by compound (s)",
        _md(evaluate.breakdown(pred, models, "compound_relative")),
        "## Chosen settings (tuned on 2024 blocks, seed 0)",
        _md(pd.DataFrame([{"model": a, "params": json.dumps(v["best"]),
                           "tuning MAE": min(g["mean_mae"] for g in v["grid"])}
                          for a, v in tuning.items()])),
        "## Compute (CPU, summed over development folds and seeds)",
        f"Building lap sequences: {seq_build_s:.1f} s.",
        _md(rt, 2),
    ]
    (out / "report.md").write_text("\n\n".join(parts) + "\n")
    pred.drop(columns=["tyre_age_bin"]).to_parquet(out / "predictions.parquet", index=False)
    import torch
    (out / "metrics.json").write_text(json.dumps({
        "summary": summary.to_dict(orient="records"), "seeds": seeds.to_dict(orient="records"),
        "comparisons": comps.to_dict(orient="records"), "bootstrap": boot}, indent=2, default=float))
    (out / "tuning.json").write_text(json.dumps(tuning, indent=2))
    (out / "run_meta.json").write_text(json.dumps({
        "started_utc": started, "finished_utc": finished, "quick": quick, "n_seeds": n_seeds,
        "max_epochs": max_epochs, "seq_len": int(seq.shape[1]), "torch": torch.__version__,
        "runtime": {k: {**v, "epochs": list(map(int, v["epochs"]))} for k, v in runtime.items()}},
        indent=2))
    return out / "report.md"
