# Phase 2: next-lap prediction on the development races

Generated 2026-11-23T21:21:40+00:00. Development sample: 2025 rounds 1-12, predicted one race at a time from every earlier race. The 2025 R13-24 test set was not loaded. These are development results, not final test results.

- Scored laps: 8727 from 11 races. Every model predicts exactly the same laps.

- Benchmark: `persistence` = last green lap of the stint (or recent field median).

- Intervals: 95%, race-clustered bootstrap (2000 resamples of 11 races). With this few races the intervals are approximate and tend to be too narrow; read them as a guide.

## Accuracy (default clean sample)

Skill = 1 - MAE / MAE of persistence. Positive means better than repeating the last lap.

| model | n | mae | mae_ci_low | mae_ci_high | rmse | median_ae | bias | skill_vs_persistence | skill_ci_low | skill_ci_high |
|---|---|---|---|---|---|---|---|---|---|---|
| xgboost | 8727 | 0.382 | 0.314 | 0.492 | 0.766 | 0.234 | -0.012 | 0.101 | 0.057 | 0.153 |
| random_forest | 8727 | 0.385 | 0.315 | 0.492 | 0.763 | 0.241 | 0.022 | 0.093 | 0.059 | 0.135 |
| ridge | 8727 | 0.403 | 0.33 | 0.513 | 0.778 | 0.258 | 0.029 | 0.051 | 0.012 | 0.096 |
| compound_drift | 8727 | 0.425 | 0.353 | 0.529 | 0.83 | 0.237 | 0.01 | 0.0 | -0.003 | 0.004 |
| persistence | 8727 | 0.425 | 0.353 | 0.53 | 0.831 | 0.237 | 0.036 | 0.0 | 0.0 | 0.0 |
| mixed_effects | 8727 | 0.434 | 0.36 | 0.549 | 0.809 | 0.282 | 0.03 | -0.021 | -0.064 | 0.027 |

## Is the lowest-MAE model (xgboost) clearly better?

A model is clearly worse only if the whole interval for its MAE difference is above zero. Overlapping intervals mean the data cannot separate the two models.

| model | MAE minus xgboost (s), 95% CI low | CI high | clearly worse | races where better |
|---|---|---|---|---|
| persistence | 0.024 | 0.062 | True | 1/11 |
| compound_drift | 0.023 | 0.062 | True | 1/11 |
| ridge | 0.006 | 0.035 | True | 1/11 |
| mixed_effects | 0.043 | 0.061 | True | 0/11 |
| random_forest | -0.008 | 0.012 | False | 3/11 |

## Sensitivity: strict sample (pace outliers removed from the targets)

Same predictions, scored only on targets that are not pace outliers.

| model | n | mae | rmse | skill_vs_persistence |
|---|---|---|---|---|
| xgboost | 8479 | 0.352 | 0.72 | 0.114 |
| random_forest | 8479 | 0.357 | 0.72 | 0.101 |
| ridge | 8479 | 0.376 | 0.736 | 0.054 |
| compound_drift | 8479 | 0.397 | 0.788 | 0.002 |
| persistence | 8479 | 0.397 | 0.79 | 0.0 |
| mixed_effects | 8479 | 0.407 | 0.767 | -0.024 |

## MAE by tyre age of the predicted lap (s)

| tyre_age_bin | n | persistence | compound_drift | ridge | mixed_effects | random_forest | xgboost |
|---|---|---|---|---|---|---|---|
| (0, 5] | 1066 | 0.656 | 0.651 | 0.519 | 0.568 | 0.502 | 0.488 |
| (5, 10] | 1990 | 0.381 | 0.381 | 0.373 | 0.376 | 0.354 | 0.346 |
| (10, 15] | 1878 | 0.379 | 0.38 | 0.364 | 0.386 | 0.348 | 0.35 |
| (15, 20] | 1350 | 0.37 | 0.371 | 0.364 | 0.401 | 0.351 | 0.355 |
| (20, 30] | 1637 | 0.391 | 0.392 | 0.389 | 0.443 | 0.368 | 0.373 |
| (30, 80] | 806 | 0.495 | 0.494 | 0.512 | 0.548 | 0.488 | 0.47 |

## MAE by compound (s)

| compound_relative | n | persistence | compound_drift | ridge | mixed_effects | random_forest | xgboost |
|---|---|---|---|---|---|---|---|
| HARD | 4644 | 0.405 | 0.404 | 0.393 | 0.424 | 0.374 | 0.37 |
| MEDIUM | 3223 | 0.437 | 0.438 | 0.41 | 0.441 | 0.393 | 0.392 |
| SOFT | 860 | 0.484 | 0.487 | 0.432 | 0.457 | 0.417 | 0.408 |

## MAE by race (s)

| race_id | n | persistence | compound_drift | ridge | mixed_effects | random_forest | xgboost |
|---|---|---|---|---|---|---|---|
| 2025_01 | 31 | 1.134 | 1.119 | 1.181 | 1.226 | 1.104 | 1.048 |
| 2025_02 | 936 | 0.384 | 0.384 | 0.413 | 0.436 | 0.375 | 0.37 |
| 2025_03 | 970 | 0.273 | 0.27 | 0.259 | 0.323 | 0.251 | 0.289 |
| 2025_04 | 900 | 0.392 | 0.397 | 0.334 | 0.389 | 0.325 | 0.316 |
| 2025_05 | 762 | 0.342 | 0.341 | 0.327 | 0.343 | 0.301 | 0.292 |
| 2025_07 | 872 | 0.383 | 0.383 | 0.346 | 0.372 | 0.344 | 0.333 |
| 2025_08 | 1125 | 0.734 | 0.732 | 0.729 | 0.781 | 0.714 | 0.714 |
| 2025_09 | 930 | 0.451 | 0.453 | 0.399 | 0.427 | 0.383 | 0.374 |
| 2025_10 | 1135 | 0.348 | 0.346 | 0.346 | 0.338 | 0.321 | 0.301 |
| 2025_11 | 952 | 0.364 | 0.364 | 0.318 | 0.346 | 0.302 | 0.298 |
| 2025_12 | 114 | 1.021 | 1.011 | 0.928 | 0.893 | 0.882 | 0.884 |

## Chosen hyperparameters (tuned on 2024 only, grid version 3)

Persistence MAE on the same 2024 blocks: 0.438 s. A choice on the edge of its grid means a better value may lie outside it.

| model | params | tuning MAE | tuning skill | on grid edge |
|---|---|---|---|---|
| ridge | {"alpha": 10000.0} | 0.416 | 0.049 | no |
| random_forest | {"min_samples_leaf": 50, "max_features": 1.0} | 0.391 | 0.106 | no |
| xgboost | {"max_depth": 6, "n_estimators": 150, "min_child_weight": 100, "objective": "reg:pseudohubererror"} | 0.384 | 0.122 | max_depth=6, n_estimators=150 |

## Compute (summed over all development folds, this machine)

| model | fit_s | predict_s |
|---|---|---|
| persistence | 0.01 | 0.0 |
| compound_drift | 0.08 | 0.02 |
| ridge | 4.27 | 0.11 |
| mixed_effects | 30.62 | 0.26 |
| random_forest | 191.85 | 0.64 |
| xgboost | 11.92 | 0.21 |

Mixed model converged on 10 of 11 folds; random-effect structure used: {'intercept_and_slope': 11}.
