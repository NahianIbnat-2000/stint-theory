"""Phase 2 experiment: tune on 2024, evaluate on 2025 R1-12 one race at a time.

    python -m models dev            # full run
    python -m models dev --quick    # small grids, few folds: a smoke test only

Writes research/results/phase2_dev/ :
    report.md, metrics.json, tuning.json, run_meta.json  (committed)
    predictions.parquet                                  (git-ignored, row-level)
"""
from __future__ import annotations

import datetime as dt
import json
import logging
import platform
import time
from pathlib import Path

import numpy as np
import pandas as pd

from pipelines import config
from . import data, evaluate, zoo

log = logging.getLogger(__name__)
OUT = config.ROOT / "research" / "results" / "phase2_dev"
MODELS = ["persistence", "compound_drift", "ridge", "mixed_effects", "random_forest", "xgboost"]
REFERENCE = "persistence"


def _mae(y, p):
    return float(np.mean(np.abs(np.asarray(p) - np.asarray(y))))


def tune(df: pd.DataFrame, quick: bool = False) -> dict:
    """Pick hyperparameters by mean MAE over the 2024 tuning blocks."""
    s = data.scored_sample(df)
    results = {}
    for name, grid in zoo.GRIDS.items():
        grid = grid[:2] if quick else grid
        scores = []
        for params in grid:
            fold_mae = []
            for tr, va, label in data.tuning_blocks(s):
                if len(tr) == 0:
                    continue
                m = zoo.make_model(name, **params).fit(s.loc[tr])
                fold_mae.append(_mae(s.loc[va, "y_next_lap_time_s"], m.predict(s.loc[va])))
            scores.append({"params": params, "mean_mae": float(np.mean(fold_mae)),
                           "fold_mae": fold_mae})
            log.info("tune %s %s -> %.4f", name, params, scores[-1]["mean_mae"])
        best = min(scores, key=lambda r: r["mean_mae"])
        results[name] = {"best": best["params"], "grid": scores,
                         "at_grid_edge": zoo.edge_params(name, best["params"])}
    # persistence on the same blocks, so tuning MAEs can be read as skill
    pm = [_mae(s.loc[va, "y_next_lap_time_s"], s.loc[va, "ref"])
          for tr, va, _ in data.tuning_blocks(s) if len(tr)]
    results["_persistence"] = {"mean_mae": float(np.mean(pm))}
    results["_grid_version"] = zoo.GRID_VERSION
    return results


def dev_predictions(df: pd.DataFrame, best: dict, quick: bool = False, split: str = "dev",
                    models: list[str] | None = None) -> tuple[pd.DataFrame, dict]:
    """Rolling origin over the dev races. Every model predicts the same rows."""
    s = data.scored_sample(df)
    models = models or MODELS
    eval_mask = s["split"] == split
    folds = list(data.rolling_folds(s, eval_mask))
    if quick:
        folds = folds[:2]
    out, runtime = [], {m: {"fit_s": 0.0, "predict_s": 0.0} for m in models}
    for tr, ev, race_id in folds:
        train, test = s.loc[tr], s.loc[ev]
        assert train["race_order"].max() < test["race_order"].min()  # no look-ahead
        frame = test[["race_id", "season", "round", "event_name", "driver", "team",
                      "lap_number", "compound_relative", "tyre_life", "target_tyre_life",
                      "target_valid_strict"]].copy()
        frame["y"] = test["y_next_lap_time_s"].to_numpy()
        frame["n_train_rows"] = len(train)
        for name in models:
            t0 = time.perf_counter()
            m = zoo.make_model(name, **best.get(name, {})).fit(train)
            t1 = time.perf_counter()
            frame[f"pred_{name}"] = m.predict(test)
            t2 = time.perf_counter()
            runtime[name]["fit_s"] += t1 - t0
            runtime[name]["predict_s"] += t2 - t1
            if name == "mixed_effects":
                frame["mixed_converged"] = getattr(m, "converged", None)
                frame["mixed_fit_mode"] = getattr(m, "fit_mode", None)
        out.append(frame)
        log.info("dev race %s done (%d rows, trained on %d)", race_id, len(test), len(train))
    return pd.concat(out, ignore_index=True), runtime


def _md(df: pd.DataFrame, digits: int = 3) -> str:
    df = df.copy()
    for c in df.select_dtypes("number").columns:
        df[c] = df[c].round(digits)
    cols = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in df.itertuples(index=False):
        lines.append("| " + " | ".join("" if pd.isna(v) else str(v) for v in r) + " |")
    return "\n".join(lines)


def write_report(pred, summary, summary_strict, boot, tuning, runtime, meta, out: Path) -> Path:
    best = summary.iloc[0]["model"]
    pairs = boot["pairs"]

    def pair(a, c):
        k, sign = (f"{a}|{c}", 1) if f"{a}|{c}" in pairs else (f"{c}|{a}", -1)
        lo, hi = pairs[k]["mae_diff_ci"]
        return (lo, hi) if sign == 1 else (-hi, -lo)

    cmp_rows = []
    for m in MODELS:
        if m == best:
            continue
        lo, hi = pair(m, best)
        w = evaluate.per_race_wins(pred, m, best)
        cmp_rows.append({"model": m, f"MAE minus {best} (s), 95% CI low": lo, "CI high": hi,
                         "clearly worse": lo > 0, "races where better": f"{w['a_better']}/{w['races']}"})
    pred = pred.assign(tyre_age_bin=pd.cut(pred["target_tyre_life"], [0, 5, 10, 15, 20, 30, 80]))
    parts = [
        "# Phase 2: next-lap prediction on the development races",
        f"Generated {meta['finished_utc']}. Development sample: 2025 rounds 1-12, "
        "predicted one race at a time from every earlier race. The 2025 R13-24 test set "
        "was not loaded. These are development results, not final test results.",
        f"- Scored laps: {len(pred)} from {pred['race_id'].nunique()} races. Every model "
        "predicts exactly the same laps.",
        f"- Benchmark: `{REFERENCE}` = last green lap of the stint (or recent field median).",
        "- Intervals: 95%, race-clustered bootstrap "
        f"({boot['b']} resamples of {boot['races']} races). With this few races the "
        "intervals are approximate and tend to be too narrow; read them as a guide.",
        "## Accuracy (default clean sample)",
        "Skill = 1 - MAE / MAE of persistence. Positive means better than repeating the last lap.",
        _md(summary[["model", "n", "mae", "mae_ci_low", "mae_ci_high", "rmse", "median_ae",
                     "bias", "skill_vs_persistence", "skill_ci_low", "skill_ci_high"]]),
        f"## Is the lowest-MAE model ({best}) clearly better?",
        "A model is clearly worse only if the whole interval for its MAE difference is "
        "above zero. Overlapping intervals mean the data cannot separate the two models.",
        _md(pd.DataFrame(cmp_rows)),
        "## Sensitivity: strict sample (pace outliers removed from the targets)",
        "Same predictions, scored only on targets that are not pace outliers.",
        _md(summary_strict[["model", "n", "mae", "rmse", "skill_vs_persistence"]]),
        "## MAE by tyre age of the predicted lap (s)",
        _md(evaluate.breakdown(pred, MODELS, "tyre_age_bin")),
        "## MAE by compound (s)",
        _md(evaluate.breakdown(pred, MODELS, "compound_relative")),
        "## MAE by race (s)",
        _md(evaluate.breakdown(pred, MODELS, "race_id")),
        f"## Chosen hyperparameters (tuned on 2024 only, grid version {tuning['_grid_version']})",
        f"Persistence MAE on the same 2024 blocks: {tuning['_persistence']['mean_mae']:.3f} s. "
        "A choice on the edge of its grid means a better value may lie outside it.",
        _md(pd.DataFrame([{"model": k, "params": json.dumps(v["best"]),
                           "tuning MAE": min(g["mean_mae"] for g in v["grid"]),
                           "tuning skill": 1 - min(g["mean_mae"] for g in v["grid"])
                           / tuning["_persistence"]["mean_mae"],
                           "on grid edge": ", ".join(v["at_grid_edge"]) or "no"}
                          for k, v in tuning.items() if not k.startswith("_")])),
        "## Compute (summed over all development folds, this machine)",
        _md(pd.DataFrame([{"model": k, **v} for k, v in runtime.items()]), 2),
        f"Mixed model converged on {meta['mixed_converged_folds']} of {meta['folds']} folds; "
        f"random-effect structure used: {meta['mixed_fit_modes']}.",
    ]
    path = out / "report.md"
    path.write_text("\n\n".join(parts) + "\n")
    return path


def run_dev(features_path: Path | None = None, out: Path | None = None, quick: bool = False,
            boot_b: int = evaluate.B_DEFAULT) -> Path:
    out = out or OUT
    out.mkdir(parents=True, exist_ok=True)
    started = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    df = data.load_features(features_path)
    assert not (df["split"] == "test").any()
    tuning = tune(df, quick=quick)
    best = {k: v["best"] for k, v in tuning.items() if not k.startswith("_")}
    pred, runtime = dev_predictions(df, best, quick=quick)
    boot = evaluate.bootstrap(pred, MODELS, REFERENCE, b=boot_b)
    summary = evaluate.summary_table(pred, MODELS, boot, REFERENCE)
    strict = pred[pred["target_valid_strict"]]
    summary_strict = evaluate.summary_table(
        strict, MODELS, evaluate.bootstrap(strict, MODELS, REFERENCE, b=200), REFERENCE)
    import sklearn, xgboost, statsmodels
    meta = {
        "started_utc": started,
        "finished_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "quick": quick, "folds": int(pred["race_id"].nunique()),
        "rows_scored": int(len(pred)),
        "train_rows_first_fold": int(pred["n_train_rows"].min()),
        "mixed_converged_folds": int(pred.groupby("race_id")["mixed_converged"].first().sum()),
        "mixed_fit_modes": pred.groupby("race_id")["mixed_fit_mode"].first().value_counts().to_dict(),
        "seeds": {"models": zoo.SEED, "bootstrap": evaluate.SEED},
        "versions": {"python": platform.python_version(), "pandas": pd.__version__,
                     "numpy": np.__version__, "sklearn": sklearn.__version__,
                     "xgboost": xgboost.__version__, "statsmodels": statsmodels.__version__},
        "split": {"train": list(data.TRAIN_SEASONS), "dev": "2025 R1-12",
                  "test": "2025 R13-24 (locked, not loaded)"},
    }
    pred.to_parquet(out / "predictions.parquet", index=False)
    (out / "metrics.json").write_text(json.dumps({
        "summary": summary.to_dict(orient="records"),
        "summary_strict": summary_strict.to_dict(orient="records"),
        "bootstrap": boot}, indent=2))
    (out / "tuning.json").write_text(json.dumps(tuning, indent=2))
    (out / "run_meta.json").write_text(json.dumps({**meta, "runtime": runtime}, indent=2))
    return write_report(pred, summary, summary_strict, boot, tuning, runtime, meta, out)
