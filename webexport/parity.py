"""Reference outputs from the Python simulator for the JavaScript parity test.

The Python side reads the same web JSON the website reads (exported decision
states, rounded), so both languages start from identical inputs. The node test
(web/test/parity.test.mjs) must reproduce every number to 1e-6 s.
"""
from __future__ import annotations

import json
from pathlib import Path

from simulation.constraints import RaceRules
from simulation.engine import DecisionState, Strategy, expected_time, simulate
from simulation.strategy import best_by_stops, best_strategies

FULL = {"S": "SOFT", "M": "MEDIUM", "H": "HARD"}


def state_from_web(p: dict, drv: str, i: int) -> DecisionState:
    s = p["drivers"][drv]["states"]
    return DecisionState(p["race_id"], drv, s["lap"][i], p["total_laps"], s["comp"][i], s["age"][i],
                         s["stops"][i], tuple(FULL[c] for c in s["used"][i]), s["mu"][i],
                         s["mu_se"][i], s["n"][i])


def rules_from_web(p: dict) -> RaceRules:
    r = p["rules"]
    return RaceRules(r["min_stops"], r["max_set_life"], r["note"])


def _strat(s: Strategy) -> dict:
    return {"stop_laps": list(s.stop_laps), "compounds": list(s.compounds)}


def make_cases(data: Path, max_races: int = 3, n: int = 40) -> dict:
    index = json.loads((data / "sim" / "index.json").read_text())
    cases = []
    for r in [x for x in index if x["simulatable"]][:max_races]:
        p = json.loads((data / "sim" / "races" / f"{r['race_id']}.json").read_text())
        for drv in sorted(p["drivers"])[:2]:
            s = p["drivers"][drv]["states"]
            if not s["lap"]:
                continue
            i = len(s["lap"]) // 2
            st = state_from_web(p, drv, i)
            rules = rules_from_web(p)
            best = best_by_stops(p, st, rules, max_stops=2)
            top = best_strategies(p, st, rules, max_stops=2, top=3)
            strats = list(best.values())
            if not strats:
                continue
            case = {"race_id": p["race_id"], "driver": drv, "state_index": i,
                    "best_by_stops": {str(k): _strat(v) for k, v in best.items()},
                    "top3": [_strat(x) for x in top],
                    "expected": [expected_time(p, st, x) for x in strats],
                    "strategies": [_strat(x) for x in strats], "runs": []}
            sc_lap = min(st.decision_lap + 5, p["total_laps"] - 1)
            for mode, seed in (("none", 11), ("random", 12), ("at_lap", 13)):
                res = simulate(p, st, strats, n=n, seed=seed, sc_mode=mode, sc_lap=sc_lap)
                case["runs"].append({"mode": mode, "seed": seed, "n": n, "sc_lap": sc_lap,
                                     "times": res["times"].tolist(), "sc_draws": res["sc_draws"]})
            cases.append(case)
    return {"cases": cases}


def write_parity(data: Path, out: Path) -> Path:
    out.write_text(json.dumps(make_cases(data), default=float))
    return out
