"""Task 2 code on synthetic races. TEST DATA ONLY."""
import numpy as np
import pandas as pd
import pytest

from fixtures import make_raw_race
from models import data
from models.horizon import H, add_horizon_targets, origin_sample
from pipelines.clean import clean_session
from pipelines.features import build_features

RACES = [(2023, 1), (2023, 2), (2024, 1), (2024, 7), (2024, 13), (2024, 19), (2025, 1), (2025, 2)]


@pytest.fixture(scope="module")
def feat_path(tmp_path_factory):
    frames = []
    for i, (s, r) in enumerate(RACES):
        raw = make_raw_race(s, r, n_drivers=6, n_laps=40, seed=i)
        raw["meta"]["event_name"] = f"Circuit {i % 3}"
        frames.append(clean_session(raw))
    p = tmp_path_factory.mktemp("h") / "f.parquet"
    build_features(pd.concat(frames, ignore_index=True)).to_parquet(p, index=False)
    return p


def test_horizon_targets(feat_path):
    df = add_horizon_targets(data.load_features(feat_path))
    d = df[(df.race_id == "2023_01") & (df.driver == "D03")].set_index("lap_number")
    # D03 pits on lap 19 (in-lap), SC on laps 12-13, restart lap 14
    assert d.loc[3, "y_h4"] == pytest.approx(d.loc[7, "lt_lag0"])
    assert d.loc[3, "valid_h5"]                       # laps 4-8, all green, same stint
    assert not d.loc[9, "valid_h3"]                   # lap 12 is SC (the target)
    assert not d.loc[10, "valid_h5"]                  # laps 12-13 SC in between
    assert not d.loc[16, "valid_h4"]                  # crosses the pit stop
    assert d.loc[16, "valid_h2"]                      # lap 18, before the in-lap


def test_horizon_targets_ignore_the_future_of_features(feat_path):
    """Adding targets must not change any feature column."""
    base = data.load_features(feat_path)
    df = add_horizon_targets(base)
    pd.testing.assert_frame_equal(df[base.columns], base)


@pytest.mark.parametrize("name", ["persistence", "compound_drift", "trend_extrapolation",
                                  "xgboost_direct"])
def test_simple_models_shape(feat_path, name):
    from models.horizon import SIMPLE
    df = add_horizon_targets(data.load_features(feat_path))
    o = origin_sample(df)
    tr, ev = o[o.split == "train"], o[o.split == "dev"]
    kw = {"n_estimators": 20} if name == "xgboost_direct" else {}
    P = SIMPLE[name](**kw).fit(tr).predict(ev)
    assert P.shape == (len(ev), H) and np.isfinite(P).all()
    if name == "persistence":
        assert (P == ev["ref"].to_numpy()[:, None]).all()


def test_multi_horizon_net_masks_and_is_deterministic(feat_path):
    from models.deep import build_sequences
    from models.horizon import MultiHorizonNet
    full = add_horizon_targets(data.load_features(feat_path))
    seq = build_sequences(full)
    o = origin_sample(full)
    tr, ev = o.index[o.split == "train"], o.index[o.split == "dev"]
    kw = dict(hidden=16, max_epochs=3, seed=2)
    p1 = MultiHorizonNet("lstm", **kw).fit(o.loc[tr], seq[tr]).predict(o.loc[ev], seq[ev])
    p2 = MultiHorizonNet("lstm", **kw).fit(o.loc[tr], seq[tr]).predict(o.loc[ev], seq[ev])
    assert p1.shape == (len(ev), H)
    np.testing.assert_allclose(p1, p2, atol=1e-5)


def test_quick_horizon_run(feat_path, tmp_path):
    from models.run import run_dev
    from models.deep_run import run_deep
    from models.horizon_run import run_horizon_dev
    run_dev(feat_path, out=tmp_path / "p2", quick=True, boot_b=50)
    run_deep(feat_path, p2_pred_path=tmp_path / "p2" / "predictions.parquet",
             out=tmp_path / "p3", quick=True, boot_b=50)
    rep = run_horizon_dev(feat_path, out=tmp_path / "t2", quick=True,
                          p2=tmp_path / "p2" / "tuning.json", p3=tmp_path / "p3" / "tuning.json")
    text = rep.read_text()
    assert "MAE by horizon" in text and "xgboost_direct" in text and "lstm_multi" in text
