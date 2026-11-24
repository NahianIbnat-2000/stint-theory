"""Coverage and data-quality report for the feasibility audit (Phase 1)."""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import pandas as pd

from . import config
from .clean import EXCLUSION_FLAGS, STRICT_FLAGS

FIELDS_TO_PROFILE = ["lap_time_s", "s1_s", "s2_s", "s3_s", "tyre_life", "compound_relative",
                     "position_end_of_lap", "grid_position", "track_temp_c", "air_temp_c",
                     "scheduled_laps"]


def coverage_tables(clean: pd.DataFrame, manifests: list[dict], validation: list[dict]) -> dict:
    by_season = {}
    for m in manifests:
        s = m["season"]
        st = pd.Series([x["status"] for x in m["sessions"]]).value_counts().to_dict()
        by_season[s] = {"races_listed": m.get("races_listed"), "ingest_status": st}
    for v in validation:
        d = by_season.setdefault(v["season"], {})
        d["validated"] = d.get("validated", 0) + 1
        d["passed_validation"] = d.get("passed_validation", 0) + int(v["passed"])

    if clean.empty:
        return {"by_season": by_season}

    g = clean.groupby("season")
    lap_stats = pd.DataFrame({
        "races_in_sample": g["race_id"].nunique(),
        "driver_laps": g.size(),
        "clean_green_laps": g["is_clean_green"].sum(),
        "clean_green_share": g["is_clean_green"].mean().round(4),
        "strict_clean_share": g["is_clean_green_strict"].mean().round(4),
        "stints": clean[["season", "race_id", "driver", "stint"]].drop_duplicates()
                  .groupby("season").size(),
    })
    nonnull = clean.groupby("season")[FIELDS_TO_PROFILE].agg(lambda x: x.notna().mean()).round(4)
    flag_rates = clean.groupby("season")[STRICT_FLAGS].mean().round(4)
    tl_bin = pd.cut(clean["tyre_life"], [0, 5, 10, 15, 20, 30, 80], right=True)
    # laps that would be clean if not for the outlier flag: its marginal effect
    usable = ~clean[EXCLUSION_FLAGS].any(axis=1)
    out_by_age = (clean[usable].assign(tyre_life_bin=tl_bin[usable].astype(str))
                  .groupby(["season", "tyre_life_bin"], observed=True)
                  .agg(laps=("flag_pace_outlier", "size"),
                       outlier_share=("flag_pace_outlier", "mean")).round(4).reset_index())
    comp = (clean.groupby(["season", "compound_raw"], dropna=False).size()
            .rename("laps").reset_index())
    comp["compound_raw"] = comp["compound_raw"].astype("string").fillna("<missing>")
    comp_method = (clean.groupby(["season", "compound_map_method"], dropna=False).size()
                   .rename("laps").reset_index())

    for s, row in lap_stats.iterrows():
        by_season.setdefault(int(s), {}).update({k: (float(v) if "share" in k else int(v))
                                                 for k, v in row.items()})
    checks = []
    for m in manifests:
        for s in m["sessions"]:
            if s.get("checks"):
                checks.append({"season": m["season"], "round": s["round"], **s["checks"]})
    recon = (pd.DataFrame(checks).drop(columns="round").groupby("season").sum()
             .reset_index().to_dict(orient="records")) if checks else []
    completeness = [{"season": v["season"], "round": v["round"], "event_name": v["event_name"],
                     "lap_completeness": None if v.get("lap_completeness") is None
                     else round(v["lap_completeness"], 4), "passed": v["passed"]}
                    for v in validation]
    return {
        "by_season": by_season,
        "lap_completeness": completeness,
        "reconstruction_checks": recon,
        "field_non_null_share": nonnull.reset_index().to_dict(orient="records"),
        "exclusion_flag_rates": flag_rates.reset_index().to_dict(orient="records"),
        "outlier_rate_by_tyre_life": out_by_age.to_dict(orient="records"),
        "compound_raw_counts": comp.to_dict(orient="records"),
        "compound_mapping_methods": comp_method.to_dict(orient="records"),
    }


def _md_table(df: pd.DataFrame) -> str:
    df = df.copy()
    cols = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        cells = []
        for v in r.to_list():
            if isinstance(v, dict):
                cells.append(", ".join(f"{k}: {x}" for k, x in v.items()))
            elif v is None or (not isinstance(v, (list, dict)) and pd.isna(v)):
                cells.append("")
            elif isinstance(v, float) and v.is_integer() and abs(v) >= 1:
                cells.append(str(int(v)))
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def write_report(cov: dict, validation_summary: pd.DataFrame, out_dir: Path | None = None) -> Path:
    out_dir = out_dir or config.REPORTS
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    (out_dir / "coverage.json").write_text(json.dumps({"generated_at_utc": stamp, **cov},
                                                      indent=2, default=str))
    parts = [
        "# STINT THEORY data coverage report",
        f"Generated {stamp} from the files in data/raw. All counts come from the data on disk.",
        "## Sessions and laps by season",
        _md_table(pd.DataFrame(cov["by_season"]).T.reset_index(names="season")
                  .sort_values("season")),
    ]
    if "field_non_null_share" in cov:
        parts += ["## Share of rows with a non-missing value",
                  _md_table(pd.DataFrame(cov["field_non_null_share"])),
                  "## Share of rows carrying each exclusion flag",
                  "Flags overlap, so shares do not add up.",
                  _md_table(pd.DataFrame(cov["exclusion_flag_rates"])),
                  "## Pace-outlier rate by tyre age",
                  "Among laps with no other exclusion flag, so this is the flag's own effect. "
                  "Should be roughly flat. A rise with tyre age means it is removing high-wear laps.",
                  _md_table(pd.DataFrame(cov["outlier_rate_by_tyre_life"])),
                  "## Raw compound labels",
                  _md_table(pd.DataFrame(cov["compound_raw_counts"])),
                  "## How the relative compound was assigned",
                  _md_table(pd.DataFrame(cov["compound_mapping_methods"]))]
    if cov.get("reconstruction_checks"):
        parts += ["## OpenF1 reconstruction checks (summed over races)",
                  "In-laps are inferred as the lap before an out-lap; `pit_rows_on_inferred_in_lap` "
                  "should be close to `pit_table_rows`. Unpaired or unmatched safety-car messages "
                  "need a manual look.",
                  _md_table(pd.DataFrame(cov["reconstruction_checks"]))]
    comp = [r for r in cov.get("lap_completeness", []) if r["lap_completeness"] is not None
            and r["lap_completeness"] < 0.98]
    parts += ["## Races with incomplete lap data",
              "Lap rows present / laps driven per the classification. Below 90% the race is "
              "excluded from the sample.",
              _md_table(pd.DataFrame(comp)) if comp else "_none below 98%_"]
    if not validation_summary.empty:
        nonInfo = validation_summary[validation_summary["severity"] != "info"]
        agg = (nonInfo.groupby(["season", "check", "severity"])
               .agg(sessions=("round", "nunique"), rows=("count", "sum")).reset_index())
        parts += ["## Validation issues (warnings and errors)", _md_table(agg)]
        validation_summary.to_csv(out_dir / "validation_issues.csv", index=False)
    path = out_dir / "coverage_report.md"
    path.write_text("\n\n".join(parts) + "\n")
    return path
