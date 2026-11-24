"""The one pre-registered run on the locked test set (2025 rounds 13-24).

    STINT_UNLOCK_TEST=I_HAVE_FROZEN_ALL_MODELS python -m models test -v

Rules: docs/preregistration.md. The runner refuses to start if the pre-registration
is missing or not committed to git, or if a final report already exists.
Writes research/results/final_test/.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import logging
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from pipelines import config
from . import data, evaluate
from .deep import ARCHS, build_sequences
from .deep_run import KEY, N_SEEDS, dev as deep_folds, seed_table
from .run import MODELS as P2_MODELS, _md, dev_predictions

log = logging.getLogger(__name__)
OUT = config.ROOT / "research" / "results" / "final_test"
PREREG = config.ROOT / "docs" / "preregistration.md"
P2_TUNING = config.ROOT / "research" / "results" / "phase2_dev" / "tuning.json"
P3_TUNING = config.ROOT / "research" / "results" / "phase3_dev" / "tuning.json"
MARGIN = 0.01
PRIMARY = [("tcn", "xgboost_ens5"), ("lstm", "xgboost_ens5"), ("mlp", "xgboost_ens5"),
           ("lstm", "mlp"), ("tcn", "mlp")]
ALL_MODELS = P2_MODELS + ["xgboost_ens5"] + ARCHS


class NotPreregistered(RuntimeError):
    pass


def _git(*args) -> str | None:
    try:
        return subprocess.run(["git", *args], cwd=config.ROOT, capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:
        return None


def check_preregistration(allow_uncommitted: bool = False, path: Path | None = None) -> dict:
    path = path or PREREG
    if not path.exists():
        raise NotPreregistered(f"{path.name} is missing.")
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    info = {"file": path.name, "sha256": sha, "git_commit": _git("rev-parse", "HEAD"),
            "prereg_committed_at": _git("log", "-1", "--format=%cI", "--", str(path))}
    tracked = _git("ls-files", "--error-unmatch", str(path)) is not None
    dirty = _git("status", "--porcelain", "--", str(path))
    if not allow_uncommitted and (not tracked or dirty):
        raise NotPreregistered(
            f"Commit docs/{path.name} to git before running the test "
            f"(git add docs/{path.name} && git commit -m 'Pre-register').")
    info["committed"] = bool(tracked and not dirty)
    return info


def run_test(features_path: Path | None = None, out: Path | None = None, quick: bool = False,
             force: bool = False, allow_uncommitted: bool = False,
             p2_tuning: Path | None = None, p3_tuning: Path | None = None,
             boot_b: int = evaluate.B_DEFAULT, access_log: Path | None = None) -> Path:
    out = out or OUT
    prereg = check_preregistration(allow_uncommitted)
    if (out / "report.md").exists() and not force:
        raise RuntimeError(f"{out/'report.md'} exists. The test is run once (pre-registration "
                           "section 7). Use --force only to rerun after a logged crash.")
    out.mkdir(parents=True, exist_ok=True)
    started = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    best2 = {k: v["best"] for k, v in json.loads((p2_tuning or P2_TUNING).read_text()).items()
             if not k.startswith("_")}
    best2["xgboost_ens5"] = best2["xgboost"]
    best3 = {k: v["best"] for k, v in json.loads((p3_tuning or P3_TUNING).read_text()).items()}

    full = data.load_features(features_path, include_test=True,
                              reason=f"final test run, prereg sha256 {prereg['sha256'][:12]}",
                              log=access_log)
    n_seeds = 1 if quick else N_SEEDS
    max_epochs = 5 if quick else 40
    p2, rt2 = dev_predictions(full, best2, quick=quick, split="test",
                              models=P2_MODELS + ["xgboost_ens5"])
    seq = build_sequences(full)
    s = data.scored_sample(full)
    p3, rt3 = deep_folds(s, seq, best3, n_seeds=n_seeds, quick=quick, max_epochs=max_epochs,
                         split="test")
    pred = p2.merge(p3, on=KEY, how="inner", validate="one_to_one")
    assert len(pred) == len(p2) == len(p3), "models scored different laps"
    assert set(pred["season"]) == {2025} and pred["round"].min() >= 13

    boot = evaluate.bootstrap(pred, ALL_MODELS, "persistence", b=boot_b)
    summary = evaluate.summary_table(pred, ALL_MODELS, boot, "persistence")

    # primary comparisons
    rows, samples, pvals = [], {}, {}
    for a, c in PRIMARY:
        k = f"{a} vs {c}"
        point, d = evaluate.paired_diff_samples(pred, a, c, b=boot_b)
        samples[k], pvals[k] = (point, d), evaluate.bootstrap_p(d)
    adj = evaluate.holm(pvals)
    for i, (a, c) in enumerate(PRIMARY, 1):
        k = f"{a} vs {c}"
        point, d = samples[k]
        w = evaluate.per_race_wins(pred, a, c)
        rows.append({"#": f"P{i}", "comparison": k, "MAE diff (s)": point,
                     "95% low": np.percentile(d, 2.5), "95% high": np.percentile(d, 97.5),
                     "90% low": np.percentile(d, 5), "90% high": np.percentile(d, 95),
                     "p": pvals[k], "Holm p": adj[k],
                     "label": evaluate.classify(point, d, adj[k], MARGIN),
                     f"races {a} better": f"{w['a_better']}/{w['races']}"})
    primary = pd.DataFrame(rows)

    def ci_row(name, frame, a, c):
        if frame.empty:
            return {"analysis": name, "comparison": f"{a} vs {c}", "n laps": 0}
        point, d = evaluate.paired_diff_samples(frame, a, c, b=boot_b)
        return {"analysis": name, "comparison": f"{a} vs {c}", "n laps": len(frame),
                "MAE diff (s)": point, "95% low": np.percentile(d, 2.5),
                "95% high": np.percentile(d, 97.5)}

    old = pred[pred["target_tyre_life"] > 30]
    secondary = pd.DataFrame([
        ci_row("S1 tyres > 30 laps", old, "lstm", "xgboost_ens5"),
        ci_row("S1 tyres > 30 laps", old, "tcn", "xgboost_ens5"),
        ci_row("S5 seed averaging", pred, "xgboost_ens5", "xgboost"),
    ])
    seeds = seed_table(pred, n_seeds)
    xgb_single = float((pred["pred_xgboost"] - pred["y"]).abs().mean())
    strict = pred[pred["target_valid_strict"]]
    summary_strict = evaluate.summary_table(
        strict, ALL_MODELS, evaluate.bootstrap(strict, ALL_MODELS, "persistence", b=500),
        "persistence")
    runtime = pd.DataFrame(
        [{"model": k, "fit_s": v["fit_s"], "predict_s": v["predict_s"]} for k, v in rt2.items()] +
        [{"model": k, "fit_s": v["fit_s"], "predict_s": v["predict_s"]} for k, v in rt3.items()])
    finished = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

    parts = [
        "# Final test: next-lap prediction (pre-registered)",
        f"Run {started} to {finished}. Test set: 2025 rounds 13-24, opened once for this run. "
        "Rules: `docs/preregistration.md`, "
        f"SHA-256 `{prereg['sha256']}`, committed {prereg['prereg_committed_at']}, "
        f"code commit `{prereg['git_commit']}`" + ("" if prereg["committed"] else
        " (**pre-registration NOT committed: this run is not valid as a final test**)") + ".",
        f"- Scored laps: {len(pred)} from {pred['race_id'].nunique()} races. Every model "
        "predicts the same laps.",
        f"- Neural models: mean of {n_seeds} seeds. xgboost_ens5: mean of 5 XGBoost seeds.",
        f"- Practical margin: {MARGIN} s. Holm correction over the five primary comparisons.",
        "## Primary comparisons (pre-registered, section 4)",
        "Negative MAE difference: the first model is more accurate.",
        _md(primary, 4),
        "## Accuracy, all models",
        _md(summary[["model", "n", "mae", "mae_ci_low", "mae_ci_high", "rmse", "median_ae",
                     "bias", "skill_vs_persistence", "skill_ci_low", "skill_ci_high"]]),
        "## Secondary analyses (no multiplicity correction)",
        _md(secondary, 4),
        f"S2. Single seeds (single XGBoost MAE: {xgb_single:.4f} s):",
        _md(seeds, 4),
        "S4. Strict sample:",
        _md(summary_strict[["model", "n", "mae", "rmse", "skill_vs_persistence"]]),
        "## MAE by tyre age of the predicted lap (s)",
        _md(evaluate.breakdown(pred.assign(tyre_age_bin=pd.cut(
            pred["target_tyre_life"], [0, 5, 10, 15, 20, 30, 80])), ALL_MODELS, "tyre_age_bin")),
        "## MAE by race (s)",
        _md(evaluate.breakdown(pred, ALL_MODELS, "race_id")),
        "## S6. Compute (this machine, summed over test folds)",
        _md(runtime, 2),
    ]
    (out / "report.md").write_text("\n\n".join(parts) + "\n")
    pred.to_parquet(out / "predictions.parquet", index=False)
    (out / "metrics.json").write_text(json.dumps({
        "primary": primary.to_dict(orient="records"),
        "secondary": secondary.to_dict(orient="records"),
        "summary": summary.to_dict(orient="records"),
        "seeds": seeds.to_dict(orient="records"), "bootstrap": boot}, indent=2, default=float))
    (out / "run_meta.json").write_text(json.dumps({
        "started_utc": started, "finished_utc": finished, "quick": quick,
        "preregistration": prereg, "margin_s": MARGIN, "n_seeds": n_seeds,
        "hyperparameters": {"phase2": best2, "phase3": best3}}, indent=2, default=str))
    return out / "report.md"
