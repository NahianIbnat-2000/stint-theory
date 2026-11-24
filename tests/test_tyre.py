"""Task 3 estimator: exactness against dummy-variable OLS, and recovery of a known
tyre-age effect from simulated races with fuel burn. SIMULATED DATA ONLY."""
import numpy as np
import pandas as pd
import pytest

from models.tyre import COMPOUNDS, estimation_sample, fe_ols, slopes

TRUE = {"SOFT": 0.10, "MEDIUM": 0.06, "HARD": 0.03}
FUEL = -0.06


def simulate(n_races=12, n_drivers=16, n_laps=50, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for r in range(n_races):
        lap_shock = rng.normal(0, 0.3, n_laps + 1)          # track / weather, common
        comp_offset = {c: rng.normal(0, 0.5) for c in COMPOUNDS}   # race-specific
        for d in range(n_drivers):
            pace = rng.normal(0, 0.5)
            stop = int(rng.integers(12, 38))                 # staggered pit stops
            comps = rng.choice(COMPOUNDS, 2, replace=False)
            for lap in range(1, n_laps + 1):
                stint = 1 if lap <= stop else 2
                age = lap if stint == 1 else lap - stop
                c = comps[stint - 1]
                t = (90 + pace + comp_offset[c] + FUEL * lap + lap_shock[lap] + TRUE[c] * age
                     + rng.normal(0, 0.15))
                rows.append({"race_id": f"R{r:02d}", "season": 2023 + r % 3,
                             "event_name": f"C{r % 4}", "driver": f"D{d:02d}", "stint": stint,
                             "lap_number": lap, "tyre_life": float(age), "compound_relative": c,
                             "lap_time_s": t, "is_clean_green": True,
                             "is_clean_green_strict": True})
    return pd.DataFrame(rows)


def test_fe_ols_matches_dummy_regression():
    import statsmodels.formula.api as smf
    d = estimation_sample(simulate(n_races=3, n_drivers=6, n_laps=20, seed=1))
    ours = fe_ols(d, "lap_time_s", ["age_SOFT", "age_MEDIUM", "age_HARD"],
                  ["race_lap", "driver_race", "race_compound"], "race_id")
    sm = smf.ols("lap_time_s ~ age_SOFT + age_MEDIUM + age_HARD + C(race_lap) + C(driver_race)"
                 " + C(race_compound)", d).fit()
    for k in ours["coef"].index:
        assert ours["coef"][k] == pytest.approx(sm.params[k], abs=1e-7)


def test_recovers_known_tyre_effect_and_naive_is_biased():
    d = estimation_sample(simulate())
    main = slopes(fe_ols(d, "lap_time_s", [f"age_{c}" for c in COMPOUNDS],
                         ["race_lap", "driver_race", "race_compound"], "race_id")).set_index("compound")
    naive = slopes(fe_ols(d, "lap_time_s", [f"age_{c}" for c in COMPOUNDS],
                          ["driver_race", "race_compound"], "race_id")).set_index("compound")
    for c, true in TRUE.items():
        assert main.loc[c, "ci_low"] < true < main.loc[c, "ci_high"]
        assert abs(main.loc[c, "s_per_lap"] - true) < 0.01
        # without race-lap effects, fuel burn (-0.06 s/lap) is mixed into the slope
        assert naive.loc[c, "s_per_lap"] < true - 0.03


def test_driver_stint_effects_make_the_slope_unidentified():
    from models.tyre import NotIdentified
    d = estimation_sample(simulate(n_races=3, n_drivers=8, n_laps=30, seed=2))
    with pytest.raises(NotIdentified):
        fe_ols(d, "lap_time_s", [f"age_{c}" for c in COMPOUNDS], ["race_lap", "driver_stint"],
               "race_id")


def test_singletons_dropped_and_absorbed_columns_reported():
    d = estimation_sample(simulate(n_races=2, n_drivers=4, n_laps=15, seed=3))
    d["const_in_stint"] = d["driver_stint"].factorize()[0].astype(float)
    r = fe_ols(d, "lap_time_s", ["age_SOFT", "const_in_stint"], ["race_lap", "driver_stint"],
               "race_id")
    assert "const_in_stint" in r["dropped_absorbed"]


def test_tyre_run_end_to_end(tmp_path):
    from models.tyre_run import run_tyre
    laps = simulate(n_races=6, n_drivers=10, n_laps=40, seed=4)
    p = tmp_path / "laps.parquet"
    laps.to_parquet(p, index=False)
    text = run_tyre(p, out=tmp_path / "t3").read_text()
    assert "main: race-lap + driver-race + race-compound FE" in text and "not measured" in text
    assert "not identified, as expected" in text
    curve = pd.read_csv(tmp_path / "t3" / "tyre_age_curves.csv")
    assert set(curve["compound"]) == set(COMPOUNDS)
