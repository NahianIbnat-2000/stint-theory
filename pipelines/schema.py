"""Single source of truth for the data dictionary.

Every column produced by clean.py and features.py must be listed here; a test
enforces it. `kind` separates raw values, derived values, flags, model features
and targets, as the methodology requires.
"""
from __future__ import annotations

import json

from . import config
from .features import FIELD_WINDOW_S

# column: (dtype, unit, kind, origin, description)
CLEAN = {
    "season": ("int", "", "raw", "OpenF1 sessions.year", "Championship year."),
    "round": ("int", "", "derived", "OpenF1 sessions.date_start", "Order of the races held that season (may differ from the official round if an event was cancelled)."),
    "race_id": ("str", "", "derived", "pipeline", "season_round key, e.g. 2023_05."),
    "event_name": ("str", "", "raw", "OpenF1 meetings.meeting_name", "Grand Prix name."),
    "regulation_era": ("str", "", "derived", "config.regulation_era", "Technical-rules era of the season."),
    "scheduled_laps": ("int", "laps", "derived", "reference file or OpenF1 session_result", "Race distance. From data/reference/scheduled_laps.csv if checked by hand, else the winner's lap count (actual distance; wrong for shortened races)."),
    "scheduled_laps_source": ("str", "", "derived", "ingest", "reference_file, winner_laps_actual or missing."),
    "driver": ("str", "", "raw", "OpenF1 drivers.name_acronym", "Three-letter driver code."),
    "driver_number": ("str", "", "raw", "OpenF1 laps.driver_number", "Car number."),
    "team": ("str", "", "raw", "OpenF1 drivers.team_name", "Constructor name for that season."),
    "lap_number": ("int", "lap", "raw", "OpenF1 laps.lap_number", "Lap counter for the driver."),
    "stint": ("int", "", "derived", "OpenF1 stints (lap_start..lap_end)", "Stint counter, starts at 1, rises after each tyre change."),
    "tyre_life": ("float", "laps", "derived", "OpenF1 stints.tyre_age_at_start", "tyre_age_at_start + laps into the stint + 1 (1 on the first lap of a new set). Includes laps from earlier sessions for used sets."),
    "fresh_tyre": ("bool", "", "derived", "OpenF1 stints.tyre_age_at_start", "tyre_age_at_start == 0."),
    "lap_time_s": ("float", "s", "raw", "OpenF1 laps.lap_duration", "Measured lap time. Not a measure of tyre wear."),
    "s1_s": ("float", "s", "raw", "OpenF1 laps.duration_sector_1", "Sector 1 time."),
    "s2_s": ("float", "s", "raw", "OpenF1 laps.duration_sector_2", "Sector 2 time."),
    "s3_s": ("float", "s", "raw", "OpenF1 laps.duration_sector_3", "Sector 3 time."),
    "lap_start_session_s": ("float", "s", "derived", "OpenF1 laps.date_start", "Seconds from the session's scheduled start to lap start."),
    "lap_end_session_s": ("float", "s", "derived", "date_start + lap_duration", "Seconds from scheduled start to lap end (next lap start if duration missing)."),
    "position_end_of_lap": ("float", "place", "derived", "OpenF1 position", "Latest running position at or before lap end."),
    "track_status_raw": ("str", "", "derived", "OpenF1 race_control", "Codes of every neutralisation period overlapping the lap, rebuilt from race-control messages (1 green, 2 yellow, 4 SC, 5 red, 6 VSC)."),
    "compound_raw": ("str", "", "raw", "OpenF1 stints.compound", "Compound label as reported."),
    "compound_class": ("str", "", "derived", "clean.map_compounds", "SLICK, INTERMEDIATE or WET."),
    "compound_relative": ("str", "", "derived", "clean.map_compounds", "SOFT/MEDIUM/HARD (or INTERMEDIATE/WET). Missing where it cannot be assigned."),
    "compound_map_method": ("str", "", "derived", "clean.map_compounds", "How compound_relative was set: reported, rank_of_observed_2018, ambiguous_*, missing."),
    "flag_yellow": ("bool", "", "flag", "track status", "Yellow flag at some point in the lap."),
    "flag_sc": ("bool", "", "flag", "track status", "Safety car at some point in the lap."),
    "flag_red": ("bool", "", "flag", "track status", "Red flag at some point in the lap."),
    "flag_vsc": ("bool", "", "flag", "track status", "Virtual safety car deployed or ending in the lap."),
    "flag_track_status_missing": ("bool", "", "flag", "track status", "No status recorded for the lap."),
    "flag_pit_in": ("bool", "", "flag", "OpenF1 laps.is_pit_out_lap", "In-lap: the lap before an out-lap. Cross-checked against the pit table."),
    "flag_pit_out": ("bool", "", "flag", "OpenF1 laps.is_pit_out_lap", "Out-lap (driver left the pit lane)."),
    "flag_first_lap": ("bool", "", "flag", "lap_number", "Opening lap (standing start)."),
    "flag_missing_time": ("bool", "", "flag", "lap_time_s", "Lap time missing."),
    "flag_deleted": ("bool", "", "flag", "OpenF1 race_control message", "Lap time deleted by race control (and not reinstated). Known only after the fact."),
    "flag_not_accurate": ("bool", "", "flag", "FastF1 IsAccurate", "Always false with OpenF1 (no equivalent field). Kept for source compatibility."),
    "flag_fastf1_generated": ("bool", "", "flag", "FastF1 FastF1Generated", "Always false with OpenF1. Kept for source compatibility."),
    "flag_non_slick": ("bool", "", "flag", "compound_class", "Not on slick tyres, or compound unknown."),
    "flag_compound_relative_missing": ("bool", "", "flag", "compound_relative", "Relative compound not assigned. Informational; not an exclusion by itself."),
    "flag_beyond_scheduled": ("bool", "", "flag", "lap_number > scheduled_laps", "Lap past the race distance (extra row after the flag, or distance undercounted)."),
    "flag_post_neutralisation": ("bool", "", "flag", "previous lap", "First lap after an SC, VSC or red-flag lap."),
    "flag_rain": ("bool", "", "flag", "weather", "Rainfall reported at the latest sample before lap start."),
    "flag_pace_outlier": ("bool", "", "flag", "clean.robust_outlier_flag", "Robust z-score of the residual from a Theil-Sen line on lap number within driver-stint, above OUTLIER_Z. Uses the whole stint: sample selection only, never a feature."),
    "grid_position": ("float", "place", "raw", "OpenF1 starting_grid.position", "Starting grid slot. Final results are not joined."),
    "air_temp_c": ("float", "°C", "raw", "OpenF1 weather.air_temperature", "Latest air temperature at or before lap start."),
    "track_temp_c": ("float", "°C", "raw", "OpenF1 weather.track_temperature", "Latest track temperature at or before lap start."),
    "humidity_pct": ("float", "%", "raw", "OpenF1 weather.humidity", "Latest humidity at or before lap start."),
    "pressure_mbar": ("float", "mbar", "raw", "OpenF1 weather.pressure", "Latest air pressure at or before lap start."),
    "rainfall": ("bool", "", "raw", "OpenF1 weather.rainfall", "Rainfall indicator at the latest sample."),
    "wind_speed_ms": ("float", "m/s", "raw", "OpenF1 weather.wind_speed", "Latest wind speed at or before lap start."),
    "weather_age_s": ("float", "s", "derived", "pipeline", "Time between the weather sample and lap start."),
    "is_clean_green": ("bool", "", "flag", "clean.EXCLUSION_FLAGS", "No default exclusion flag set (pace outlier not included). Default research sample for scored targets."),
    "is_clean_green_strict": ("bool", "", "flag", "clean.STRICT_FLAGS", "is_clean_green and not a pace outlier. Sensitivity sample."),
    "exclusion_reason": ("str", "", "derived", "clean.EXCLUSION_FLAGS", "Semicolon list of every exclusion flag set on the lap, pace outlier included."),
}

FEATURES = {
    "lt_lag0": ("float", "s", "feature", "own laps <= t", "Lap time of lap t (any status)."),
    "lt_lag1": ("float", "s", "feature", "own laps <= t", "Lap time of lap t-1 (any status)."),
    "last_green_lt": ("float", "s", "feature", "own laps <= t", "Most recent real-time-green lap in this stint."),
    "roll_mean_green_3": ("float", "s", "feature", "own laps <= t", "Mean of the last 3 real-time-green laps in this stint."),
    "roll_std_green_5": ("float", "s", "feature", "own laps <= t", "Std. dev. of the last 5 real-time-green laps in this stint."),
    "trend_slope_green_5": ("float", "s/lap", "feature", "own laps <= t", "OLS slope of lap time on tyre life, last 5 green laps (needs 3)."),
    "green_laps_in_stint": ("int", "laps", "feature", "own laps <= t", "Count of real-time-green laps so far in the stint."),
    "target_tyre_life": ("float", "laps", "feature", "tyre_life + 1", "Tyre life on lap t+1 if the driver stays out."),
    "prev_stint_compound": ("str", "", "feature", "own laps <= t", "Relative compound of the previous stint."),
    "pit_stops_so_far": ("float", "stops", "feature", "stint - 1", "Tyre changes made before lap t."),
    "race_progress": ("float", "share", "feature", "lap / scheduled", "Share of scheduled distance done."),
    "laps_remaining_sched": ("float", "laps", "feature", "scheduled - lap", "Laps left to the scheduled finish. Main fuel-load proxy."),
    "field_green_median_recent": ("float", "s", "feature", "other drivers, ended <= end of lap t", f"Median of other drivers' green laps that ended in the last {int(FIELD_WINDOW_S)} s."),
    "rel_pace_to_field": ("float", "s", "feature", "derived", "roll_mean_green_3 minus field_green_median_recent."),
    "is_rt_green": ("bool", "", "feature", "real-time flags of lap t", "Lap t had no real-time exclusion flag (pit, SC/VSC/red, yellow, restart, wet, rain). Used for lap sequences."),
    "y_next_lap_time_s": ("float", "s", "target", "own lap t+1", "Lap time of lap t+1."),
    "target_lap_number": ("float", "lap", "target", "own lap t+1", "Lap number of the target lap."),
    "target_valid": ("bool", "", "target", "lap t+1 flags", "Target is the next lap, same stint, and a clean green lap."),
    "target_valid_strict": ("bool", "", "target", "lap t+1 flags", "target_valid and lap t+1 is not a pace outlier. Sensitivity sample."),
}


def all_columns() -> dict:
    return {**CLEAN, **FEATURES}


def write_docs() -> str:
    lines = ["# Data dictionary", "",
             "Generated by `python -m pipelines dictionary` from `pipelines/schema.py`. Do not edit by hand.",
             "", "Kinds: **raw** (as delivered by the source), **derived** (computed, no model), "
             "**flag** (quality or exclusion marker), **feature** (model input, leakage-checked), "
             "**target** (model output to predict).", ""]
    for title, table in (("Clean lap table (`laps_clean.parquet`)", CLEAN),
                         ("Next-lap feature table (`features_next_lap.parquet`)", FEATURES)):
        lines += [f"## {title}", "", "| column | type | unit | kind | origin | description |",
                  "|---|---|---|---|---|---|"]
        for c, (t, u, k, o, d) in table.items():
            lines.append(f"| `{c}` | {t} | {u} | {k} | {o} | {d} |")
        lines.append("")
    lines.append("The feature table also repeats these clean-table columns as IDs or features: "
                 "race_id, season, round, event_name, regulation_era, driver, team, lap_number, "
                     "stint, compound_relative, tyre_life, fresh_tyre, scheduled_laps, "
                     "position_end_of_lap, grid_position, flag_sc, flag_vsc, flag_yellow, "
                     "flag_post_neutralisation, track_temp_c, air_temp_c, humidity_pct.")
    path = config.ROOT / "docs" / "data_dictionary.md"
    path.write_text("\n".join(lines) + "\n")
    schemas = {c: {"type": t, "unit": u, "kind": k, "origin": o, "description": d}
               for c, (t, u, k, o, d) in all_columns().items()}
    config.SCHEMAS.mkdir(parents=True, exist_ok=True)
    (config.SCHEMAS / "columns.json").write_text(json.dumps(schemas, indent=2, ensure_ascii=False))
    return str(path)
