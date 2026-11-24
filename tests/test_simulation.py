"""Simulator invariants on synthetic races. SIMULATED DATA ONLY."""
import itertools
import json

import numpy as np
import pandas as pd
import pytest

from fixtures import make_raw_race
from pipelines.clean import clean_session
from simulation import constraints, engine, params
from simulation.constraints import RaceRules
from simulation.engine import Strategy
from simulation.rng import Mulberry32

EVENTS = ["Alpha GP", "Beta GP", "Gamma GP"]


def build_laps(perturb_race=None):
    frames = []
    k = 0
    for season in (2023, 2024):
        for i, ev in enumerate(EVENTS):
            raw = make_raw_race(season, i + 1, n_drivers=8, n_laps=40, seed=k,
                                compounds=("MEDIUM", "HARD") if k % 2 else ("SOFT", "HARD"))
            raw["meta"]["event_name"] = ev
            c = clean_session(raw)
            if perturb_race == c["race_id"].iloc[0]:
                c["lap_time_s"] = c["lap_time_s"] + 3.0
            frames.append(c)
            k += 1
    return pd.concat(frames, ignore_index=True)


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    root = tmp_path_factory.mktemp("sim")
    laps = build_laps()
    lp = root / "laps.parquet"
    laps.to_parquet(lp, index=False)
    params.build_all(lp, out=root / "out", log=lambda *a: None)
    return root, laps


def load(root, rid):
    return json.loads((root / "out" / "races" / f"{rid}.json").read_text())


# ------------------------------------------------------------------ rng
def test_rng_matches_reference_mulberry32():
    r = Mulberry32(1)
    assert [r.next_u32() for _ in range(3)] == [2693262067, 11749833, 2265367787]
    a, b = Mulberry32(7), Mulberry32(7)
    assert a.normals(50).tolist() == b.normals(50).tolist()


# ------------------------------------------------------------------ rules
def state(**kw):
    base = dict(race_id="x", driver="D", decision_lap=10, total_laps=50, current_compound="MEDIUM",
                current_age=10, stops_so_far=0, compounds_used=("MEDIUM",), mu=0.0, mu_se=0.1,
                n_pace_laps=8)
    base.update(kw)
    return engine.DecisionState(**base)


def test_rules():
    st = state()
    ok = Strategy((25,), ("HARD",))
    assert constraints.check(ok, st, RaceRules()) == []
    assert constraints.check(Strategy((25,), ("MEDIUM",)), st, RaceRules())    # one compound
    assert constraints.check(Strategy((), ()), st, RaceRules())                 # no second compound
    assert constraints.check(Strategy((25, 26), ("HARD", "SOFT")), st, RaceRules())  # 1-lap stint
    assert constraints.check(Strategy((48,), ("HARD",)), st, RaceRules())        # last stint 2 laps
    monaco = constraints.rules_for(2025, "Monaco Grand Prix")
    assert constraints.check(ok, st, monaco)
    assert constraints.check(Strategy((25, 38), ("HARD", "HARD")), st, monaco) == []
    qatar = constraints.rules_for(2023, "Qatar Grand Prix")
    assert constraints.check(ok, st, qatar)                     # 10 + 15 > 18 laps on current set
    assert constraints.check(Strategy((19, 36), ("HARD", "MEDIUM")), st, qatar)  # 10 + 9 > 18
    assert constraints.check(Strategy((18, 36), ("HARD", "MEDIUM")), st, qatar) == []  # 18, 18, 14
    assert constraints.check(Strategy((18, 31), ("HARD", "MEDIUM")), st, qatar)  # last set 19 laps


# ------------------------------------------------------------------ params
def test_params_are_leave_race_out(built, tmp_path):
    root, laps = built
    rid = sorted(laps["race_id"].unique())[0]
    base = load(root, rid)
    pert = build_laps(perturb_race=rid)
    lp = tmp_path / "laps.parquet"
    pert.to_parquet(lp, index=False)
    params.build_all(lp, out=tmp_path / "out", races=[rid], log=lambda *a: None)
    pub = json.loads((tmp_path / "out" / "public" / "races" / f"{rid}.json").read_text())
    assert "drivers" not in pub                       # no lap histories in the public files
    new = json.loads((tmp_path / "out" / "races" / f"{rid}.json").read_text())
    for key in ("pace", "ar1", "pit_loss", "safety_car", "circuit"):
        assert json.dumps(new[key], sort_keys=True) == json.dumps(base[key], sort_keys=True), key
    assert new["drivers"] != base["drivers"]            # the race's own laps are still there


def test_decision_state_uses_only_laps_up_to_decision(built):
    root, laps = built
    rid = sorted(laps["race_id"].unique())[1]
    p = load(root, rid)
    st = engine.decision_state(p, "D02", 8)
    h = p["drivers"]["D02"]
    for k, ln in enumerate(h["lap_number"]):
        if ln > 8 and h["lap_time_s"][k] is not None:
            h["lap_time_s"][k] += 50
    assert engine.decision_state(p, "D02", 8).mu == pytest.approx(st.mu)
    assert st.current_age == 8 and st.stops_so_far == 0


# ------------------------------------------------------------------ engine
def test_pit_stop_adds_its_loss(built):
    root, laps = built
    p = load(root, sorted(laps["race_id"].unique())[2])
    st = engine.decision_state(p, "D01", 8)
    pace = engine.Pace(p)
    s = Strategy((20,), ("HARD",))
    lap_sum = sum(float(pace.lap_mean(st.mu, j, c, a)) for j, c, a, _ in engine.lap_plan(st, s))
    assert engine.expected_time(p, st, s) == pytest.approx(lap_sum + p["pit_loss"]["mean_s"])


def test_simulation_reproducible_and_common_random_numbers(built):
    root, laps = built
    p = load(root, sorted(laps["race_id"].unique())[2])
    st = engine.decision_state(p, "D01", 8)
    a = Strategy((20,), ("HARD",), "a")
    r1 = engine.simulate(p, st, [a, a], n=50, seed=3, sc_mode="random")
    r2 = engine.simulate(p, st, [a, a], n=50, seed=3, sc_mode="random")
    np.testing.assert_array_equal(r1["times"], r2["times"])
    np.testing.assert_array_equal(r1["times"][:, 0], r1["times"][:, 1])   # same draws
    b = Strategy((20, 30), ("HARD", "SOFT"), "b")
    r = engine.simulate(p, st, [a, b], n=200, seed=4)
    d = (r["times"][:, 1] - r["times"][:, 0]).mean()
    exp = engine.expected_time(p, st, b) - engine.expected_time(p, st, a)
    assert d == pytest.approx(exp, abs=1.0)


def test_safety_car_makes_stops_cheaper(built):
    """Under an SC at lap 20, stopping on lap 20 gains against stopping on lap 23,
    compared with the same two plans without a safety car."""
    root, laps = built
    p = load(root, sorted(laps["race_id"].unique())[2])
    p["pit_loss"]["neutralised_factor"] = 0.5
    st = engine.decision_state(p, "D01", 8)
    a, b = Strategy((20,), ("HARD",), "a"), Strategy((23,), ("HARD",), "b")
    g = engine.simulate(p, st, [a, b], n=30, seed=5)["times"]
    sc = engine.simulate(p, st, [a, b], n=30, seed=5, sc_mode="at_lap", sc_lap=20)["times"]
    assert (sc[:, 0] - sc[:, 1]).mean() < (g[:, 0] - g[:, 1]).mean() - 0.3 * p["pit_loss"]["mean_s"]
    assert sc.mean() > g.mean()                         # SC laps are slower


# ------------------------------------------------------------------ optimiser
def test_dp_matches_brute_force(built):
    from simulation.strategy import best_strategies
    root, laps = built
    p = load(root, sorted(laps["race_id"].unique())[3])
    p["total_laps"] = 30
    st = engine.decision_state(p, "D00", 8)
    st.total_laps = 30
    rules = RaceRules()
    best = best_strategies(p, st, rules, max_stops=2, top=1)[0]
    brute = []
    for k in (0, 1, 2):
        for laps_ in itertools.combinations(range(9, 30), k):
            for comps in itertools.product(("SOFT", "MEDIUM", "HARD"), repeat=k):
                s = Strategy(laps_, comps)
                if not constraints.check(s, st, rules):
                    brute.append(engine.expected_time(p, st, s))
    assert engine.expected_time(p, st, best) == pytest.approx(min(brute), abs=1e-6)


def test_backtest_and_demo_run(built, capsys, monkeypatch):
    from simulation import backtest
    root, laps = built
    text = backtest.run_backtest(root / "out").read_text()
    assert "Simulator backtest" in text
    monkeypatch.setattr(backtest, "OUT", root / "out")
    from simulation.__main__ import demo
    rid = sorted(laps["race_id"].unique())[2]
    demo(rid, "D01", 8, plan="20:H", n=40)
    out = capsys.readouterr().out
    assert "your plan" in out and "best 1-stop" in out and "counterfactual" in out
