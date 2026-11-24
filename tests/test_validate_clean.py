import numpy as np
import pandas as pd

from fixtures import SC_LAPS, make_raw_race
from pipelines.clean import clean_session, map_compounds, parse_track_status
from pipelines.validate import validate_session


def _checks(rep, severity):
    return {i["check"] for i in rep["issues"] if i["severity"] == severity}


def test_fixture_passes_validation():
    rep = validate_session(make_raw_race())
    assert rep["passed"], _checks(rep, "error")


def test_duplicate_driver_lap_is_an_error():
    raw = make_raw_race()
    raw["laps"] = pd.concat([raw["laps"], raw["laps"].iloc[[5]]], ignore_index=True)
    rep = validate_session(raw)
    assert not rep["passed"]
    assert "duplicate_driver_lap" in _checks(rep, "error")


def test_more_laps_than_scheduled_is_flagged_not_fatal():
    raw = make_raw_race()
    raw["meta"]["scheduled_laps"] = 29
    rep = validate_session(raw)
    assert rep["passed"] and "laps_exceed_scheduled" in _checks(rep, "warning")
    c = clean_session(raw)
    assert c.loc[c.lap_number == 30, "flag_beyond_scheduled"].all()
    assert not c.loc[c.lap_number == 30, "is_clean_green"].any()
    assert not c.loc[c.lap_number < 30, "flag_beyond_scheduled"].any()


def test_tyre_life_jump_is_reported():
    raw = make_raw_race()
    raw["laps"].loc[3, "TyreLife"] += 5
    assert "tyre_life_step_not_one" in _checks(validate_session(raw), "warning")


def test_cleaning_never_drops_rows():
    raw = make_raw_race()
    assert len(clean_session(raw)) == len(raw["laps"])


def test_pit_and_neutralisation_flags():
    c = clean_session(make_raw_race())
    d0 = c[c.driver == "D00"].set_index("lap_number")
    assert d0.loc[10, "flag_pit_in"] and d0.loc[11, "flag_pit_out"]
    assert d0.loc[1, "flag_first_lap"]
    assert all(d0.loc[list(SC_LAPS), "flag_sc"])
    assert d0.loc[SC_LAPS[-1] + 1, "flag_post_neutralisation"]
    assert not d0.loc[SC_LAPS[0], "flag_post_neutralisation"]  # SC lap itself is flagged as SC
    for lap in (1, 10, 11, *SC_LAPS, SC_LAPS[-1] + 1):
        assert not d0.loc[lap, "is_clean_green"]
    assert d0.loc[5, "is_clean_green"]


def test_track_status_string_parsing():
    f = parse_track_status(pd.Series(["1", "41", "6", "671", "2", None]))
    assert f["flag_sc"].tolist() == [False, True, False, False, False, False]
    assert f["flag_vsc"].tolist() == [False, False, True, True, False, False]
    assert f["flag_track_status_missing"].iloc[-1]


def test_compound_mapping_2018_named():
    s = pd.Series(["ULTRASOFT", "SUPERSOFT", "SOFT", "ULTRASOFT", "INTERMEDIATE"])
    m = map_compounds(2018, s)
    assert m["compound_relative"].tolist() == ["SOFT", "MEDIUM", "HARD", "SOFT", "INTERMEDIATE"]


def test_compound_mapping_2018_ambiguous_left_missing():
    m = map_compounds(2018, pd.Series(["ULTRASOFT", "SUPERSOFT"]))
    assert m["compound_relative"].isna().all()
    assert m["compound_map_method"].str.startswith("ambiguous").all()


def test_weather_uses_only_samples_at_or_before_lap_start():
    raw = make_raw_race()
    c = clean_session(raw)
    w = raw["weather"].assign(t=raw["weather"]["Time"].dt.total_seconds())
    for _, r in c.sample(20, random_state=1).iterrows():
        prior = w[w.t <= r.lap_start_session_s]
        assert np.isclose(r.track_temp_c, prior.iloc[-1].TrackTemp)
        assert r.weather_age_s >= 0


def test_final_results_not_joined():
    c = clean_session(make_raw_race())
    assert "grid_position" in c.columns
    assert not {"Position", "final_position", "ClassifiedPosition"} & set(c.columns)


def test_outlier_flag_flags_but_keeps_row():
    raw = make_raw_race()
    idx = raw["laps"].index[(raw["laps"].Driver == "D01") & (raw["laps"].LapNumber == 22)][0]
    raw["laps"].loc[idx, "LapTime"] += pd.Timedelta(seconds=30)
    c = clean_session(raw)
    row = c[(c.driver == "D01") & (c.lap_number == 22)].iloc[0]
    assert row.flag_pace_outlier and not row.is_clean_green_strict
    assert row.is_clean_green  # outliers stay in the default sample


def test_outlier_flag_ignores_steady_tyre_wear_trend():
    """A stint that slows 0.15 s/lap with small noise: late, worn-tyre laps are not
    flagged and flags stay rare overall."""
    raw = make_raw_race(n_laps=50)
    L = raw["laps"]
    rng = np.random.default_rng(3)
    for d in L.Driver.unique():
        m = (L.Driver == d) & (L.Stint == 2)
        tl = L.loc[m, "TyreLife"].to_numpy()
        L.loc[m, "LapTime"] = pd.to_timedelta(88 + 0.15 * tl + rng.normal(0, 0.1, m.sum()), unit="s")
    c = clean_session(raw)
    late = c[(c.stint == 2) & ~c.flag_sc & ~c.flag_pit_out & ~c.flag_post_neutralisation]
    assert late.loc[late.tyre_life > 25, "flag_pace_outlier"].sum() == 0
    assert late["flag_pace_outlier"].mean() < 0.02


def test_lap_completeness_excludes_half_missing_race():
    from pipelines.validate import lap_completeness
    raw = make_raw_race()
    raw["results"]["Laps"] = 30
    assert lap_completeness(raw["laps"], raw["results"]) == 1.0
    assert validate_session(raw)["passed"]
    raw["laps"] = raw["laps"][raw["laps"].LapNumber <= 15]   # like Miami 2025
    rep = validate_session(raw)
    assert rep["lap_completeness"] == 0.5 and not rep["passed"]
    assert "lap_completeness" in _checks(rep, "error")
