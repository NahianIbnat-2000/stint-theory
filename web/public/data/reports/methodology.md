# Methodology (Phase 1: data)

Status: the pipeline is written and tested on a synthetic fixture and fake OpenF1 responses. No real race data
has been processed yet, so this document describes rules, not results. Coverage
numbers will appear in `data/reports/coverage_report.md` after the first ingest run.

## 1. Source and sample

- Source: the OpenF1 historical API (https://openf1.org), free tier, no login.
  OpenF1 states that historical data from 2023 onward is free and needs no
  authentication. Endpoints used per race: laps, stints, drivers, pit, position,
  race_control, weather, starting_grid, session_result.
- Why not FastF1: since mid-October 2026 Formula 1's live-timing archive, which
  FastF1 reads, requires a paid F1 TV subscription (FastF1 issue #978, release
  3.9.0). That conflicts with the project's zero-cost rule, so FastF1 is not used.
- Sessions: Grand Prix races only (`session_name == "Race"`). Sprints are excluded.
- Seasons: 2023, 2024, 2025. One technical-rules era (2022 to 2025 ground-effect
  cars). There is no cross-era test in this sample.
- 2026 is held out: new cars, power units and tyres make it a different era.
- `round` is the order of races held in that season by start date. It can differ
  from the official round if a cancelled event kept its number.
- Every OpenF1 response is cached as JSON (`.cache/openf1/`) with its URL and
  retrieval time, so the dataset can be rebuilt offline.

## 2. Unit of observation

One row in `laps_clean.parquet` is one driver-lap in one race. Keys:
`race_id` (season_round), `driver`, `lap_number`. Stints are `(race_id, driver, stint)`.

## 3. Rebuilding FastF1-style fields from OpenF1 (`pipelines/openf1.py`)

OpenF1 delivers some facts differently. Each conversion is a rule, is tested
against a race with known structure, and leaves counts in `session_meta.json`
(`checks`) that the coverage report sums by season.

| field | OpenF1 source | rule | audit count |
|---|---|---|---|
| session clock | `sessions.date_start` | seconds since scheduled race start | `laps_missing_start_time` |
| lap end | `laps.date_start + lap_duration` | next lap start if duration missing | |
| stint, compound | `stints.lap_start..lap_end` | assigned by lap range; a lap right after the driver's last stint end is attached to that stint | `laps_without_stint`, `laps_stint_extended_by_one` |
| tyre life | `stints.tyre_age_at_start` | age at start + laps into stint + 1 | |
| out-lap | `laps.is_pit_out_lap` | as given | `pit_rows_on_out_lap` |
| in-lap | none | the lap before an out-lap | `pit_rows_on_inferred_in_lap` vs `pit_table_rows` |
| track status | `race_control` messages | see below | `sc_unpaired`, `vsc_unpaired`, `red_unpaired`, `yellow_capped`, `safetycar_msgs_unmatched` |
| deleted lap | `race_control` message text | "CAR n ... DELETED ... LAP k", undone by "REINSTATED" | `deleted_laps` |
| position | `position` | latest at or before lap end | |
| grid | `starting_grid.position`; if empty, each driver's first `position` record | `grid_source` in session meta | `starting_grid_rows` |
| race distance | reference file, else `session_result` | see section 3b | `scheduled_laps_source` |

**Track status.** OpenF1 has no per-lap status code, so periods are rebuilt from
race-control messages:
- safety car: "SAFETY CAR DEPLOYED" until "SAFETY CAR IN THIS LAP" (or "... ENDING"),
- VSC: "VIRTUAL SAFETY CAR DEPLOYED" until "VIRTUAL SAFETY CAR ENDING",
- red flag: track-wide RED until the next track-wide GREEN or CLEAR, or until a
  new "SAFETY CAR DEPLOYED" (restart behind the safety car). A red flag closes any
  running SC or VSC period,
- yellow: a sector YELLOW or DOUBLE YELLOW until CLEAR in that sector (or a
  track-wide clear), capped at 300 s.
- a safety car deployment ends a running VSC (VSC upgraded to SC),
- a restart behind the safety car ("RACE WILL START/RESUME BEHIND THE SAFETY CAR",
  "ROLLING START PROCEDURE", "SAFETY CAR WILL STAY OUT") opens a safety-car period
  and ends a red flag; "SAFETY CAR WILL ENTER PITS" or "ROLLING START" ends it,
- the chequered flag ends every running period, and nothing opens after it.
Each rule comes from a race in the 2023 to 2025 sample where the simpler rules
failed (listed in `pipelines/openf1.py`), and each has a test.
A lap gets a code when its time window overlaps the period. A start without an end
runs to the end of the session and is counted. Safety-car messages that match no
rule are counted, so wording changes in real data show up in the report. These
periods use only messages sent up to that moment, so they are known in real time.

**3b. Race distance.** OpenF1 does not give the planned number of laps. The
pipeline uses `data/reference/scheduled_laps.csv` where a row has been checked by
hand; otherwise it uses the winner's lap count. That equals the actual distance,
which is wrong for shortened races and leaks a little end-of-race information into
`race_progress` and `laps_remaining_sched`. Races where it matters should be added
to the reference file. Laps numbered above the race distance get
`flag_beyond_scheduled` and leave the clean sample; this is a warning, not a reason
to drop the race. `python -m pipelines diagnose` lists them per race.

## 4. Validation (`pipelines/validate.py`)

A race enters the sample only if it has no `error`-level issue: missing required
columns, duplicate driver-laps, invalid lap numbers, non-positive lap times, stint
counters going backwards, missing track status, or more laps than scheduled.
Warnings (sector sums that disagree with lap time by over 0.1 s, tyre-life steps
other than one lap, unknown compounds, missing weather) keep the race in, and the
rows are flagged. Every issue is written to `data/reports/validation_issues.csv`.

## 5. Cleaning rules (`pipelines/clean.py`)

No row is deleted. Each rule sets a flag; `is_clean_green` is true when no
exclusion flag is set. Analyses must say which flags they apply.

| flag | rule | known in real time? |
|---|---|---|
| `flag_first_lap` | lap 1 (standing start) | yes |
| `flag_pit_in` / `flag_pit_out` | in-lap / out-lap (section 3) | yes |
| `flag_sc`, `flag_vsc`, `flag_red`, `flag_yellow` | status code 4, 6 or 7, 5, 2 seen during the lap | yes |
| `flag_post_neutralisation` | previous lap had SC, VSC or red flag (restart lap) | yes |
| `flag_non_slick` | compound not a slick, or unknown | yes |
| `flag_rain` | rainfall at the latest weather sample before lap start | yes |
| `flag_missing_time` | no lap time | yes |
| `flag_deleted` | lap deleted by race control | no, decided later |
| `flag_not_accurate` | always false with OpenF1 (no such field) | n/a |
| `flag_fastf1_generated` | always false with OpenF1 | n/a |
| `flag_beyond_scheduled` | lap number above the race distance | yes, once the distance is known |
| `flag_pace_outlier` | robust z-score above 4 of the residual from a Theil-Sen line on lap number within driver-stint (MAD of residuals, at least 5 usable laps). Laps already excluded for another reason are left out of the fit. Detrending measures spread from lap-to-lap noise rather than from the wear trend. A sudden tyre "cliff" can still be flagged, which would bias tyre-age slopes toward zero, so the coverage report shows the flag rate by tyre age to check this | no, uses the whole stint |

`flag_pace_outlier` is not part of `is_clean_green`. On the 2023 to 2025 data, among
laps with no other flag, it hit 6 to 9% of laps in the first five laps of a stint,
about 2.5 to 3% in mid-stint, and 3.6 to 4.5% past 30 laps. A flag tied to tyre age
would bias the very relationship under study, and slow laps in traffic are real
laps a forecaster has to predict. It is kept as `is_clean_green_strict`, a
sensitivity sample. The outlier cut-off (4) is itself a sensitivity parameter. Results should be repeated at
other values (for example 3 and 6) and with the flag turned off. Slow laps caused
by traffic are real racing data and are not removed by any fixed threshold.

Yellow-flag laps are excluded from `is_clean_green` by default. A local yellow may
cost little time, so the coverage report shows how many laps this removes, and
models should be checked with yellow laps included.

## 6. Compounds

OpenF1 reports SOFT, MEDIUM or HARD relative to the three compounds Pirelli
brought to that race (plus INTERMEDIATE and WET). The mapper also handles 2018
named compounds, which does not apply to this sample.

The relative label hides real differences: a 2023 "SOFT" at one race can be a
harder compound than "SOFT" at another. Models should include circuit effects.

## 7. Information rule for features (`pipelines/features.py`)

Prediction origin: the end of lap t for one driver. Target: the driver's lap t+1
time. A feature may use only:

1. the driver's own laps 1..t,
2. other drivers' laps that ended at or before the end of lap t on the session clock,
3. weather samples at or before the start of lap t,
4. facts fixed before the start (grid position, scheduled laps, circuit, season).

Pace features (`last_green_lt`, `roll_mean_green_3`, `roll_std_green_5`,
`trend_slope_green_5`) use only laps that are green by the real-time flags above,
within the current stint. Hindsight flags never enter features.

`tests/test_leakage.py` changes every lap and weather sample after the origin, then
checks that no feature at the origin changes. A second test plants a deliberate leak
and checks that the first test catches it.

## 8. Target definition

`target_valid` is true when lap t+1 is the next lap, on the same stint, and is a
clean green lap. So the forecast is conditional on the driver staying out, which is
how a strategist uses it. Scoring only clean targets uses hindsight flags. That is
acceptable for choosing the evaluation sample, but it means reported errors apply
to normal green-flag laps, not to every lap.

## 9. Why lap time is not tyre wear

Lap time within a stint changes for many reasons at once:

- fuel burn (the car gets lighter, about one lap's worth per lap),
- track evolution (rubber laid down),
- traffic and dirty air,
- driver management (lifting and coasting, saving tyres, managing gaps),
- changing weather and track temperature,
- car setup and damage.

Within a single stint, tyre age and fuel load both rise by one per lap, so they
cannot be separated from that stint alone. The planned identification uses
differences across drivers on the same race lap: drivers who pitted at different
times run different tyre ages under the same fuel-burn and track conditions, and
race-lap fixed effects absorb the common part. This has a known weakness. Pit
timing is chosen, often because tyres are fading, so long stints are more likely
from cars whose tyres held up. That biases tyre-age slopes toward zero. Any
"degradation" estimate on the site will be labelled as estimated pace change linked
to tyre age, never as measured wear.

## 10. Not yet implemented

Multi-lap forecasting targets, model training, evaluation splits, the strategy
simulator and the website. These are Phases 2 to 5.
