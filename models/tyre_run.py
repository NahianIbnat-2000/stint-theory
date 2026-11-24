"""Task 3 runner: python -m models tyre

Writes research/results/task3/: report.md, estimates.json, tyre_age_curves.csv.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import numpy as np
import pandas as pd

from pipelines import config
from .run import _md
from .tyre import COMPOUNDS, FE_MAIN, NotIdentified, age_curve, estimation_sample, fe_ols, slopes

OUT = config.ROOT / "research" / "results" / "task3"
LAPS = config.PROCESSED / "laps_clean.parquet"
FE = FE_MAIN
LIN = [f"age_{c}" for c in COMPOUNDS]


def _spec(d, name, fe=FE, xs=LIN):
    r = fe_ols(d, "lap_time_s", xs, fe, "race_id")
    t = slopes(r)
    t.insert(0, "specification", name)
    t["n laps"], t["races"] = r["n"], r["clusters"]
    return t, r


def marginal(r, c, age):
    b1, b2 = r["coef"][f"age_{c}"], r["coef"][f"age2_{c}"]
    V = r["vcov"]
    v = V.loc[f"age_{c}", f"age_{c}"] + 4 * age ** 2 * V.loc[f"age2_{c}", f"age2_{c}"] \
        + 4 * age * V.loc[f"age_{c}", f"age2_{c}"]
    m = b1 + 2 * b2 * age
    return m, np.sqrt(v)


def run_tyre(laps_path: Path | None = None, out: Path | None = None) -> Path:
    out = out or OUT
    out.mkdir(parents=True, exist_ok=True)
    laps = pd.read_parquet(laps_path or LAPS)
    d = estimation_sample(laps)
    tables, results = [], {}
    main, results["main"] = _spec(d, "main: race-lap + driver-race + race-compound FE")
    tables.append(main)
    naive, results["naive"] = _spec(d, "naive: no race-lap FE (fuel and track not removed)",
                                    fe=["driver_race", "race_compound"])
    tables.append(naive)
    try:
        fe_ols(d, "lap_time_s", LIN, ["race_lap", "driver_stint"], "race_id")
        stint_check = "identified (unexpected: check the data)"
    except NotIdentified:
        stint_check = ("not identified, as expected: with driver-stint effects, tyre age is an "
                       "exact combination of the race-lap and stint effects")
    t, _ = _spec(d[d["lap_in_stint"] > 2], "R1: first 2 laps of each stint dropped")
    tables.append(t)
    t, _ = _spec(d[d["tyre_life"] <= 15], "R2: tyre age <= 15 laps")
    tables.append(t)
    t, _ = _spec(estimation_sample(laps, strict=True), "R4: strict sample (pace outliers out)")
    tables.append(t)
    try:
        t, _ = _spec(d, "R6: + race x stint-number FE (common push/manage pattern by stint)",
                     fe=FE + ["race_stintno"])
        tables.append(t)
    except NotIdentified:
        pass
    for season in sorted(d["season"].unique()):
        t, _ = _spec(d[d["season"] == season], f"R5: season {season}")
        tables.append(t)
    robust = pd.concat(tables, ignore_index=True)

    quad = fe_ols(d, "lap_time_s", LIN + [f"age2_{c}" for c in COMPOUNDS], FE, "race_id")
    qrows = []
    for c in COMPOUNDS:
        for a in (5, 10, 20, 30):
            m, s = marginal(quad, c, a)
            qrows.append({"compound": c, "tyre_age": a, "marginal s_per_lap": m, "se": s,
                          "ci_low": m - 1.96 * s, "ci_high": m + 1.96 * s})
    quad_t = pd.DataFrame(qrows)

    circ = []
    for ev, g in d.groupby("event_name"):
        g = g.assign(age_all=g["tyre_life"])
        try:
            r = fe_ols(g, "lap_time_s", ["age_all"], FE, "race_id")
        except Exception:
            continue
        if "age_all" in r["coef"] and r["clusters"] >= 2:
            b, s = r["coef"]["age_all"], r["se"]["age_all"]
            circ.append({"circuit": ev, "races": r["clusters"], "n laps": r["n"],
                         "s_per_lap": b, "se": s, "ci_low": b - 1.96 * s, "ci_high": b + 1.96 * s})
    circ_t = pd.DataFrame(circ).sort_values("s_per_lap", ascending=False)

    curve = age_curve(d)
    curve.to_csv(out / "tyre_age_curves.csv", index=False)

    implied = []
    for c in COMPOUNDS:
        k = f"age_{c}"
        implied.append({"compound": c,
                        "naive minus main (s/lap)": results["naive"]["coef"][k] - results["main"]["coef"][k]})
    parts = [
        "# Task 3: lap-time change associated with tyre age",
        f"Generated {dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')}. "
        f"Sample: clean green dry laps on slicks, 2023-2025, {main['n laps'].iloc[0]} laps in "
        f"{main['races'].iloc[0]} races after dropping singleton groups. Standard errors "
        "clustered by race. These are estimated associations with tyre age, not measured "
        "tyre wear; see docs/methodology_tyre.md for the assumptions.",
        "## Main estimate and robustness (seconds per extra lap of tyre age)",
        "Positive = laps get slower as the tyres age, holding fixed the race lap (fuel, "
        "track), the driver's pace in that race and the compound's pace level at that race.",
        _md(robust, 4),
        "## Identification check",
        f"Same model with driver-stint instead of driver-race effects: {stint_check}. The "
        "main slope is therefore identified only from pace gains at pit stops compared "
        "across drivers who stopped at different tyre ages, under two assumptions: a "
        "driver's underlying pace is the same across stints, and compound offsets at a race "
        "are common to all cars.",
        "## What the race-lap fixed effects remove",
        "The naive slope mixes tyre ageing with everything that changes lap by lap for all "
        "cars (mostly fuel burn, which makes cars faster). The difference is roughly the "
        "common per-lap trend.",
        _md(pd.DataFrame(implied), 4),
        "## Curvature: quadratic specification, marginal effect at given tyre ages",
        _md(quad_t, 4),
        "## Heterogeneity by circuit (all slick compounds pooled)",
        "Compound levels are absorbed by the stint effects; the slope is pooled across "
        "compounds, so circuits with more soft running look steeper.",
        _md(circ_t, 4),
        "## Non-parametric curve",
        "Effect of each tyre age relative to age 5, by compound, saved in "
        "`tyre_age_curves.csv` (used by the website). Ages above 35 pooled.",
        _md(curve[curve["tyre_age"].isin([1, 2, 3, 10, 15, 20, 25, 30, 35])], 3),
    ]
    (out / "report.md").write_text("\n\n".join(parts) + "\n")
    (out / "estimates.json").write_text(json.dumps({
        "robustness": robust.to_dict(orient="records"),
        "quadratic_marginal": quad_t.to_dict(orient="records"),
        "by_circuit": circ_t.to_dict(orient="records")}, indent=2, default=float))
    return out / "report.md"
