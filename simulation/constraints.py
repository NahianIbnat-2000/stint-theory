"""Strategy rules the simulator enforces.

General (dry race): at least two different slick compounds must be used in the
race (FIA Sporting Regulations). Race-specific rules, each checked against
official or press sources (docs/methodology_simulator.md):
  * 2023 Qatar GP: at most 18 laps of total tyre life per set (history included).
  * 2025 Monaco GP: at least two pit stops (three sets of tyres).
  * 2025 Qatar GP: at most 25 laps per set (cumulative over the weekend).
Not modelled: the number of sets of each compound a team still has, and tyre
life used in practice and qualifying beyond what the race data shows.
"""
from __future__ import annotations

from dataclasses import dataclass

SLICKS = ("SOFT", "MEDIUM", "HARD")
MIN_STINT = 3


@dataclass(frozen=True)
class RaceRules:
    min_stops: int = 0
    max_set_life: int | None = None   # laps of tyre life per set, history included
    note: str = ""


SPECIAL = {
    (2023, "Qatar Grand Prix"): RaceRules(max_set_life=18,
                                          note="FIA/Pirelli: 18 laps maximum tyre life per set"),
    (2025, "Monaco Grand Prix"): RaceRules(min_stops=2,
                                           note="FIA: at least two pit stops (three sets)"),
    (2025, "Qatar Grand Prix"): RaceRules(max_set_life=25,
                                          note="Pirelli: 25 laps maximum per set"),
}


def rules_for(season: int, event_name: str) -> RaceRules:
    return SPECIAL.get((int(season), event_name), RaceRules())


def check(strategy, state, rules: RaceRules) -> list[str]:
    """Problems with a strategy (empty list = allowed).

    strategy: Strategy (stops after the decision lap); state: DecisionState.
    """
    errs = []
    N, L = state.total_laps, state.decision_lap
    stops = list(strategy.stop_laps)
    comps = list(strategy.compounds)
    if len(stops) != len(comps):
        errs.append("each stop needs a compound")
    if any(c not in SLICKS for c in comps):
        errs.append("only dry compounds (soft, medium, hard) are simulated")
    if stops != sorted(stops) or len(set(stops)) != len(stops):
        errs.append("stop laps must be increasing")
    if stops and (stops[0] <= L or stops[-1] >= N):
        errs.append(f"stops must be between lap {L + 1} and lap {N - 1}")
    bounds = [L] + stops + [N]
    for a, b in zip(bounds[1:-1], bounds[2:]):
        if b - a < MIN_STINT:
            errs.append(f"stints after a stop must be at least {MIN_STINT} laps")
            break
    used = set(state.compounds_used) | {state.current_compound} | set(comps)
    if len(used & set(SLICKS)) < 2:
        errs.append("a dry race requires at least two different compounds")
    if state.stops_so_far + len(stops) < rules.min_stops:
        errs.append(f"this race requires at least {rules.min_stops} pit stops")
    if rules.max_set_life is not None:
        first_end = stops[0] if stops else N
        if state.current_age + (first_end - L) > rules.max_set_life:
            errs.append(f"current set would exceed {rules.max_set_life} laps of life")
        for a, b in zip(stops, stops[1:] + [N]):
            if b - a > rules.max_set_life:
                errs.append(f"a new set would exceed {rules.max_set_life} laps of life")
                break
    return errs
