# Model change log

Every change to data rules, features, models or grids made after looking at
development results is recorded here, with the result that prompted it. The
2025 R13-24 test set has not been loaded for any of these decisions.

## Run 1: development results (grid version 1), 2026-11-23

Source: `research/results/phase2_dev/report.md` from the first full run.
9,115 scored laps, 12 races (2025 R1-12). Race-clustered 95% intervals.

| model | MAE (s) | 95% CI | skill vs persistence | skill 95% CI |
|---|---|---|---|---|
| random_forest | 0.380 | 0.313-0.479 | 0.095 | 0.062-0.135 |
| xgboost | 0.391 | 0.327-0.488 | 0.070 | 0.023-0.121 |
| ridge | 0.413 | 0.341-0.513 | 0.016 | -0.046-0.074 |
| compound_drift | 0.420 | 0.350-0.515 | 0.000 | -0.003-0.003 |
| persistence | 0.420 | 0.350-0.516 | 0 | - |
| mixed_effects | 0.430 | 0.360-0.534 | -0.024 | -0.070-0.022 |

Random forest minus XGBoost MAE: interval 0.003 to 0.022 s in favour of random
forest; random forest lower in 8 of 12 races.

## Changes after run 1

1. **Lap completeness check (data).** Miami 2025 had about 559 lap rows where
   about 1,100 laps were driven. Races where lap rows cover less than 90% of the
   laps in the classification are now excluded (`validate.lap_completeness`). The
   threshold was set before seeing which other races it removes.
2. **Wider grids (grid version 2).** Every v1 choice was on a grid edge: ridge
   alpha 1000 (largest), random forest leaf 50 (largest), XGBoost depth 3, 300
   trees and child weight 20 (all on edges). Grids were extended past those edges.
3. **Robust loss option for XGBoost.** Errors are heavy-tailed (RMSE about twice
   MAE). XGBoost may now choose pseudo-Huber loss (slope 0.5 s) instead of
   squared error; the choice is made on the 2024 tuning blocks like any other
   setting.

## Run 2: development results (grid version 2), 2026-11-23

8,727 scored laps, 11 races (Miami 2025 excluded: 55.8% of laps present).

| model | MAE (s) | 95% CI | skill vs persistence | skill 95% CI |
|---|---|---|---|---|
| xgboost | 0.385 | 0.317-0.494 | 0.095 | 0.041-0.153 |
| random_forest | 0.385 | 0.315-0.492 | 0.093 | 0.059-0.135 |
| ridge | 0.403 | 0.330-0.513 | 0.051 | 0.012-0.096 |
| compound_drift | 0.425 | 0.353-0.529 | 0.000 | -0.003-0.004 |
| persistence | 0.425 | 0.353-0.530 | 0 | - |
| mixed_effects | 0.434 | 0.360-0.549 | -0.021 | -0.064-0.027 |

XGBoost minus random forest: interval -0.012 to 0.016 s; no difference. The run 1
ordering (random forest ahead of XGBoost) did not survive wider tuning.
Chosen: ridge alpha 1e4; random forest leaf 50, max_features 1.0; XGBoost depth 4,
300 trees, child weight 100, pseudo-Huber loss.

## Changes after run 2

4. **XGBoost grid version 3.** Depth 4 and child weight 100 were upper edges, so
   the grid is now depth 3-6 and child weight 50-400. Pseudo-Huber loss, chosen
   by the v2 tuning, is fixed. Random forest `max_features=1.0` is the largest
   possible value, so it is not treated as an edge. Ridge and random forest grids
   unchanged. After this run the Phase 2 configuration is frozen.

## Run 3: development results (grid version 3), 2026-11-23. Phase 2 frozen.

| model | MAE (s) | 95% CI | skill vs persistence | skill 95% CI |
|---|---|---|---|---|
| xgboost | 0.382 | 0.314-0.492 | 0.101 | 0.057-0.153 |
| random_forest | 0.385 | 0.315-0.492 | 0.093 | 0.059-0.135 |
| ridge | 0.403 | 0.330-0.513 | 0.051 | 0.012-0.096 |
| persistence | 0.425 | 0.353-0.530 | 0 | - |
| mixed_effects | 0.434 | 0.360-0.549 | -0.021 | -0.064-0.027 |

XGBoost chose depth 6 and 150 trees (both edges), but its tuning MAE (0.384 s)
equals the v2 choice (depth 4, 300 trees) to three decimals: deeper trees with
fewer rounds fit the same as shallower trees with more rounds. The tuning surface
is flat here, so the grid is not extended again. Ridge is now clearly behind
XGBoost (difference interval 0.006 to 0.035 s); XGBoost and random forest remain
tied (-0.008 to 0.012 s).

**Freeze.** From here the Phase 2 models, grids and settings do not change. Phase 3
models are compared against these Phase 2 predictions on the same laps.

## Phase 3 development run, 2026-11-24. Phase 3 frozen.

Same 8,727 laps, 11 races. Neural models: mean of 5 seeds.

| model | MAE (s) | 95% CI | skill vs persistence |
|---|---|---|---|
| tcn | 0.377 | 0.310-0.482 | 0.113 |
| lstm | 0.378 | 0.308-0.486 | 0.111 |
| mlp | 0.380 | 0.311-0.491 | 0.106 |
| xgboost | 0.382 | 0.314-0.492 | 0.101 |
| random_forest | 0.385 | 0.315-0.492 | 0.093 |

TCN minus XGBoost: -0.010 to -0.000 s (borderline, single comparison of six, and
five-seed ensemble against a single XGBoost). LSTM/TCN minus MLP: no difference.
Single-seed TCN mean 0.3795 s (sd 0.0024). Chosen: mlp hidden 64 / dropout 0.3,
lstm 32 / 0.3, tcn 64 / 0.3.

## Before the final test

5. **xgboost_ens5 control.** Mean of five XGBoost fits (frozen settings, seeds 0-4),
   added so the five-seed neural ensembles are compared like for like. Not run on
   development races.
6. **Pre-registration** (`docs/preregistration.md`): primary comparisons, Holm
   correction, 0.01 s practical margin, decision labels, secondary analyses, one-run
   rule. Written after all development runs and before the test set was opened.

## Task 1 final test, 2026-11-24 (pre-registered, one run)

All five primary comparisons equivalent within the 0.01 s margin (90% intervals
inside ±0.005 s). Development hint "TCN beats XGBoost" did not replicate
(+0.0004 s). Secondary S1 (tyres > 30 laps) went the other way: TCN 0.009 s worse
than xgboost_ens5 (interval 0.003-0.015, uncorrected). Full report:
`research/results/final_test/report.md`.

## Task 2 development run, 2026-11-24

Settings carried over from Task 1. 9,064 origins, 11 races. XGBoost skill vs
persistence rises from 0.066 (h=1) to 0.16-0.17 (h=5-10). LSTM minus XGBoost
negative at every horizon (-0.005 to -0.017 s) but intervals include zero from
h=2 on. 10-lap total MAE: xgboost_direct 3.72 s, lstm_multi 3.73 s, mlp_multi
4.01 s, persistence 4.84 s. Known weakness: stacked XGBoost at h=1 is 0.397 s vs
0.382 s for the dedicated Task 1 model; not changed.

7. **Task 2 pre-registration** (`docs/preregistration_task2.md`) written after
   this run and before Task 2 was run on the test races.

Not changed: the split, the reference pace, the features, the scored sample and
the evaluation method.
