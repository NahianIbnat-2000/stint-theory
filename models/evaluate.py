"""Metrics, race-clustered bootstrap and paired model comparisons.

Laps within a race share track conditions, so errors are correlated within races.
Intervals therefore resample whole races, not laps.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

B_DEFAULT = 2000
SEED = 7


def point_metrics(y: np.ndarray, yhat: np.ndarray) -> dict:
    e = yhat - y
    a = np.abs(e)
    return {"n": int(len(y)), "mae": float(a.mean()), "rmse": float(np.sqrt((e ** 2).mean())),
            "median_ae": float(np.median(a)), "bias": float(e.mean())}


def _race_sums(pred: pd.DataFrame, models: list[str]):
    """Per race: count, sum of |error| and sum of squared error for each model."""
    g = pred.groupby("race_id")
    n = g.size().to_numpy(float)
    abs_s = np.column_stack([g[f"abs_{m}"].sum().to_numpy() for m in models])
    sq_s = np.column_stack([g[f"sq_{m}"].sum().to_numpy() for m in models])
    return n, abs_s, sq_s


def bootstrap(pred: pd.DataFrame, models: list[str], reference: str,
              b: int = B_DEFAULT, seed: int = SEED) -> dict:
    """Race-clustered bootstrap of MAE, RMSE, skill vs `reference` and MAE
    differences between every pair of models. Returns 95% percentile intervals."""
    pred = pred.copy()
    for m in models:
        e = pred[f"pred_{m}"] - pred["y"]
        pred[f"abs_{m}"] = e.abs()
        pred[f"sq_{m}"] = e ** 2
    n, abs_s, sq_s = _race_sums(pred, models)
    rng = np.random.default_rng(seed)
    k = len(n)
    w = rng.multinomial(k, np.full(k, 1 / k), size=b).astype(float)  # b x races
    tot = w @ n
    mae = (w @ abs_s) / tot[:, None]
    rmse = np.sqrt((w @ sq_s) / tot[:, None])
    ref_i = models.index(reference)
    skill = 1 - mae / mae[:, [ref_i]]
    ci = lambda x: [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]
    out = {"b": b, "races": k, "models": {}}
    for j, m in enumerate(models):
        out["models"][m] = {"mae_ci": ci(mae[:, j]), "rmse_ci": ci(rmse[:, j]),
                            "skill_vs_ref_ci": ci(skill[:, j])}
    out["pairs"] = {}
    for i, a in enumerate(models):
        for j, c in enumerate(models):
            if i < j:
                d = mae[:, i] - mae[:, j]
                out["pairs"][f"{a}|{c}"] = {"mae_diff_ci": ci(d),
                                            "share_boot_a_better": float((d < 0).mean())}
    return out


def per_race_wins(pred: pd.DataFrame, a: str, c: str) -> dict:
    g = pred.assign(ea=(pred[f"pred_{a}"] - pred["y"]).abs(),
                    ec=(pred[f"pred_{c}"] - pred["y"]).abs()).groupby("race_id")[["ea", "ec"]].mean()
    return {"races": int(len(g)), "a_better": int((g.ea < g.ec).sum()),
            "c_better": int((g.ec < g.ea).sum())}


def summary_table(pred: pd.DataFrame, models: list[str], boot: dict, reference: str) -> pd.DataFrame:
    rows = []
    ref_mae = np.abs(pred[f"pred_{reference}"] - pred["y"]).mean()
    for m in models:
        pm = point_metrics(pred["y"].to_numpy(), pred[f"pred_{m}"].to_numpy())
        bm = boot["models"][m]
        rows.append({"model": m, **pm, "skill_vs_persistence": 1 - pm["mae"] / ref_mae,
                     "mae_ci_low": bm["mae_ci"][0], "mae_ci_high": bm["mae_ci"][1],
                     "skill_ci_low": bm["skill_vs_ref_ci"][0],
                     "skill_ci_high": bm["skill_vs_ref_ci"][1]})
    return pd.DataFrame(rows).sort_values("mae").reset_index(drop=True)


def breakdown(pred: pd.DataFrame, models: list[str], by: str) -> pd.DataFrame:
    out = []
    for key, g in pred.groupby(by, observed=True, dropna=False):
        row = {by: str(key), "n": len(g)}
        for m in models:
            row[m] = float((g[f"pred_{m}"] - g["y"]).abs().mean())
        out.append(row)
    return pd.DataFrame(out)


# ---------------------------------------------------------------- final test
def paired_diff_samples(pred: pd.DataFrame, a: str, c: str, b: int = B_DEFAULT,
                        seed: int = SEED) -> tuple[float, np.ndarray]:
    """MAE(a) - MAE(c): point value and race-clustered bootstrap samples.
    Negative means a has the lower error."""
    ea = (pred[f"pred_{a}"] - pred["y"]).abs()
    ec = (pred[f"pred_{c}"] - pred["y"]).abs()
    g = pd.DataFrame({"race": pred["race_id"], "ea": ea, "ec": ec}).groupby("race")
    n = g.size().to_numpy(float)
    sa, sc = g["ea"].sum().to_numpy(), g["ec"].sum().to_numpy()
    rng = np.random.default_rng(seed)
    k = len(n)
    w = rng.multinomial(k, np.full(k, 1 / k), size=b).astype(float)
    tot = w @ n
    d = (w @ sa - w @ sc) / tot
    return float(ea.mean() - ec.mean()), d


def bootstrap_p(d: np.ndarray) -> float:
    """Two-sided bootstrap p-value for 'no difference' (share of resamples on the
    other side of zero, doubled, capped at 1)."""
    return float(min(1.0, 2 * min((d <= 0).mean(), (d >= 0).mean())))


def holm(pvals: dict) -> dict:
    """Holm step-down adjusted p-values."""
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m, out, running = len(items), {}, 0.0
    for i, (k, p) in enumerate(items):
        running = max(running, min(1.0, (m - i) * p))
        out[k] = running
    return out


def classify(point: float, d: np.ndarray, p_adj: float, margin: float,
             alpha: float = 0.05) -> str:
    """Pre-registered decision rule (docs/preregistration.md, section 4)."""
    lo95, hi95 = np.percentile(d, [2.5, 97.5])
    lo90, hi90 = np.percentile(d, [5, 95])
    if p_adj < alpha and (hi95 < -margin or lo95 > margin):
        return "meaningful difference"
    if lo90 > -margin and hi90 < margin:
        return ("equivalent (statistically different, within margin)" if p_adj < alpha
                else "equivalent")
    if p_adj < alpha:
        return "statistically different, size unclear"
    return "inconclusive"
