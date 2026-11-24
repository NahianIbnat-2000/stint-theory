# Pre-registration: final test of multi-lap stint forecasts (Task 2)

Written 2026-11-24, after the Task 2 development run and before Task 2 was run on
the test races. Commit this file to git **before** running
`python -m models horizon-test`. The runner records its SHA-256 and the git commit.

## 1. Test set and what was already seen

2025 rounds 13-24, the races used in the Task 1 final test. Task 1 scored
next-lap forecasts only; no multi-lap forecast has been made or scored on these
races. Feature definitions and data rules are unchanged since Task 1.

## 2. Protocol

As in development: each test race forecast by models trained on every earlier
race. Origins and scored (origin, horizon) pairs as defined in
`docs/methodology_models.md` (Task 2). Settings frozen: XGBoost from
`research/results/phase2_dev/tuning.json`, networks from
`research/results/phase3_dev/tuning.json`; neural models are the mean of 3 seeds.
No model, setting or rule changes after the development run, including the known
weakness of the stacked XGBoost at horizon 1 (0.397 s vs 0.382 s for the
dedicated Task 1 model in development).

Models: persistence, compound_drift, trend_extrapolation, xgboost_direct,
mlp_multi, lstm_multi.

## 3. Primary metric

Absolute error of the **total time of the next 10 laps**, on origins where all ten
laps are scored. Differences are MAE(A) minus MAE(B) in seconds; negative means A
is more accurate. Race-clustered bootstrap, 2,000 resamples, seed 7.

## 4. Primary comparisons and decision rule

Three comparisons, Holm correction at family-wise 5%:

| # | comparison | question |
|---|---|---|
| Q1 | xgboost_direct vs persistence | Do models beat repeating the last lap over a 10-lap stint segment? |
| Q2 | lstm_multi vs xgboost_direct | Does deep learning beat boosted trees on stint forecasts? |
| Q3 | lstm_multi vs mlp_multi | Does the lap sequence add information for stint forecasts? |

Practical margin: **0.1 s on the 10-lap total** (Task 1's 0.01 s per lap times
ten). Labels exactly as in `docs/preregistration.md` section 4: meaningful
difference (Holm p < 0.05 and 95% interval entirely beyond ±0.1 s), equivalent
(90% interval entirely within ±0.1 s), statistically different with size unclear,
or inconclusive.

## 5. Secondary analyses (no multiplicity correction)

- MAE by horizon 1-10 for every model; XGBoost skill by horizon with intervals.
- lstm_multi vs mlp_multi and lstm_multi vs xgboost_direct at horizons 5 and 10.
- Correlation of a model's errors across the ten laps of an origin (mean pairwise
  correlation of per-lap errors), as input to the simulator's uncertainty model.

## 6. Commitments

One run; rerun only after a logged crash with unchanged code. Every number is
published. Anything else done on these results is labelled post hoc.
