"""Phase 2 model code on synthetic races. TEST DATA ONLY: no number here is a result."""
import json

import numpy as np
import pandas as pd
import pytest

from fixtures import make_raw_race
from models import data, evaluate, zoo
from pipelines.clean import clean_session
from pipelines.features import build_features

RACES = [(2023, 1), (2023, 2), (2024, 1), (2024, 7), (2024, 13), (2024, 19),
         (2025, 1), (2025, 2), (2025, 13)]


@pytest.fixture(scope="module")
def feat_path(tmp_path_factory):
    frames = []
    for i, (s, r) in enumerate(RACES):
        raw = make_raw_race(s, r, n_drivers=6, n_laps=30, seed=i)
        raw["meta"]["event_name"] = f"Circuit {i % 3}"
        frames.append(clean_session(raw))
    f = build_features(pd.concat(frames, ignore_index=True))
    p = tmp_path_factory.mktemp("feat") / "features.parquet"
    f.to_parquet(p, index=False)
    return p


def test_split_assignment():
    s = data.assign_split(pd.Series([2023, 2024, 2025, 2025, 2025]), pd.Series([5, 24, 1, 12, 13]))
    assert s.tolist() == ["train", "train", "dev", "dev", "test"]


def test_test_set_is_dropped_and_locked(feat_path, tmp_path, monkeypatch):
    df = data.load_features(feat_path)
    assert not (df["split"] == "test").any()
    assert (df["split"] == "dev").any()
    monkeypatch.delenv(data.UNLOCK_ENV, raising=False)
    with pytest.raises(data.TestSetLocked):
        data.load_features(feat_path, include_test=True, log=tmp_path / "log")
    monkeypatch.setenv(data.UNLOCK_ENV, data.UNLOCK_VALUE)
    full = data.load_features(feat_path, include_test=True, reason="unit test", log=tmp_path / "log")
    assert (full["split"] == "test").any()
    assert "unit test" in (tmp_path / "log").read_text()


def test_rolling_folds_never_look_ahead(feat_path):
    s = data.scored_sample(data.load_features(feat_path))
    folds = list(data.rolling_folds(s, s["split"] == "dev"))
    assert len(folds) == 2
    for tr, ev, _ in folds:
        assert s.loc[tr, "race_order"].max() < s.loc[ev, "race_order"].min()
        assert s.loc[ev, "race_id"].nunique() == 1


def test_tuning_uses_only_training_seasons(feat_path):
    s = data.scored_sample(data.load_features(feat_path))
    blocks = list(data.tuning_blocks(s))
    assert blocks
    for tr, va, _ in blocks:
        assert (s.loc[tr, "split"] == "train").all() and (s.loc[va, "season"] == 2024).all()
        assert s.loc[tr, "race_order"].max() < s.loc[va, "race_order"].min()


def test_persistence_is_the_reference(feat_path):
    s = data.scored_sample(data.load_features(feat_path))
    p = zoo.make_model("persistence").fit(s).predict(s)
    np.testing.assert_allclose(p, s["last_green_lt"].fillna(s["field_green_median_recent"]))


@pytest.mark.parametrize("name", list(zoo.REGISTRY))
def test_every_model_fits_predicts_and_is_deterministic(feat_path, name):
    s = data.scored_sample(data.load_features(feat_path))
    tr, ev = s[s.split == "train"], s[s.split == "dev"]
    params = zoo.GRIDS.get(name, [{}])[0]
    if name == "random_forest":
        params = {**params, "n_estimators": 20}
    p1 = zoo.make_model(name, **params).fit(tr).predict(ev)
    p2 = zoo.make_model(name, **params).fit(tr).predict(ev)
    assert p1.shape == (len(ev),) and np.isfinite(p1).all()
    np.testing.assert_allclose(p1, p2)


def test_preprocessing_learned_from_training_only(feat_path):
    """Changing evaluation rows must not change what the model learned."""
    s = data.scored_sample(data.load_features(feat_path))
    tr, ev = s[s.split == "train"], s[s.split == "dev"].copy()
    m = zoo.make_model("ridge", alpha=1.0).fit(tr)
    before = m.predict(ev.iloc[:5])
    ev.loc[ev.index[5:], "track_temp_c"] = 500.0   # absurd values in other eval rows
    np.testing.assert_allclose(m.predict(ev.iloc[:5]), before)


def test_point_metrics():
    m = evaluate.point_metrics(np.array([1.0, 2.0, 3.0]), np.array([1.0, 3.0, 1.0]))
    assert m["mae"] == pytest.approx(1.0) and m["rmse"] == pytest.approx(np.sqrt(5 / 3))
    assert m["bias"] == pytest.approx(-1 / 3) and m["median_ae"] == 1.0


def test_bootstrap_is_race_clustered_and_reproducible():
    rng = np.random.default_rng(0)
    rows = []
    for r in range(15):
        shift = rng.normal(0, 1)
        for _ in range(40):
            y = rng.normal()
            rows.append({"race_id": f"r{r}", "y": y, "pred_a": y + shift + rng.normal(0, .1),
                         "pred_b": y + rng.normal(0, .5)})
    pred = pd.DataFrame(rows)
    b1 = evaluate.bootstrap(pred, ["a", "b"], "a", b=300, seed=1)
    b2 = evaluate.bootstrap(pred, ["a", "b"], "a", b=300, seed=1)
    assert b1 == b2 and b1["races"] == 15
    lo, hi = b1["models"]["a"]["mae_ci"]
    assert lo < np.abs(pred.pred_a - pred.y).mean() < hi
    assert b1["models"]["a"]["skill_vs_ref_ci"] == [0.0, 0.0]


def test_quick_dev_run_end_to_end(feat_path, tmp_path):
    from models.run import MODELS, run_dev
    report = run_dev(feat_path, out=tmp_path, quick=True, boot_b=100)
    text = report.read_text()
    assert "development results, not final test results" in text
    m = json.loads((tmp_path / "metrics.json").read_text())
    assert {r["model"] for r in m["summary"]} == set(MODELS)
    assert len({r["n"] for r in m["summary"]}) == 1          # same laps for every model
    pred = pd.read_parquet(tmp_path / "predictions.parquet")
    assert set(pred["season"]) == {2025} and pred["round"].max() <= 12


def test_grid_edge_detection():
    assert zoo.edge_params("ridge", {"alpha": 1e5}) == ["alpha=100000.0"]
    assert zoo.edge_params("xgboost", {"max_depth": 4, "n_estimators": 300,
                                       "min_child_weight": 100}) == []
    assert zoo.edge_params("random_forest", {"min_samples_leaf": 50, "max_features": 1.0}) == []


def test_xgboost_pseudo_huber_runs(feat_path):
    s = data.scored_sample(data.load_features(feat_path))
    m = zoo.make_model("xgboost", max_depth=2, n_estimators=50, min_child_weight=20,
                       objective="reg:pseudohubererror").fit(s[s.split == "train"])
    assert np.isfinite(m.predict(s[s.split == "dev"])).all()


# ------------------------------------------------------------------ Phase 3
def test_sequences_use_only_laps_up_to_origin(feat_path):
    from models.deep import build_sequences
    df = data.load_features(feat_path)
    seq = build_sequences(df)
    i = df.index[(df.driver == "D01") & (df.lap_number == 16) & (df.race_id == "2024_07")][0]
    pert = df.copy()
    fut = (pert.race_id == "2024_07") & (pert.lap_number > 16)
    pert.loc[fut, "lt_lag0"] += 50
    pert.loc[fut, ["flag_sc", "is_rt_green"]] = [True, False]
    np.testing.assert_array_equal(build_sequences(pert)[i], seq[i])
    # last step is lap t itself; earlier steps are earlier laps of the same driver
    lt = df.loc[i, "lt_lag0"]
    assert seq[i, -1, 0] == pytest.approx(np.clip((lt - df.loc[i, "ref"]) / 5, -3, 6), abs=1e-5)
    assert seq[i, :, -1].sum() == 10                      # 10 real laps, no padding
    first = df.index[(df.driver == "D01") & (df.lap_number == 1) & (df.race_id == "2024_07")][0]
    assert seq[first, :, -1].sum() == 1                   # lap 1: only itself


@pytest.mark.parametrize("arch", ["mlp", "lstm", "tcn"])
def test_neural_models_fit_and_are_seed_deterministic(feat_path, arch):
    from models.deep import NeuralModel, build_sequences
    df = data.load_features(feat_path)
    seq = build_sequences(df)
    s = data.scored_sample(df)
    tr, ev = s.index[s.split == "train"], s.index[s.split == "dev"]
    kw = dict(hidden=16, max_epochs=3, seed=1)
    p1 = NeuralModel(arch, **kw).fit(s.loc[tr], seq[tr]).predict(s.loc[ev], seq[ev])
    p2 = NeuralModel(arch, **kw).fit(s.loc[tr], seq[tr]).predict(s.loc[ev], seq[ev])
    assert np.isfinite(p1).all()
    np.testing.assert_allclose(p1, p2, atol=1e-5)


def test_tcn_sees_the_whole_window():
    """The TCN output (taken at lap t) responds to lap t and to the oldest lap in the
    window: the dilations cover all SEQ_LEN steps. Inputs never include laps after t."""
    import torch
    from models.deep import _nets
    torch.manual_seed(0)
    net = _nets()["tcn"](d_tab=4, d_seq=15, hidden=8, dropout=0.0).eval()
    tab, seq = torch.zeros(1, 4), torch.randn(1, 10, 15)
    base = net(tab, seq).item()
    seq2 = seq.clone(); seq2[0, -1, 0] += 5
    assert net(tab, seq2).item() != pytest.approx(base)
    # receptive field covers the oldest step
    seq3 = seq.clone(); seq3[0, 0, 0] += 5
    assert net(tab, seq3).item() != pytest.approx(base)


def test_quick_deep_run_end_to_end(feat_path, tmp_path):
    from models.run import run_dev
    from models.deep_run import run_deep
    run_dev(feat_path, out=tmp_path / "p2", quick=True, boot_b=50)
    report = run_deep(feat_path, p2_pred_path=tmp_path / "p2" / "predictions.parquet",
                      out=tmp_path / "p3", quick=True, boot_b=50)
    text = report.read_text()
    for m in ("mlp", "lstm", "tcn", "xgboost", "persistence"):
        assert f"| {m} |" in text
    assert "temporal-history ablation" in text


def test_holm_and_decision_rules():
    adj = evaluate.holm({"a": 0.01, "b": 0.04, "c": 0.03})
    assert adj == {"a": 0.03, "c": 0.06, "b": 0.06}
    rng = np.random.default_rng(0)
    assert evaluate.classify(-0.05, rng.normal(-0.05, 0.005, 4000), 0.001, 0.01) == "meaningful difference"
    assert evaluate.classify(0.0, rng.normal(0, 0.002, 4000), 0.9, 0.01) == "equivalent"
    assert evaluate.classify(-0.004, rng.normal(-0.004, 0.0015, 4000), 0.01, 0.01) == \
        "equivalent (statistically different, within margin)"
    assert evaluate.classify(0.0, rng.normal(0, 0.03, 4000), 0.9, 0.01) == "inconclusive"
    assert evaluate.bootstrap_p(np.array([-1.0, -2.0, 1.0, -3.0])) == 0.5


def test_final_test_needs_unlock_and_runs_end_to_end(feat_path, tmp_path, monkeypatch):
    from models.run import run_dev
    from models.deep_run import run_deep
    from models import final_test
    run_dev(feat_path, out=tmp_path / "p2", quick=True, boot_b=50)
    run_deep(feat_path, p2_pred_path=tmp_path / "p2" / "predictions.parquet",
             out=tmp_path / "p3", quick=True, boot_b=50)
    kw = dict(features_path=feat_path, out=tmp_path / "final", quick=True,
              allow_uncommitted=True, p2_tuning=tmp_path / "p2" / "tuning.json",
              p3_tuning=tmp_path / "p3" / "tuning.json", boot_b=100,
              access_log=tmp_path / "access.log")
    monkeypatch.delenv(data.UNLOCK_ENV, raising=False)
    with pytest.raises(data.TestSetLocked):
        final_test.run_test(**kw)
    monkeypatch.setenv(data.UNLOCK_ENV, data.UNLOCK_VALUE)
    report = final_test.run_test(**kw).read_text()
    assert "P5" in report and "xgboost_ens5" in report and "NOT committed" in report
    pred = pd.read_parquet(tmp_path / "final" / "predictions.parquet")
    assert set(pred["round"]) == {13}
    with pytest.raises(RuntimeError, match="run once"):
        final_test.run_test(**kw)           # second run refused
    assert "final test run" in (tmp_path / "access.log").read_text()
