"""Single-car race-time simulator from a decision lap to the flag.

Strategy outcomes are model-based counterfactual estimates, not observations of
what would necessarily have happened. One car is simulated against the clock:
traffic, track position and other cars' strategies are not modelled, so the
simulator reports race time, never finishing positions.

Lap time of lap j (after the decision lap L):
  mu + beta * j + kappa[c] + s * g_c(age)  + AR(1) noise
plus, on a stop lap, the pit loss (in-lap + out-lap minus two normal laps), and
under a safety car the lap is slowed by the SC factor and a stop costs less.
mu is the driver's pace estimated from laps up to L only.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .constraints import SLICKS, RaceRules, check
from .rng import Mulberry32

DISCLAIMER = ("Strategy outcomes are model-based counterfactual estimates, not observations "
              "of what would necessarily have happened.")


@dataclass
class Strategy:
    stop_laps: tuple
    compounds: tuple
    label: str = ""

    def describe(self, current: str) -> str:
        seq = [current[0]] + [c[0] for c in self.compounds]
        stops = ", ".join(str(s) for s in self.stop_laps) or "no further stops"
        return f"{'-'.join(seq)} (stops: {stops})"


@dataclass
class DecisionState:
    race_id: str
    driver: str
    decision_lap: int
    total_laps: int
    current_compound: str
    current_age: int
    stops_so_far: int
    compounds_used: tuple
    mu: float              # driver pace intercept, from laps <= L
    mu_se: float
    n_pace_laps: int
    notes: list = field(default_factory=list)


# ------------------------------------------------------------------ pace pieces
class Pace:
    def __init__(self, p: dict, coef: dict | None = None):
        self.c = dict(coef or p["pace"]["coef"])
        self.cap = p["pace"]["age_cap"]
        self.scale = p["circuit"]["scale"]

    def kappa(self, comp):
        return self.c.get(f"k_{comp}", 0.0)

    def g(self, comp, age):
        """Tyre-age term; quadratic up to the cap, then linear at the cap's slope."""
        b1, b2 = self.c[f"age_{comp}"], self.c[f"age2_{comp}"]
        age = np.asarray(age, float)
        a = np.minimum(age, self.cap)
        val = b1 * a + b2 * a ** 2
        slope_cap = b1 + 2 * b2 * self.cap
        return self.scale * (val + np.maximum(age - self.cap, 0) * slope_cap)

    def lap_mean(self, mu, lap, comp, age):
        return mu + self.c["lap_number"] * np.asarray(lap, float) + self.kappa(comp) + self.g(comp, age)


# v2 (after the first backtest): 30 instead of 8. With 8, mu came from late-stint
# laps only and absorbed end-of-stint slowness (model too slow after a stop by
# about 0.3 s/lap). See docs/model_changes.md.
N_PACE = 30


def decision_state(p: dict, driver: str, lap: int, n_pace: int = N_PACE) -> DecisionState:
    """State known at the end of `lap`. Pace intercept mu from the driver's clean
    laps up to `lap` (most recent n_pace), net of the model's lap, compound and
    tyre-age terms."""
    h = p["drivers"][driver]
    laps = np.array(h["lap_number"])
    if lap not in set(laps.tolist()):
        raise ValueError(f"{driver} did not complete lap {lap}")
    i = int(np.where(laps == lap)[0][0])
    comp = h["compound_relative"][i]
    if comp not in SLICKS:
        raise ValueError("the simulator handles dry running on slicks only")
    pace = Pace(p)
    idx = [k for k in range(i + 1) if h["is_clean_green"][k]
           and h["compound_relative"][k] in SLICKS and h["lap_time_s"][k] is not None][-n_pace:]
    notes = []
    if len(idx) < 3:
        clean = [laps[k] for k in range(len(laps)) if h["is_clean_green"][k]
                 and h["compound_relative"][k] in SLICKS]
        first = clean[2] if len(clean) >= 3 else None
        raise ValueError(f"{driver} has fewer than 3 clean laps by lap {lap}; "
                         + (f"the earliest usable decision lap is {first}" if first
                            else "this driver has too few clean laps in this race"))
    resid = [h["lap_time_s"][k] - (pace.lap_mean(0.0, laps[k], h["compound_relative"][k],
                                                 h["tyre_life"][k])) for k in idx]
    mu = float(np.mean(resid))
    mu_se = float(np.std(resid, ddof=1) / np.sqrt(len(resid))) if len(resid) > 1 else 0.5
    stints = h["stint"][: i + 1]
    used = tuple(sorted({c for c in h["compound_relative"][: i + 1] if c in SLICKS}))
    return DecisionState(p["race_id"], driver, lap, p["total_laps"], comp,
                         int(h["tyre_life"][i]), int(max(stints) - 1), used, mu, mu_se, len(idx),
                         notes)


def observed_strategy(p: dict, driver: str, lap: int) -> Strategy | None:
    """What the driver actually did after `lap` (stops and compounds), or None if
    the driver did not finish or the rest of the race was not dry."""
    h = p["drivers"][driver]
    laps = h["lap_number"]
    if max(laps) < p["total_laps"]:
        return None
    stops, comps = [], []
    for k, ln in enumerate(laps):
        if ln > lap and h["flag_pit_in"][k] and ln < p["total_laps"]:
            nxt = h["compound_relative"][k + 1] if k + 1 < len(laps) else None
            if nxt not in SLICKS:
                return None
            stops.append(int(ln))
            comps.append(nxt)
    return Strategy(tuple(stops), tuple(comps), "observed")


# ------------------------------------------------------------------ deterministic
def lap_plan(state: DecisionState, s: Strategy):
    """Per lap after L: (lap, compound, tyre age, is_stop_lap)."""
    L, N = state.decision_lap, state.total_laps
    comp, age0, start = state.current_compound, state.current_age, L
    stops = dict(zip(s.stop_laps, s.compounds))
    out = []
    for j in range(L + 1, N + 1):
        age = age0 + (j - start)
        out.append((j, comp, age, j in stops))
        if j in stops:
            comp, age0, start = stops[j], 0, j
    return out


def expected_time(p: dict, state: DecisionState, s: Strategy, pace: Pace | None = None) -> float:
    """Expected remaining race time with no safety car (noise has mean zero)."""
    pace = pace or Pace(p)
    plan = lap_plan(state, s)
    total = sum(float(pace.lap_mean(state.mu, j, c, a)) for j, c, a, _ in plan)
    return total + len(s.stop_laps) * p["pit_loss"]["mean_s"]


# ------------------------------------------------------------------ Monte Carlo
def simulate(p: dict, state: DecisionState, strategies: list[Strategy], n: int = 1000,
             seed: int = 2026, sc_mode: str = "none", sc_lap: int | None = None) -> dict:
    """Common random numbers: in each draw every strategy sees the same pace
    parameters, driver pace, residual path, pit-loss shocks and safety car.

    sc_mode: "none" | "random" (historical rate from other races) | "at_lap" (sc_lap).
    Returns total times (n x strategies) plus summaries.
    """
    rng = Mulberry32(seed)
    names = p["pace"]["names"]
    b = np.array([p["pace"]["coef"][k] for k in names])
    V = np.array(p["pace"]["vcov"])
    Lc = np.linalg.cholesky(V + 1e-12 * np.eye(len(b)))
    L, N = state.decision_lap, state.total_laps
    n_laps = N - L
    phi, sig = p["ar1"]["phi"], p["ar1"]["sigma_innov"]
    sig0 = p["ar1"]["sigma_marginal"]
    pl, sc = p["pit_loss"], p["safety_car"]
    pmf = sorted((int(k), v) for k, v in sc["duration_pmf"].items()) or [(4, 1.0)]
    plans = [lap_plan(state, s) for s in strategies]
    T = np.zeros((n, len(strategies)))
    sc_used = np.zeros(n, dtype=int)
    for i in range(n):
        coef = dict(zip(names, b + Lc @ rng.normals(len(b))))
        pace = Pace(p, coef)
        mu = state.mu + state.mu_se * rng.normal()
        z = rng.normals(n_laps)
        e = np.empty(n_laps)
        e[0] = sig0 * z[0]
        for k in range(1, n_laps):
            e[k] = phi * e[k - 1] + sig * z[k]
        stop_shocks = rng.normals(8)
        # safety car: start lap and length, same for every strategy in this draw
        sc_laps = set()
        u_sc = rng.uniforms(n_laps)
        u_len = rng.uniform()
        if sc_mode == "random":
            hits = np.where(u_sc < sc["hazard_per_lap"])[0]
            start = L + 1 + int(hits[0]) if len(hits) else None
        elif sc_mode == "at_lap":
            start = sc_lap
        else:
            start = None
        if start is not None:
            acc, length = 0.0, pmf[-1][0]
            for k, w in pmf:
                acc += w
                if u_len <= acc:
                    length = k
                    break
            sc_laps = set(range(start, min(start + length, N + 1)))
            sc_used[i] = 1
        base_mean = None
        for col, plan in enumerate(plans):
            t, n_stop = 0.0, 0
            for k, (j, c, a, stop) in enumerate(plan):
                lap_t = float(pace.lap_mean(mu, j, c, a)) + e[k]
                if j in sc_laps:
                    lap_t *= sc["lap_time_factor"]
                t += lap_t
                if stop:
                    loss = pl["mean_s"] + pl["sd_s"] * stop_shocks[min(n_stop, 7)]
                    if j in sc_laps:
                        loss *= pl["neutralised_factor"]
                    t += max(loss, 0.5 * pl["mean_s"])
                    n_stop += 1
            T[i, col] = t
    return {"times": T, "sc_draws": int(sc_used.sum()), "n": n, "seed": seed, "sc_mode": sc_mode}


def summarise(res: dict, strategies: list[Strategy], ref: int = 0) -> list[dict]:
    T = res["times"]
    out = []
    for j, s in enumerate(strategies):
        d = T[:, j] - T[:, ref]
        out.append({"strategy": s.label, "mean_s": float(T[:, j].mean()),
                    "p05_s": float(np.percentile(T[:, j], 5)),
                    "p95_s": float(np.percentile(T[:, j], 95)),
                    "delta_vs_ref_mean_s": float(d.mean()),
                    "delta_p05_s": float(np.percentile(d, 5)),
                    "delta_p95_s": float(np.percentile(d, 95)),
                    "p_faster_than_ref": float((d < 0).mean()) if j != ref else None})
    return out


__all__ = ["Strategy", "DecisionState", "decision_state", "observed_strategy", "expected_time",
           "simulate", "summarise", "check", "RaceRules", "DISCLAIMER", "Pace", "lap_plan"]
