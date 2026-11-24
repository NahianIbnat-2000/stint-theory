"""Task 2: multi-lap stint forecasting.

At the end of lap t, forecast the driver's lap times for laps t+1 ... t+H
(H = 10), given that the driver stays out on the same tyres. A pair (t, h) is
scored when:
  * laps t+1 .. t+h are consecutive laps of the same stint,
  * none of laps t+1 .. t+h-1 is under SC, VSC or red flag, or a restart lap,
  * lap t+h is a clean green lap (target_valid of lap t+h-1).
Laps in between may be slow for other reasons (traffic, a yellow): that is part of
what a stint forecast has to cope with. Neutralisations are left out because the
strategy simulator models them separately.

Inputs are only the features of the origin lap t (leakage-checked in Task 1), plus
the horizon h, which is known in advance. Every model forecasts the same (t, h) pairs.
"""
from __future__ import annotations

import copy
import os

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder

from .deep import SEED_BASE, Tabular, _nets
from .zoo import CATEGORICAL, FLAGS, NUMERIC, SEED, _design

H = 10
NEUTRAL = ["flag_sc", "flag_vsc", "flag_red", "flag_post_neutralisation"]


def add_horizon_targets(df: pd.DataFrame, horizon: int = H) -> pd.DataFrame:
    """Adds y_h1..y_hH (lap time of lap t+h) and valid_h1..valid_hH."""
    d = df.sort_values(["race_id", "driver", "lap_number"])
    g = d.groupby(["race_id", "driver"], sort=False)
    neutral = d[NEUTRAL].astype(bool).any(axis=1)
    clean_between = pd.Series(True, index=d.index)       # laps t+1..t+h-1 not neutralised
    out = {}
    for h in range(1, horizon + 1):
        lap_h = g["lap_number"].shift(-h)
        same = (g["stint"].shift(-h) == d["stint"]) & (lap_h == d["lap_number"] + h)
        target_ok = g["target_valid"].shift(-(h - 1)).astype("boolean").fillna(False) \
            if h > 1 else d["target_valid"]
        if h > 1:
            clean_between &= ~g[NEUTRAL].shift(-(h - 1)).astype("boolean") \
                .fillna(True).any(axis=1).astype(bool)
        y = g["lt_lag0"].shift(-h)
        valid = same.fillna(False) & target_ok.astype(bool) & clean_between & y.notna()
        out[f"y_h{h}"] = y
        out[f"valid_h{h}"] = valid.astype(bool)
    res = pd.DataFrame(out, index=d.index)
    del neutral
    return df.join(res)


def origin_sample(df: pd.DataFrame, horizon: int = H) -> pd.DataFrame:
    """Origins with a reference pace and at least one scored horizon."""
    v = df[[f"valid_h{h}" for h in range(1, horizon + 1)]].any(axis=1)
    return df[v & df["ref"].notna()]


def target_matrix(df, horizon=H):
    Y = df[[f"y_h{h}" for h in range(1, horizon + 1)]].to_numpy(float)
    M = df[[f"valid_h{h}" for h in range(1, horizon + 1)]].to_numpy(bool)
    return Y, M


# ------------------------------------------------------------------ models
class Persistence:
    def fit(self, df, seq=None):
        return self

    def predict(self, df, seq=None):
        return np.repeat(df["ref"].to_numpy(float)[:, None], H, axis=1)


class CompoundDrift:
    """ref + h x (average one-lap change for the compound, from training)."""

    def fit(self, df, seq=None):
        d = df["y_h1"] - df["ref"]
        ok = df["valid_h1"]
        self.overall = float(d[ok].mean())
        self.by = d[ok].groupby(df.loc[ok, "compound_relative"]).mean().to_dict()
        return self

    def predict(self, df, seq=None):
        r = df["compound_relative"].map(self.by).astype(float).fillna(self.overall).to_numpy()
        return df["ref"].to_numpy(float)[:, None] + np.outer(r, np.arange(1, H + 1))


class TrendExtrapolation:
    """ref + h x the driver's recent pace trend (trend_slope_green_5), with the slope
    clipped to the 1st-99th percentile of training slopes."""

    def fit(self, df, seq=None):
        s = df["trend_slope_green_5"].dropna()
        self.lo, self.hi = np.percentile(s, [1, 99]) if len(s) else (0.0, 0.0)
        return self

    def predict(self, df, seq=None):
        sl = df["trend_slope_green_5"].fillna(0).clip(self.lo, self.hi).to_numpy()
        return df["ref"].to_numpy(float)[:, None] + np.outer(sl, np.arange(1, H + 1))


class XGBDirect:
    """One XGBoost model on stacked (origin, horizon) rows, horizon as an input.
    Settings carried over from the frozen Task 1 XGBoost."""

    def __init__(self, max_depth=6, n_estimators=150, min_child_weight=100,
                 learning_rate=0.05, objective="reg:pseudohubererror", n_jobs=-1, seed=SEED):
        self.params = dict(max_depth=max_depth, n_estimators=n_estimators,
                           min_child_weight=min_child_weight, learning_rate=learning_rate,
                           objective=objective, n_jobs=n_jobs, seed=seed)

    @staticmethod
    def _stack(df, hs):
        X = _design(df)
        parts = []
        for h in hs:
            Xh = X.copy()
            Xh["horizon"] = float(h)
            Xh["tyre_life_at_target"] = Xh["tyre_life"] + h
            parts.append(Xh)
        return pd.concat(parts, ignore_index=True)

    def fit(self, df, seq=None):
        from xgboost import XGBRegressor
        p = self.params
        extra = {"huber_slope": 0.5} if p["objective"] == "reg:pseudohubererror" else {}
        num = NUMERIC + FLAGS + ["tyre_life_sq", "horizon", "tyre_life_at_target"]
        prep = ColumnTransformer([
            ("num", make_pipeline(SimpleImputer(strategy="median", add_indicator=True)), num),
            ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=20,
                                  sparse_output=False), CATEGORICAL)])
        self.pipe = Pipeline([("prep", prep), ("est", XGBRegressor(
            max_depth=p["max_depth"], n_estimators=p["n_estimators"],
            learning_rate=p["learning_rate"], min_child_weight=p["min_child_weight"],
            subsample=0.8, colsample_bytree=0.8, objective=p["objective"], tree_method="hist",
            n_jobs=p["n_jobs"], random_state=p["seed"], **extra))])
        X = self._stack(df, range(1, H + 1))
        Y, M = target_matrix(df)
        r = (Y - df["ref"].to_numpy(float)[:, None]).T.reshape(-1)   # horizon-major
        keep = M.T.reshape(-1)
        self.pipe.fit(X[keep], r[keep])
        return self

    def predict(self, df, seq=None):
        X = self._stack(df, range(1, H + 1))
        r = self.pipe.predict(X).reshape(H, len(df)).T
        return df["ref"].to_numpy(float)[:, None] + r


class MultiHorizonNet:
    """MLP or LSTM with H outputs, trained with a masked Huber loss (only scored
    horizons count). Same inputs, early stopping and settings as Task 1."""

    def __init__(self, arch, hidden=64, dropout=0.3, lr=1e-3, weight_decay=1e-4,
                 max_epochs=40, patience=5, batch_size=256, val_races=3, seed=0):
        self.arch, self.hidden, self.dropout = arch, hidden, dropout
        self.lr, self.wd, self.max_epochs, self.patience = lr, weight_decay, max_epochs, patience
        self.bs, self.val_races, self.seed = batch_size, val_races, seed

    def fit(self, df, seq):
        import torch
        torch.manual_seed(SEED_BASE + self.seed)
        np.random.seed(SEED_BASE + self.seed)
        torch.set_num_threads(max(1, os.cpu_count() or 1))
        Y, M = target_matrix(df)
        R = np.nan_to_num(Y - df["ref"].to_numpy(float)[:, None]).astype(np.float32)
        orders = np.sort(df["race_order"].unique())
        cut = orders[-self.val_races] if len(orders) > self.val_races else orders[-1] + 1
        is_val = (df["race_order"] >= cut).to_numpy()
        self.tab = Tabular().fit(df[~is_val])
        tab = torch.from_numpy(self.tab.transform(df))
        s = torch.from_numpy(seq)
        y, m = torch.from_numpy(R), torch.from_numpy(M.astype(np.float32))
        tr = torch.from_numpy(np.where(~is_val)[0])
        va = torch.from_numpy(np.where(is_val)[0])
        self.net = _nets()[self.arch](d_tab=tab.shape[1], d_seq=seq.shape[2], hidden=self.hidden,
                                      dropout=self.dropout, n_out=H)
        opt = torch.optim.AdamW(self.net.parameters(), lr=self.lr, weight_decay=self.wd)
        huber = torch.nn.HuberLoss(delta=0.5, reduction="none")
        gen = torch.Generator().manual_seed(SEED_BASE + self.seed)
        best, best_state, bad, self.history = np.inf, None, 0, []
        for _ in range(self.max_epochs):
            self.net.train()
            perm = tr[torch.randperm(len(tr), generator=gen)]
            for i in range(0, len(perm), self.bs):
                b = perm[i:i + self.bs]
                opt.zero_grad()
                l = (huber(self.net(tab[b], s[b]), y[b]) * m[b]).sum() / m[b].sum().clamp(min=1)
                l.backward()
                opt.step()
            if len(va) == 0:
                best_state = copy.deepcopy(self.net.state_dict())
                continue
            self.net.eval()
            with torch.no_grad():
                e = ((self.net(tab[va], s[va]) - y[va]).abs() * m[va]).sum() / m[va].sum()
            v = float(e)
            self.history.append(v)
            if v < best - 1e-4:
                best, best_state, bad = v, copy.deepcopy(self.net.state_dict()), 0
            else:
                bad += 1
                if bad >= self.patience:
                    break
        self.net.load_state_dict(best_state)
        self.epochs_run = len(self.history)
        return self

    def predict(self, df, seq):
        import torch
        self.net.eval()
        with torch.no_grad():
            r = self.net(torch.from_numpy(self.tab.transform(df)), torch.from_numpy(seq)).numpy()
        return df["ref"].to_numpy(float)[:, None] + r.astype(float)


SIMPLE = {"persistence": Persistence, "compound_drift": CompoundDrift,
          "trend_extrapolation": TrendExtrapolation, "xgboost_direct": XGBDirect}
NEURAL = ["mlp", "lstm"]
MODELS = list(SIMPLE) + [f"{a}_multi" for a in NEURAL]
