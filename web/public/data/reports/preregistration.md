# Pre-registration: final test of next-lap prediction models

Written 2026-11-24, after all development runs and before the test set was opened.
Commit this file to git **before** running `python -m models test`. The test
runner records this file's SHA-256 hash and the git commit it ran on, so anyone
can check the rules below were fixed in advance.

## 1. Test set

2025 rounds 13 to 24 (the order of races held, as in `data/manifests/ingest_2025.json`).
Locked in code since Phase 2 (`models/data.py`); never loaded during development
(`data/reports/test_access.log` should have no entry before the final run).
Races are excluded only by the data rules already in place (lap completeness under
90%), decided by `python -m pipelines build`, not by looking at results.

## 2. Protocol

Identical to development: each test race is predicted by models trained on every
earlier race (2023, 2024, 2025 rounds 1-12, and earlier test races). Scored laps are
`target_valid` laps with a reference pace. Hyperparameters are the frozen ones:
`research/results/phase2_dev/tuning.json` and `research/results/phase3_dev/tuning.json`.
No refitting of hyperparameters on the test set. Neural models: 5 seeds per race,
prediction = mean of the 5.

Models scored: persistence, compound_drift, ridge, mixed_effects, random_forest,
xgboost, xgboost_ens5, mlp, lstm, tcn.

`xgboost_ens5` (new, added here) is the mean of 5 XGBoost fits with the frozen
settings and seeds 0-4. It is the like-for-like comparator for the 5-seed neural
ensembles. It was not run on the development races.

## 3. Metric

Mean absolute error of the next-lap time (seconds), on the default clean sample.
Differences are MAE(model A) minus MAE(model B); negative means A is more accurate.
Uncertainty: race-clustered bootstrap, 2,000 resamples, seed 7.

## 4. Primary comparisons and decision rule

Five comparisons, tested together with Holm correction at family-wise 5%:

| # | comparison | question |
|---|---|---|
| P1 | tcn vs xgboost_ens5 | Does a temporal CNN beat boosted trees? |
| P2 | lstm vs xgboost_ens5 | Does an LSTM beat boosted trees? |
| P3 | mlp vs xgboost_ens5 | Does a neural net beat trees on identical inputs? |
| P4 | lstm vs mlp | Does the raw lap sequence add information (LSTM)? |
| P5 | tcn vs mlp | Does the raw lap sequence add information (TCN)? |

Practical margin: **0.01 s of MAE** (about 2.5% of the development MAE). Each
comparison gets exactly one label:

1. **meaningful difference**: Holm-adjusted p < 0.05 and the 95% interval lies
   entirely beyond ±0.01 s.
2. **equivalent**: the 90% interval lies entirely within ±0.01 s (two one-sided
   tests at 5%). If also Holm p < 0.05: "equivalent (statistically different,
   within margin)".
3. **statistically different, size unclear**: Holm p < 0.05, neither of the above.
4. **inconclusive**: none of the above.

p-values are two-sided bootstrap p-values (twice the share of resamples on the
other side of zero).

## 5. What would answer the research question

- Deep learning "improves" next-lap forecasting only if P1 or P2 is a **meaningful
  difference** in favour of the neural model.
- The lap sequence "adds information" only if P4 or P5 is a meaningful difference
  in favour of the sequence model.
- If P1-P3 are equivalent or inconclusive, the conclusion is that deep learning does
  not measurably improve on boosted trees for this task, and that is the headline.

## 6. Secondary analyses (reported, no multiplicity correction, not headline)

- S1. On tyres older than 30 laps: lstm and tcn vs xgboost_ens5 (the development
  hint was 0.462 vs 0.470 s against single XGBoost).
- S2. Single-seed neural models vs single xgboost (mean, spread, range over seeds).
- S3. All models vs persistence: skill with intervals.
- S4. Strict sample (pace outliers removed).
- S5. Single xgboost vs xgboost_ens5 (how much seed averaging alone is worth).
- S6. Training and prediction time.

## 7. Commitments

- One run. If the run crashes, it is rerun with unchanged code and settings; the
  crash and its cause are logged in `docs/model_changes.md`.
- Every number in the final report is published, including results that contradict
  the development findings.
- No model, feature, sample rule or hyperparameter is changed after the test set is
  opened. Any later exploratory analysis on the test set is labelled post hoc.
