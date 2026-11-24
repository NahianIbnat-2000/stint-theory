"""Estimate simulator parameters for every race, leaving that race out.

For race r, everything about pace, pit loss and safety cars is estimated from the
other races only, so a simulation of race r never uses race r's own outcome
(no hindsight). The only information taken from race r is what a strategist would
know at the decision lap: the race distance, each driver's laps so far, and the
race-specific tyre rules.

Pace model (on clean green dry laps on slicks, other races):
  lap_time = mu[driver x race] + beta * lap
             + kappa[compound] + b1[compound] * age + b2[compound] * age^2 + e
with driver x race fixed effects and race-clustered covariance. beta is the common
per-lap trend (fuel burn plus track evolution). MEDIUM is the reference compound.
Tyre-age terms are scaled by a circuit factor (other years at the same circuit,
shrunk toward 1). Residuals e follow AR(1) within a driver's race.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from models.tyre import COMPOUNDS, estimation_sample, fe_ols
from pipelines import config
from .constraints import rules_for

OUT = config.ROOT / "research" / "results" / "simulator"
LAPS = config.PROCESSED / "laps_clean.parquet"
AGE_CAP = 40          # quadratic used up to this tyre age, linear beyond
PACE_X = ["lap_number", "k_SOFT", "k_HARD"] + [f"age_{c}" for c in COMPOUNDS] + \
         [f"age2_{c}" for c in COMPOUNDS]


# ------------------------------------------------------------------ pace
def pace_sample(laps: pd.DataFrame) -> pd.DataFrame:
    d = estimation_sample(laps)
    d["k_SOFT"] = (d["compound_relative"] == "SOFT").astype(float)
    d["k_HARD"] = (d["compound_relative"] == "HARD").astype(float)
    d["lap_number"] = d["lap_number"].astype(float)
    return d


def fit_pace(d: pd.DataFrame) -> dict:
    r = fe_ols(d, "lap_time_s", PACE_X, ["driver_race"], "race_id")
    return {"coef": r["coef"].to_dict(), "vcov": r["vcov"].values.tolist(),
            "names": list(r["coef"].index), "n": r["n"], "races": r["clusters"]}


def residual_ar1(d: pd.DataFrame, pace: dict) -> dict:
    """AR(1) of residuals (after removing driver-race means) within driver-races,
    on consecutive clean laps."""
    c = pace["coef"]
    pred = sum(c[k] * d[k] for k in c)
    e = d["lap_time_s"] - pred
    e = e - e.groupby(d["driver_race"]).transform("mean")
    s = d.assign(e=e).sort_values(["driver_race", "lap_number"])
    prev = s.groupby("driver_race")["e"].shift(1)
    consecutive = s.groupby("driver_race")["lap_number"].diff() == 1
    x, y = prev[consecutive], s.loc[consecutive, "e"]
    phi = float(np.clip((x * y).sum() / (x * x).sum(), 0, 0.99))
    innov = float(np.std(y - phi * x, ddof=1))
    return {"phi": phi, "sigma_innov": innov, "sigma_marginal": innov / np.sqrt(1 - phi ** 2)}


def race_slopes(d: pd.DataFrame) -> pd.Series:
    """Pooled tyre-age slope per race (race-lap, driver-race, race-compound FE)."""
    out = {}
    for rid, g in d.groupby("race_id"):
        g = g.assign(age_all=g["tyre_life"])
        try:
            r = fe_ols(g, "lap_time_s", ["age_all"], ["race_lap", "driver_race", "race_compound"],
                       "driver_race")
            out[rid] = float(r["coef"]["age_all"])
        except Exception:
            continue
    return pd.Series(out)


def circuit_scale(slopes: pd.Series, events: pd.Series, race_id: str) -> dict:
    """Ratio of this circuit's tyre-age slope (other years) to the average slope of
    all other races, shrunk toward 1 with weight n / (n + 1), n = other years here."""
    others = slopes.drop(race_id, errors="ignore")
    same = others[events.reindex(others.index) == events.get(race_id)]
    base = others.mean()
    if len(same) == 0 or base <= 0:
        return {"scale": 1.0, "raw": None, "years": 0}
    raw = float(max(same.mean(), 0.0) / base)
    w = len(same) / (len(same) + 1)
    return {"scale": float(1 + w * (raw - 1)), "raw": raw, "years": int(len(same))}


# ------------------------------------------------------------------ pit loss
def pit_stops(laps: pd.DataFrame) -> pd.DataFrame:
    """One row per pit stop: in-lap + out-lap time minus twice the driver's typical
    clean lap nearby. Stops whose in- or out-lap is under a red flag are dropped
    (tyre changes during a stoppage cost no pit-lane time)."""
    rows = []
    for (rid, drv), g in laps.sort_values("lap_number").groupby(["race_id", "driver"]):
        g = g.set_index("lap_number")
        for lap in g.index[g["flag_pit_in"]]:
            if lap + 1 not in g.index or not g.loc[lap + 1, "flag_pit_out"]:
                continue
            pair = g.loc[[lap, lap + 1]]
            if pair["flag_red"].any() or pair["lap_time_s"].isna().any():
                continue
            near = g.loc[(g.index >= lap - 6) & (g.index <= lap + 7) & g["is_clean_green"],
                         "lap_time_s"]
            if len(near) < 3:
                continue
            ref = float(near.median())
            rows.append({"race_id": rid, "season": int(g["season"].iloc[0]),
                         "event_name": g["event_name"].iloc[0], "driver": drv, "lap": int(lap),
                         "neutralised": bool((pair["flag_sc"] | pair["flag_vsc"]).any()),
                         "loss_s": float(pair["lap_time_s"].sum() - 2 * ref)})
    return pd.DataFrame(rows)


def pit_loss_params(stops: pd.DataFrame, race_id: str, event: str) -> dict:
    o = stops[stops["race_id"] != race_id]
    green = o[~o["neutralised"]]
    same = green[green["event_name"] == event]["loss_s"]
    # trim implausible values (slow stops are real but unrepeatable mistakes stay in the spread)
    q = same.clip(upper=same.quantile(0.95)) if len(same) >= 10 else same
    if len(q) >= 5:
        mean, source = float(q.median()), f"{event}, other years ({len(q)} green-flag stops)"
    else:
        mean, source = float(green["loss_s"].median()), "all other races (circuit has too few stops)"
    resid = (green["loss_s"] - green.groupby("event_name")["loss_s"].transform("median"))
    sd = float(resid.clip(resid.quantile(0.02), resid.quantile(0.95)).std())
    neut = o[o["neutralised"]]
    factor = float((neut["loss_s"] / neut["event_name"].map(
        green.groupby("event_name")["loss_s"].median())).median()) if len(neut) else 0.6
    return {"mean_s": mean, "sd_s": sd, "source": source,
            "neutralised_factor": float(np.clip(factor, 0.2, 1.0)),
            "n_green_stops_other_races": int(len(green))}


# ------------------------------------------------------------------ safety car
def sc_periods(laps: pd.DataFrame) -> pd.DataFrame:
    """Safety-car periods from the race leader's laps: consecutive SC laps."""
    rows = []
    for rid, g in laps.groupby("race_id"):
        lead = g[g["position_end_of_lap"] == 1].sort_values("lap_number")
        if lead.empty:
            continue
        sc = lead.set_index("lap_number")["flag_sc"]
        run = 0
        for lap, on in sc.items():
            if on:
                run += 1
            elif run:
                rows.append({"race_id": rid, "end_lap": int(lap) - 1, "laps": run})
                run = 0
        if run:
            rows.append({"race_id": rid, "end_lap": int(sc.index.max()), "laps": run})
    return pd.DataFrame(rows, columns=["race_id", "end_lap", "laps"])


def sc_params(laps: pd.DataFrame, periods: pd.DataFrame, race_id: str) -> dict:
    o_laps = laps[laps["race_id"] != race_id]
    race_laps = o_laps.groupby("race_id")["lap_number"].max().sum()
    o = periods[periods["race_id"] != race_id]
    hazard = float(len(o) / race_laps) if race_laps else 0.0
    dur = o["laps"].clip(upper=8).value_counts(normalize=True).sort_index()
    # SC lap time relative to the same driver's clean laps in that race
    ok = o_laps[o_laps["flag_sc"] & ~o_laps["flag_pit_in"] & ~o_laps["flag_pit_out"]
                & o_laps["lap_time_s"].notna()]
    ref = o_laps[o_laps["is_clean_green"]].groupby(["race_id", "driver"])["lap_time_s"].median()
    ratio = ok["lap_time_s"] / ok.set_index(["race_id", "driver"]).index.map(ref)
    return {"hazard_per_lap": hazard,
            "duration_pmf": {int(k): float(v) for k, v in dur.items()},
            "lap_time_factor": float(np.nanmedian(ratio)) if len(ratio) else 1.4,
            "periods_other_races": int(len(o))}


# ------------------------------------------------------------------ build
def driver_histories(g: pd.DataFrame) -> dict:
    cols = ["lap_number", "stint", "compound_relative", "tyre_life", "lap_time_s",
            "is_clean_green", "flag_pit_in", "flag_pit_out", "flag_sc", "flag_vsc", "flag_red",
            "position_end_of_lap"]
    out = {}
    for drv, h in g.sort_values("lap_number").groupby("driver"):
        h = h[cols].copy()
        h["compound_relative"] = h["compound_relative"].astype(object).where(
            h["compound_relative"].notna(), None)
        out[str(drv)] = {k: [None if (isinstance(v, float) and np.isnan(v)) else
                             (v.item() if hasattr(v, "item") else v) for v in h[k].tolist()]
                         for k in cols}
    return out


def build_all(laps_path: Path | None = None, out: Path | None = None,
              races: list[str] | None = None, log=print) -> Path:
    out = out or OUT
    (out / "races").mkdir(parents=True, exist_ok=True)
    laps = pd.read_parquet(laps_path or LAPS)
    d = pace_sample(laps)
    slopes = race_slopes(d)
    events = laps.groupby("race_id")["event_name"].first()
    stops = pit_stops(laps)
    periods = sc_periods(laps)
    stops.to_csv(out / "pit_stops.csv", index=False)
    index = []
    for rid in sorted(races or laps["race_id"].unique()):
        g = laps[laps["race_id"] == rid]
        season, event = int(g["season"].iloc[0]), g["event_name"].iloc[0]
        dry_slick_share = float(g["compound_relative"].isin(COMPOUNDS).mean())
        pace = fit_pace(d[d["race_id"] != rid])
        ar = residual_ar1(d[d["race_id"] != rid], pace)
        rules = rules_for(season, event)
        params = {
            "race_id": rid, "season": season, "round": int(g["round"].iloc[0]),
            "event_name": event, "total_laps": int(g["scheduled_laps"].iloc[0]),
            "dry_slick_share": dry_slick_share,
            "simulatable": dry_slick_share > 0.9,
            "rules": {"min_stops": rules.min_stops, "max_set_life": rules.max_set_life,
                      "note": rules.note},
            "pace": {**pace, "age_cap": AGE_CAP}, "ar1": ar,
            "circuit": circuit_scale(slopes, events, rid),
            "pit_loss": pit_loss_params(stops, rid, event),
            "safety_car": sc_params(laps, periods, rid),
            "drivers": driver_histories(g),
            "estimation": "leave-this-race-out: no parameter uses this race's laps",
        }
        (out / "races" / f"{rid}.json").write_text(json.dumps(params, default=float))
        index.append({"race_id": rid, "season": season, "event_name": event,
                      "total_laps": params["total_laps"], "simulatable": params["simulatable"]})
        log(f"params {rid} {event}")
    (out / "index.json").write_text(json.dumps(index, indent=1))
    return out
