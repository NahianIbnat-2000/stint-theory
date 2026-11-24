"""Task 3: pace change associated with tyre age.

Estimand: the change in lap time associated with one more lap of tyre age, by
compound, holding constant
  * everything common to all cars on a given lap of a given race (fuel burn,
    track evolution, track temperature, wind): race x lap fixed effects,
  * the driver-car's pace in that race: driver x race fixed effects, and
  * the pace level of each compound at that race: race x compound fixed effects.

Identification: within a stint, tyre age = lap - stint start, so with driver x
stint effects the linear tyre slope is NOT identified (age-period-cohort problem;
fe_ols raises NotIdentified). With driver x race effects it is identified from the
pace gain at each pit stop, compared across drivers who stopped after different
numbers of laps. Key assumptions: a driver's underlying pace is the same across
stints, and compound pace offsets at a race are common to all cars.
Assumptions and threats are in docs/methodology_tyre.md. Results are an estimated
association with tyre age, not measured tyre wear.

The estimator is OLS with two high-dimensional fixed effects absorbed by
alternating projections, and standard errors clustered by race (CR1, fixed
effects nested in clusters are not counted as parameters, as in reghdfe).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

COMPOUNDS = ["SOFT", "MEDIUM", "HARD"]


class NotIdentified(ValueError):
    pass


# ------------------------------------------------------------- estimator
def _codes(s: pd.Series) -> np.ndarray:
    return pd.factorize(s, sort=False)[0]


def drop_singletons(df: pd.DataFrame, fe: list[str]) -> pd.DataFrame:
    """Repeatedly drop observations alone in any fixed-effect group."""
    while True:
        keep = np.ones(len(df), bool)
        for f in fe:
            keep &= df.groupby(f)[f].transform("size").to_numpy() > 1
        if keep.all():
            return df
        df = df[keep]


def demean(M: np.ndarray, groups: list[np.ndarray], tol: float = 1e-10,
           max_iter: int = 10_000) -> np.ndarray:
    """Project out several sets of fixed effects (alternating projections)."""
    M = M.astype(float).copy()
    counts = [np.bincount(g).astype(float) for g in groups]
    for _ in range(max_iter):
        before = M.copy()
        for g, c in zip(groups, counts):
            for j in range(M.shape[1]):
                M[:, j] -= (np.bincount(g, weights=M[:, j]) / c)[g]
        if np.max(np.abs(M - before)) < tol:
            return M
    raise RuntimeError("fixed-effect demeaning did not converge")


def fe_ols(df: pd.DataFrame, y: str, xs: list[str], fe: list[str], cluster: str) -> dict:
    """OLS of y on xs with absorbed fixed effects; cluster-robust (CR1) covariance."""
    d = drop_singletons(df.dropna(subset=[y] + xs), fe)
    groups = [_codes(d[f]) for f in fe]
    Z = demean(np.column_stack([d[y].to_numpy(float)] + [d[x].to_numpy(float) for x in xs]),
               groups)
    yt, X = Z[:, 0], Z[:, 1:]
    keep = np.abs(X).sum(axis=0) > 1e-9                     # drop columns absorbed by the FE
    X, names = X[:, keep], [x for x, k in zip(xs, keep) if k]
    # refuse to report coefficients that the fixed effects make unidentified
    sv = np.linalg.svd(X / np.maximum(np.linalg.norm(X, axis=0), 1e-12), compute_uv=False)
    if len(sv) and sv[-1] < 1e-6 * sv[0]:
        raise NotIdentified(
            f"{len(names)} regressors are collinear with the fixed effects {fe}; "
            "coefficients are not identified.")
    XtX_inv = np.linalg.inv(X.T @ X)
    b = XtX_inv @ X.T @ yt
    e = yt - X @ b
    cl = _codes(d[cluster])
    G, n, k = cl.max() + 1, len(yt), X.shape[1]
    if G < 2 or n <= k:
        raise NotIdentified("too few clusters or observations for these regressors")
    S = np.zeros((G, k))
    np.add.at(S, cl, X * e[:, None])
    V = XtX_inv @ (S.T @ S) @ XtX_inv * (G / (G - 1)) * ((n - 1) / (n - k))
    se = np.sqrt(np.diag(V))
    return {"coef": pd.Series(b, index=names), "se": pd.Series(se, index=names),
            "vcov": pd.DataFrame(V, index=names, columns=names), "n": int(n),
            "clusters": int(G), "dropped_absorbed": [x for x, k in zip(xs, keep) if not k]}


# ------------------------------------------------------------- data
def estimation_sample(laps: pd.DataFrame, strict: bool = False) -> pd.DataFrame:
    """Dry, clean green laps on slicks; ids for the fixed effects."""
    flag = "is_clean_green_strict" if strict else "is_clean_green"
    laps = laps.reset_index(drop=True)
    d = laps[laps[flag] & laps["compound_relative"].isin(COMPOUNDS)].copy()
    d["race_lap"] = d["race_id"] + "_" + d["lap_number"].astype(str)
    d["driver_stint"] = d["race_id"] + "_" + d["driver"].astype(str) + "_" + d["stint"].astype(str)
    d["driver_race"] = d["race_id"] + "_" + d["driver"].astype(str)
    d["race_compound"] = d["race_id"] + "_" + d["compound_relative"].astype(str)
    d["race_stintno"] = d["race_id"] + "_s" + d["stint"].astype(str)
    first = laps.groupby(["race_id", "driver", "stint"])["lap_number"].transform("min")
    d["lap_in_stint"] = (laps.loc[d.index, "lap_number"] - first.loc[d.index] + 1).astype(int)
    for c in COMPOUNDS:
        on = (d["compound_relative"] == c).astype(float)
        d[f"age_{c}"] = d["tyre_life"] * on
        d[f"age2_{c}"] = d["tyre_life"] ** 2 * on
    return d


def slopes(res: dict, prefix: str = "age_") -> pd.DataFrame:
    rows = []
    for c in COMPOUNDS:
        k = f"{prefix}{c}"
        if k in res["coef"]:
            b, s = res["coef"][k], res["se"][k]
            rows.append({"compound": c, "s_per_lap": b, "se": s,
                         "ci_low": b - 1.96 * s, "ci_high": b + 1.96 * s})
    return pd.DataFrame(rows)


FE_MAIN = ["race_lap", "driver_race", "race_compound"]


def age_curve(d: pd.DataFrame, cap: int = 35, ref: int = 5) -> pd.DataFrame:
    """Non-parametric curve: tyre-age bin dummies by compound (reference age `ref`),
    same fixed effects. Ages above `cap` are pooled."""
    age = d["tyre_life"].clip(upper=cap).astype(int)
    new = {}
    for c in COMPOUNDS:
        on = d["compound_relative"] == c
        for a in range(1, cap + 1):
            if a != ref:
                new[f"b_{c}_{a}"] = ((age == a) & on).astype(float)
    cols = list(new)
    d = pd.concat([d, pd.DataFrame(new, index=d.index)], axis=1)
    res = fe_ols(d, "lap_time_s", cols, FE_MAIN, "race_id")
    rows = []
    for c in COMPOUNDS:
        n_by_age = d[d["compound_relative"] == c]["tyre_life"].clip(upper=cap).astype(int).value_counts()
        for a in range(1, cap + 1):
            col = f"b_{c}_{a}"
            if a == ref:
                b = s = 0.0
            elif col in res["coef"]:
                b, s = res["coef"][col], res["se"][col]
            else:
                continue
            rows.append({"compound": c, "tyre_age": a, "effect_s": b, "se": s,
                         "ci_low": b - 1.96 * s, "ci_high": b + 1.96 * s,
                         "laps": int(n_by_age.get(a, 0))})
    return pd.DataFrame(rows)
