"""Features at origin (driver, lap t) must not change when the future changes."""
import numpy as np
import pandas as pd
import pytest

from fixtures import make_raw_race
from pipelines.clean import clean_session
from pipelines.features import FEATURE_COLUMNS, build_features

from pipelines.features import SEQUENCE_COLUMNS

COLS = [c for c in FEATURE_COLUMNS if c != "lap_number"] + SEQUENCE_COLUMNS


def _features(raw):
    return build_features(clean_session(raw)).set_index(["driver", "lap_number"])


def _perturb_future(raw, driver, lap, seed=99):
    """Change every lap that ends after the origin lap ends, for all drivers."""
    rng = np.random.default_rng(seed)
    laps = raw["laps"].copy()
    origin_end = laps.loc[(laps.Driver == driver) & (laps.LapNumber == lap), "Time"].iloc[0]
    future = laps["Time"] > origin_end
    laps.loc[future, "LapTime"] = laps.loc[future, "LapTime"] + pd.to_timedelta(
        rng.normal(0, 3, future.sum()), unit="s")
    laps.loc[future, "TrackStatus"] = rng.choice(["1", "2", "4", "6"], future.sum())
    laps.loc[future, "Deleted"] = True
    laps.loc[future, "IsAccurate"] = False
    out = dict(raw)
    out["laps"] = laps
    w = raw["weather"].copy()
    w.loc[w["Time"] > origin_end, ["TrackTemp", "AirTemp"]] += 15
    out["weather"] = w
    return out


@pytest.mark.parametrize("driver,lap", [("D00", 6), ("D01", 16), ("D02", 20), ("D03", 25)])
def test_future_changes_do_not_move_features(driver, lap):
    raw = make_raw_race()
    base = _features(raw).loc[(driver, lap), COLS]
    pert = _features(_perturb_future(raw, driver, lap)).loc[(driver, lap), COLS]
    pd.testing.assert_series_equal(base, pert, check_names=False)


def test_target_is_next_lap_and_changes_with_future():
    raw = make_raw_race()
    f = _features(raw)
    nxt = clean_session(raw).set_index(["driver", "lap_number"]).loc[("D00", 7), "lap_time_s"]
    assert np.isclose(f.loc[("D00", 6), "y_next_lap_time_s"], nxt)


def test_target_invalid_across_pit_stop_and_sc():
    f = _features(make_raw_race())
    assert not f.loc[("D00", 9), "target_valid"]   # lap 10 is the in-lap
    assert not f.loc[("D00", 10), "target_valid"]  # next lap is a new stint
    assert not f.loc[("D00", 11), "target_valid"]  # lap 12 is under SC
    assert f.loc[("D00", 6), "target_valid"]


def test_rolling_features_exclude_current_and_future_flagged_laps():
    raw = make_raw_race()
    f = _features(raw)
    c = clean_session(raw).set_index(["driver", "lap_number"])
    # on lap 8 for D00 the last three green laps are 6, 7, 8
    exp = c.loc[[("D00", 6), ("D00", 7), ("D00", 8)], "lap_time_s"].mean()
    assert np.isclose(f.loc[("D00", 8), "roll_mean_green_3"], exp)
    # D00 stint 2 starts on lap 11 (out-lap); laps 12-13 are SC and 14 is post-SC,
    # so no green lap exists yet in the stint on lap 14, and lap 15 is the first.
    assert np.isnan(f.loc[("D00", 14), "last_green_lt"])
    assert np.isclose(f.loc[("D00", 15), "last_green_lt"], c.loc[("D00", 15), "lap_time_s"])


def test_perturbation_reaches_the_target():
    """Guard against a vacuous leakage test: the future change must move the target."""
    raw = make_raw_race()
    base = _features(raw).loc[("D01", 16), "y_next_lap_time_s"]
    pert = _features(_perturb_future(raw, "D01", 16)).loc[("D01", 16), "y_next_lap_time_s"]
    assert not np.isclose(base, pert)


def test_leakage_test_catches_a_deliberate_leak(monkeypatch):
    """Mutation check: a feature built from lap t+1 must make the leakage test fail."""
    import pipelines.features as F
    orig = F.build_race_features

    def leaky(race):
        out = orig(race)
        out["lt_lag1"] = out.groupby("driver")["lap_time_s"].shift(-1)  # future value
        return out

    monkeypatch.setattr(F, "build_race_features", leaky)
    with pytest.raises(AssertionError):
        test_future_changes_do_not_move_features("D01", 16)
