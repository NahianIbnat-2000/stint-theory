"""Strategy simulator command line.

    python -m simulation build                     # leave-race-out params for every race
    python -m simulation backtest                  # checks against what happened
    python -m simulation demo --race 2024_01 --driver VER --lap 15 [--sc random] [--plan "30:H"]
"""
from __future__ import annotations

import argparse

from .constraints import rules_for
from .engine import DISCLAIMER, Strategy, check, decision_state, observed_strategy, simulate, summarise


def parse_plan(text: str) -> Strategy:
    stops, comps = [], []
    for part in filter(None, (x.strip() for x in text.split(","))):
        lap, c = part.split(":")
        stops.append(int(lap))
        comps.append({"S": "SOFT", "M": "MEDIUM", "H": "HARD"}[c.strip().upper()[0]])
    return Strategy(tuple(stops), tuple(comps), "your plan")


def demo(race, driver, lap, sc="none", sc_lap=None, plan=None, n=1000, seed=2026):
    from .backtest import load_params
    from .strategy import best_by_stops
    p = load_params(race)
    if not p["simulatable"]:
        raise SystemExit("This race was largely wet; the simulator covers dry races only.")
    rules = rules_for(p["season"], p["event_name"])
    st = decision_state(p, driver, lap)
    cands = []
    obs = observed_strategy(p, driver, lap)
    if obs:
        obs.label = "observed: " + obs.describe(st.current_compound)
        cands.append(obs)
    if plan:
        s = parse_plan(plan)
        errs = check(s, st, rules)
        if errs:
            raise SystemExit("Plan not allowed: " + "; ".join(errs))
        s.label = "your plan: " + s.describe(st.current_compound)
        cands.append(s)
    for k, s in best_by_stops(p, st, rules).items():
        s.label = f"best {k}-stop: " + s.describe(st.current_compound)
        cands.append(s)
    res = simulate(p, st, cands, n=n, seed=seed, sc_mode=sc, sc_lap=sc_lap)
    print(f"{p['event_name']} {p['season']}, {driver}, decision after lap {lap} of "
          f"{p['total_laps']} on {st.current_compound} (age {st.current_age}).")
    if rules.note:
        print("Race rule:", rules.note)
    print(f"Safety car: {sc}; {n} draws, seed {seed}. Reference = first row.")
    for r in summarise(res, cands):
        pf = "" if r["p_faster_than_ref"] is None else f"  P(faster than ref) {r['p_faster_than_ref']:.2f}"
        print(f"  {r['strategy']:<55} mean {r['mean_s']:9.1f} s  delta {r['delta_vs_ref_mean_s']:+6.1f} s "
              f"[{r['delta_p05_s']:+.1f}, {r['delta_p95_s']:+.1f}]{pf}")
    print(DISCLAIMER)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="simulation")
    ap.add_argument("command", choices=["build", "backtest", "demo"])
    ap.add_argument("--race")
    ap.add_argument("--driver")
    ap.add_argument("--lap", type=int)
    ap.add_argument("--sc", default="none", choices=["none", "random", "at_lap"])
    ap.add_argument("--sc-lap", type=int)
    ap.add_argument("--plan", help='e.g. "28:H" or "20:M,45:S"')
    ap.add_argument("--n", type=int, default=1000)
    a = ap.parse_args(argv)
    if a.command == "build":
        from .params import build_all
        print(build_all())
    elif a.command == "backtest":
        from .backtest import run_backtest
        print(run_backtest())
    else:
        demo(a.race, a.driver, a.lap, a.sc, a.sc_lap, a.plan, a.n)


if __name__ == "__main__":
    main()
