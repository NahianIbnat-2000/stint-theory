"""Phase 2 models for next-lap time. All share one interface:

    m = make_model(name, **params); m.fit(train_df); yhat = m.predict(eval_df)

Except for the persistence benchmark, models learn the change from the reference
pace, y - ref (ref = last green lap of the stint, or the recent field median).
Predicting the change rather than the raw lap time keeps circuit lap-time levels
out of the problem, so every model is asked the same question. Imputation, scaling
and encoding live inside each model and are fitted on the training fold only.
"""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

SEED = 20260101

NUMERIC = [
    "lt_lag0", "lt_lag1", "last_green_lt", "roll_mean_green_3", "roll_std_green_5",
    "trend_slope_green_5", "green_laps_in_stint", "tyre_life", "target_tyre_life",
    "pit_stops_so_far", "lap_number", "scheduled_laps", "race_progress",
    "laps_remaining_sched", "position_end_of_lap", "grid_position", "track_temp_c",
    "air_temp_c", "humidity_pct", "field_green_median_recent", "rel_pace_to_field",
]
FLAGS = ["flag_sc", "flag_vsc", "flag_yellow", "flag_post_neutralisation", "fresh_tyre"]
CATEGORICAL = ["compound_relative", "prev_stint_compound", "event_name", "team"]


def _design(df: pd.DataFrame) -> pd.DataFrame:
    X = df[NUMERIC + FLAGS + CATEGORICAL].copy()
    for c in FLAGS:
        X[c] = X[c].astype("float")
    # ref-relative versions of the pace columns: the target is a change from ref
    for c in ("lt_lag0", "lt_lag1", "last_green_lt", "roll_mean_green_3",
              "field_green_median_recent"):
        X[c] = X[c] - df["ref"]
    X["tyre_life_sq"] = X["tyre_life"] ** 2
    for c in CATEGORICAL:
        X[c] = X[c].astype("object").where(X[c].notna(), "NA").astype(str)
    return X


def _preprocessor(scale: bool) -> ColumnTransformer:
    num = NUMERIC + FLAGS + ["tyre_life_sq"]
    num_steps = [SimpleImputer(strategy="median", add_indicator=True)]
    if scale:
        num_steps.append(StandardScaler())
    return ColumnTransformer([
        ("num", make_pipeline(*num_steps), num),
        ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=20,
                              sparse_output=False), CATEGORICAL),
    ])


class Persistence:
    family = "benchmark"

    def fit(self, df):
        return self

    def predict(self, df):
        return df["ref"].to_numpy(float)


class CompoundDrift:
    """ref plus the average lap-to-lap change seen in training for that compound."""
    family = "benchmark"

    def fit(self, df):
        d = df["y_next_lap_time_s"] - df["ref"]
        self.overall = float(d.mean())
        self.by_comp = d.groupby(df["compound_relative"]).mean().to_dict()
        return self

    def predict(self, df):
        add = df["compound_relative"].map(self.by_comp).astype(float).fillna(self.overall)
        return (df["ref"] + add).to_numpy(float)


class _ResidualSklearn:
    def __init__(self, estimator, scale: bool):
        self.pipe = Pipeline([("prep", _preprocessor(scale)), ("est", estimator)])

    def fit(self, df):
        self.pipe.fit(_design(df), (df["y_next_lap_time_s"] - df["ref"]).to_numpy(float))
        return self

    def predict(self, df):
        return df["ref"].to_numpy(float) + self.pipe.predict(_design(df))


class RidgeModel(_ResidualSklearn):
    family = "statistical"

    def __init__(self, alpha: float = 10.0):
        super().__init__(Ridge(alpha=alpha), scale=True)


class RandomForestModel(_ResidualSklearn):
    family = "machine_learning"

    def __init__(self, min_samples_leaf: int = 20, max_features: float = 0.3,
                 n_estimators: int = 200, n_jobs: int = -1):
        super().__init__(RandomForestRegressor(
            n_estimators=n_estimators, min_samples_leaf=min_samples_leaf,
            max_features=max_features, max_samples=0.5, n_jobs=n_jobs,
            random_state=SEED), scale=False)


class XGBModel(_ResidualSklearn):
    family = "machine_learning"

    def __init__(self, max_depth: int = 5, n_estimators: int = 400,
                 min_child_weight: float = 10, learning_rate: float = 0.05,
                 objective: str = "reg:squarederror", n_jobs: int = -1, seed: int = SEED):
        from xgboost import XGBRegressor
        extra = {"huber_slope": 0.5} if objective == "reg:pseudohubererror" else {}
        super().__init__(XGBRegressor(
            max_depth=max_depth, n_estimators=n_estimators, learning_rate=learning_rate,
            min_child_weight=min_child_weight, subsample=0.8, colsample_bytree=0.8,
            objective=objective, tree_method="hist", n_jobs=n_jobs,
            random_state=seed, **extra), scale=False)


class XGBSeedEnsemble:
    """Mean of five XGBoost fits that differ only in random seed (row and column
    subsampling). The like-for-like comparator for the five-seed neural ensembles.
    Added as a pre-registered control before the test set was opened."""
    family = "machine_learning"
    N = 5

    def __init__(self, **params):
        self.params = params

    def fit(self, df):
        # seed SEED + 0 is the single frozen XGBoost; the ensemble adds four more
        self.members = [XGBModel(seed=SEED + k, **self.params).fit(df) for k in range(self.N)]
        return self

    def predict(self, df):
        return np.mean([m.predict(df) for m in self.members], axis=0)


class MixedEffectsModel:
    """Linear mixed model on y - ref: fixed effects for tyre age (and its square),
    fuel proxy, track temperature, recent pace trend and spread, relative pace,
    compound and circuit; random intercept and random tyre-age slope by driver.
    Unseen drivers get the fixed part only."""
    family = "statistical"
    FIXED = ["tyre_life", "tyre_life_sq", "laps_remaining_sched", "track_temp_c",
             "trend_slope_green_5", "roll_std_green_5", "rel_pace_to_field",
             "flag_post_neutralisation"]

    def _frame(self, df, fit: bool):
        X = _design(df)
        if fit:  # drop columns with no variation in this training fold
            self.num = [c for c in self.FIXED if X[c].fillna(X[c].median()).std() > 0]
        num = self.num
        if fit:
            self.med = X[num].median()
            self.mu = X[num].fillna(self.med).mean()
            self.sd = X[num].fillna(self.med).std().replace(0, 1)
        Z = (X[num].fillna(self.med) - self.mu) / self.sd
        Z["compound"] = X["compound_relative"].to_numpy()
        Z["circuit"] = X["event_name"].to_numpy()
        Z["driver"] = df["driver"].astype(str).to_numpy()
        return Z

    def fit(self, df):
        import statsmodels.formula.api as smf
        Z = self._frame(df, fit=True)
        Z["y"] = (df["y_next_lap_time_s"] - df["ref"]).to_numpy(float)
        terms = list(self.num)
        for col in ("compound", "circuit"):
            if Z[col].nunique() > 1:
                terms.append(f"C({col})")
        self.formula = "y ~ " + (" + ".join(terms) if terms else "1")
        # Random tyre-age slope by driver; if that fit fails, random intercept only.
        # The fit actually used is recorded in self.fit_mode.
        self.fit_mode = "intercept_and_slope"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                self.res = smf.mixedlm(self.formula, Z, groups=Z["driver"],
                                       re_formula="~tyre_life").fit(method="lbfgs", reml=True)
            except (np.linalg.LinAlgError, ValueError):
                self.fit_mode = "intercept_only"
                self.res = smf.mixedlm(self.formula, Z, groups=Z["driver"]).fit(
                    method="lbfgs", reml=True)
        self.converged = bool(getattr(self.res, "converged", True))
        self.re = {k: v for k, v in self.res.random_effects.items()}
        self.levels = {"compound": set(Z["compound"]), "circuit": set(Z["circuit"])}
        return self

    def predict(self, df):
        Z = self._frame(df, fit=False)
        # unseen category levels fall back to the reference level (effect zero)
        for col in ("compound", "circuit"):
            base = sorted(self.levels[col])[0]
            Z.loc[~Z[col].isin(self.levels[col]), col] = base
        fixed = np.asarray(self.res.predict(Z), float)
        rand = np.zeros(len(Z))
        for i, (d, tl) in enumerate(zip(Z["driver"], Z["tyre_life"])):
            if d in self.re:
                r = self.re[d]
                rand[i] = r.iloc[0] + (r.iloc[1] * tl if len(r) > 1 else 0.0)
        return df["ref"].to_numpy(float) + fixed + rand


REGISTRY = {
    "persistence": Persistence,
    "compound_drift": CompoundDrift,
    "ridge": RidgeModel,
    "mixed_effects": MixedEffectsModel,
    "random_forest": RandomForestModel,
    "xgboost": XGBModel,
    "xgboost_ens5": XGBSeedEnsemble,
}

# Hyperparameter grids searched on the 2024 tuning blocks only.
# v2 (after the first development run, 2026-11-24): the v1 choices all sat on a
# grid edge (ridge alpha 1000, RF leaf 50, XGB depth 3 / 300 trees / weight 20),
# so the grids were extended past those edges, and XGBoost may also choose a
# pseudo-Huber loss because the lap-time errors are heavy-tailed. See
# docs/model_changes.md. The test set was not used for this decision.
# v3 (after run 2): XGBoost still chose depth 4 and child weight 100, both upper
# edges, so its grid moves up; pseudo-Huber loss, chosen in v2 tuning, is fixed.
GRID_VERSION = 3
GRIDS = {
    "ridge": [{"alpha": a} for a in (1.0, 10.0, 100.0, 1e3, 1e4, 1e5)],
    "random_forest": [{"min_samples_leaf": l, "max_features": f}
                      for l in (20, 50, 100, 200) for f in (0.3, 0.6, 1.0)],
    "xgboost": [{"max_depth": d, "n_estimators": n, "min_child_weight": w,
                 "objective": "reg:pseudohubererror"}
                for d in (3, 4, 5, 6) for n in (150, 300, 600) for w in (50, 100, 200, 400)],
}
# value lists per parameter, used to warn when a choice lands on an edge
GRID_AXES = {
    "ridge": {"alpha": [1.0, 10.0, 100.0, 1e3, 1e4, 1e5]},
    "random_forest": {"min_samples_leaf": [20, 50, 100, 200], "max_features": [0.3, 0.6, 1.0]},
    "xgboost": {"max_depth": [3, 4, 5, 6], "n_estimators": [150, 300, 600],
                "min_child_weight": [50, 100, 200, 400]},
}
# values that are the largest the parameter can take, so an "edge" there is not a limit
NATURAL_BOUNDS = {("random_forest", "max_features", 1.0)}


def edge_params(name: str, params: dict) -> list[str]:
    """Parameters whose chosen value is the smallest or largest tried."""
    out = []
    for k, vals in GRID_AXES.get(name, {}).items():
        if k in params and params[k] in (min(vals), max(vals)) \
                and (name, k, params[k]) not in NATURAL_BOUNDS:
            out.append(f"{k}={params[k]}")
    return out


def make_model(name: str, **params):
    return REGISTRY[name](**params)
