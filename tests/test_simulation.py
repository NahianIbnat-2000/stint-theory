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
    js = json.loads((root / "out" / "backtest.json").read_text())
    if "calibration" in js:
        c = js["calibration"]
        assert 0 <= c["coverage50"] <= c["coverage90"] <= 1
        assert abs(c["below90"] + c["above90"] + c["coverage90"] - 1) < 1e-9
    monkeypatch.setattr(backtest, "OUT", root / "out")
    from simulation.__main__ import demo
    rid = sorted(laps["race_id"].unique())[2]
    demo(rid, "D01", 8, plan="20:H", n=40)
    out = capsys.readouterr().out
    assert "your plan" in out and "best 1-stop" in out and "counterfactual" in out


# ------------------------------------------------------------------ pace model v3
def confounded_panel(seed=0):
    """SIMULATED DATA. Hards are run late in the race (low fuel), races differ in
    track evolution, drivers differ in pace. True values below."""
    rng = np.random.default_rng(seed)
    kappa = {"SOFT": -0.5, "MEDIUM": 0.0, "HARD": 0.4}
    wear = {"SOFT": 0.07, "MEDIUM": 0.05, "HARD": 0.04}
    rows = []
    for r in range(12):
        evo = rng.uniform(-0.09, -0.04)
        for drv in range(14):
            start = "SOFT" if drv % 2 else "MEDIUM"
            stop = int(rng.integers(12, 30))
            mu = rng.normal(0, 0.4)
            for lap in range(1, 51):
                comp, age, stint = (start, lap, 1) if lap <= stop else ("HARD", lap - stop, 2)
                t = 90 + r + mu + evo * lap + kappa[comp] + wear[comp] * age + rng.normal(0, 0.08)
                rows.append({"race_id": f"R{r:02d}", "driver": f"D{drv:02d}", "lap_number": lap,
                             "stint": stint, "compound_relative": comp, "tyre_life": age,
                             "lap_time_s": t, "is_clean_green": True})
    return pd.DataFrame(rows)


def test_pace_v3_recovers_offsets_and_wear_under_confounding():
    d = params.pace_sample(confounded_panel())
    c = params.fit_pace(d)["coef"]
    def slope(comp, a=10):
        return c[f"age_{comp}"] + 2 * c[f"age2_{comp}"] * a
    assert c["k_HARD"] == pytest.approx(0.4, abs=0.08)
    assert c["k_SOFT"] == pytest.approx(-0.5, abs=0.08)
    for comp, w in {"SOFT": 0.07, "MEDIUM": 0.05, "HARD": 0.04}.items():
        assert slope(comp) == pytest.approx(w, abs=0.006), comp
    assert c["lap_number"] == pytest.approx(-0.065, abs=0.015)


def test_circuit_scale_averages_one_and_is_capped():
    rng = np.random.default_rng(1)
    ev = pd.Series({f"r{i}": f"E{i % 10}" for i in range(30)})
    sl = pd.Series(np.abs(rng.normal(0.05, 0.04, 30)), index=ev.index)
    sl.iloc[0] = 1.0                                     # one wild race
    s = [params.circuit_scale(sl, ev, r)["scale"] for r in ev.index]
    assert all(params.SCALE_BOUNDS[0] <= x <= params.SCALE_BOUNDS[1] for x in s)
    assert np.mean(s) == pytest.approx(1.0, abs=0.15)


def test_tyre_term_never_falls_with_age():
    p = {"pace": {"coef": {"age_SOFT": 0.1, "age2_SOFT": -0.004}, "age_cap": 40,
                  "tail_slope": {"SOFT": 0.03}}, "circuit": {"scale": 1.0}}
    g = engine.Pace(p).g("SOFT", np.arange(0, 60))
    assert np.all(np.diff(g) >= -1e-12)                  # peak of the quadratic at 12.5
    assert g[59] - g[58] == pytest.approx(0.03)          # tail at the linear slope
