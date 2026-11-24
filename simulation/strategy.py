"""Best strategy within the model's feasible set, by dynamic programming.

Objective: expected remaining race time without a safety car. The driver-pace and
per-lap-trend terms are the same for every strategy, so only compound offsets,
tyre-age terms and pit losses matter. The search is exact over all stop laps and
compounds allowed by the rules (constraints.py), up to `max_stops` more stops.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from .constraints import MIN_STINT, SLICKS, RaceRules, check
from .engine import DecisionState, Pace, Strategy, expected_time


def best_strategies(p: dict, state: DecisionState, rules: RaceRules, max_stops: int = 3,
                    top: int = 5, exact: bool = False) -> list[Strategy]:
    """Lowest expected-time strategies with up to `max_stops` more stops
    (exactly `max_stops` if exact=True)."""
    pace = Pace(p)
    L, N = state.decision_lap, state.total_laps
    loss = p["pit_loss"]["mean_s"]
    cap = rules.max_set_life

    max_age = state.current_age + N + 1
    prefix = {c: np.concatenate([[0.0], np.cumsum(pace.g(c, np.arange(1, max_age + 1)))])
              for c in SLICKS}

    def stint_cost(comp, age0, a, b):
        """Laps a+1..b on `comp`, tyre age age0 at lap a (prefix sums of the age term)."""
        n = b - a
        return float(pace.kappa(comp) * n + prefix[comp][age0 + n] - prefix[comp][age0])

    @lru_cache(maxsize=None)
    def go(start, comp, age0, used, stops_left, made):
        """Min cost from lap `start` (stint on `comp`, age age0 at `start`)."""
        best = []
        # option: no more stops
        if (cap is None or age0 + (N - start) <= cap) and len(set(used) & set(SLICKS)) >= 2 \
                and state.stops_so_far + made >= rules.min_stops and not (exact and stops_left):
            best.append((stint_cost(comp, age0, start, N), ()))
        if stops_left:
            first = start + (MIN_STINT if start > L else 1)
            for stop in range(first, N - MIN_STINT + 1):
                if cap is not None and age0 + (stop - start) > cap:
                    break
                here = stint_cost(comp, age0, start, stop) + loss
                for nc in SLICKS:
                    rest = go(stop, nc, 0, tuple(sorted(set(used) | {nc})), stops_left - 1, made + 1)
                    for cost, path in rest[:top]:
                        best.append((here + cost, ((stop, nc),) + path))
        best.sort(key=lambda x: x[0])
        return tuple(best[:top])

    used0 = tuple(sorted(set(state.compounds_used) | {state.current_compound}))
    found = go(L, state.current_compound, state.current_age, used0, max_stops, 0)
    out = []
    for cost, path in found:
        s = Strategy(tuple(x[0] for x in path), tuple(x[1] for x in path), "")
        if not check(s, state, rules):
            s.label = s.describe(state.current_compound)
            out.append(s)
    return out


def best_by_stops(p, state, rules, max_stops=3):
    """Best strategy for each number of further stops (0..max_stops) that is allowed."""
    res = {}
    for k in range(0, max_stops + 1):
        cand = best_strategies(p, state, rules, max_stops=k, top=1, exact=True)
        if cand:
            res[k] = cand[0]
    return res
