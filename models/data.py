"""Sample splits and the locked test set.

Split (fixed before any model was fitted; see docs/methodology_models.md):
  train : seasons 2023 and 2024
  dev   : 2025 rounds 1-12  (rolling-origin evaluation, one race at a time)
  test  : 2025 rounds 13-24 (LOCKED until every model, deep learning included, is final)

The test rows are dropped at load time unless the lock is opened on purpose:
    STINT_UNLOCK_TEST=I_HAVE_FROZEN_ALL_MODELS python -m models test
Every opening is appended to data/reports/test_access.log.
"""
from __future__ import annotations

import datetime as dt
import os
from pathlib import Path

import numpy as np
import pandas as pd

from pipelines import config

TRAIN_SEASONS = (2023, 2024)
DEV = (2025, range(1, 13))
TEST = (2025, range(13, 25))
UNLOCK_ENV = "STINT_UNLOCK_TEST"
UNLOCK_VALUE = "I_HAVE_FROZEN_ALL_MODELS"
TEST_LOG = config.REPORTS / "test_access.log"
FEATURES_PATH = config.PROCESSED / "features_next_lap.parquet"


class TestSetLocked(RuntimeError):
    pass


def assign_split(season: pd.Series, rnd: pd.Series) -> pd.Series:
    s = pd.Series("unused", index=season.index, dtype="object")
    s[season.isin(TRAIN_SEASONS)] = "train"
    s[(season == DEV[0]) & rnd.isin(list(DEV[1]))] = "dev"
    s[(season == TEST[0]) & rnd.isin(list(TEST[1]))] = "test"
    return s


def test_unlocked() -> bool:
    return os.environ.get(UNLOCK_ENV) == UNLOCK_VALUE


def _log_test_access(reason: str, log: Path) -> None:
    log.parent.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    with open(log, "a") as fh:
        fh.write(f"{stamp}\t{reason}\n")


def reference_pace(df: pd.DataFrame) -> pd.Series:
    """Naive forecast every model is measured against: the last real-time-green lap
    of the stint, or the recent field median when the stint has none yet."""
    return df["last_green_lt"].fillna(df["field_green_median_recent"])


def load_features(path: Path | None = None, *, include_test: bool = False,
                  reason: str = "", log: Path | None = None) -> pd.DataFrame:
    """Feature rows with `split`, `race_order` and `ref` added. Test rows are removed
    unless include_test=True and the lock is open (which is logged)."""
    df = pd.read_parquet(path or FEATURES_PATH)
    df["split"] = assign_split(df["season"], df["round"])
    if include_test:
        if not test_unlocked():
            raise TestSetLocked(
                f"The 2025 R13-24 test set is locked. Set {UNLOCK_ENV}={UNLOCK_VALUE} only "
                "after every model (including Phase 3) is frozen.")
        _log_test_access(reason or "unspecified", log or TEST_LOG)
    else:
        df = df[df["split"] != "test"]
    races = df[["season", "round"]].drop_duplicates().sort_values(["season", "round"])
    races["race_order"] = np.arange(len(races))
    df = df.merge(races, on=["season", "round"], how="left")
    df["ref"] = reference_pace(df)
    return df.reset_index(drop=True)


def scored_sample(df: pd.DataFrame, strict: bool = False) -> pd.DataFrame:
    """Rows every model is fitted and scored on: valid next-lap target and a reference."""
    flag = "target_valid_strict" if strict else "target_valid"
    return df[df[flag] & df["ref"].notna() & df["y_next_lap_time_s"].notna()]


def rolling_folds(df: pd.DataFrame, eval_mask: pd.Series):
    """Rolling origin: for each evaluation race (in date order), train on every
    scored race strictly before it. Yields (train_index, eval_index, race_id)."""
    order = df["race_order"]
    for ro in sorted(order[eval_mask].unique()):
        ev = df.index[eval_mask & (order == ro)]
        tr = df.index[order < ro]
        yield tr, ev, df.loc[ev[0], "race_id"]


def tuning_blocks(df: pd.DataFrame):
    """Inner folds for choosing hyperparameters, inside the training seasons only:
    2024 split into four blocks of rounds; each block is predicted from everything
    before it. 2025 is never used for tuning."""
    for lo, hi in ((1, 6), (7, 12), (13, 18), (19, 24)):
        val = (df["season"] == 2024) & df["round"].between(lo, hi)
        if not val.any():
            continue
        first = df.loc[val, "race_order"].min()
        tr = df.index[(df["split"] == "train") & (df["race_order"] < first)]
        yield tr, df.index[val], f"2024 R{lo}-{hi}"
