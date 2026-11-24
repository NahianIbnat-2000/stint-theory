# Phase 3: neural models on the development races

Generated 2026-11-23T22:39:03+00:00. Same scored laps, folds and tuning blocks as Phase 2; the Phase 2 models are the frozen run. The 2025 R13-24 test set was not loaded. Development results, not final test results.

- Scored laps: 8727 from 11 races.

- Neural predictions are the mean of 5 seeds; single-seed spread is shown below.

- Intervals: 95% race-clustered bootstrap; approximate with this few races.

## Accuracy, all models (default clean sample)

| model | n | mae | mae_ci_low | mae_ci_high | rmse | median_ae | bias | skill_vs_persistence | skill_ci_low | skill_ci_high |
|---|---|---|---|---|---|---|---|---|---|---|
| tcn | 8727 | 0.377 | 0.31 | 0.482 | 0.756 | 0.231 | -0.034 | 0.113 | 0.075 | 0.157 |
| lstm | 8727 | 0.378 | 0.308 | 0.486 | 0.76 | 0.231 | -0.03 | 0.111 | 0.072 | 0.156 |
| mlp | 8727 | 0.38 | 0.311 | 0.491 | 0.763 | 0.232 | -0.028 | 0.106 | 0.063 | 0.158 |
| xgboost | 8727 | 0.382 | 0.314 | 0.492 | 0.766 | 0.234 | -0.012 | 0.101 | 0.057 | 0.153 |
| random_forest | 8727 | 0.385 | 0.315 | 0.492 | 0.763 | 0.241 | 0.022 | 0.093 | 0.059 | 0.135 |
| ridge | 8727 | 0.403 | 0.33 | 0.513 | 0.778 | 0.258 | 0.029 | 0.051 | 0.012 | 0.096 |
| compound_drift | 8727 | 0.425 | 0.353 | 0.529 | 0.83 | 0.237 | 0.01 | 0.0 | -0.003 | 0.004 |
| persistence | 8727 | 0.425 | 0.353 | 0.53 | 0.831 | 0.237 | 0.036 | 0.0 | 0.0 | 0.0 |
| mixed_effects | 8727 | 0.434 | 0.36 | 0.549 | 0.809 | 0.282 | 0.03 | -0.021 | -0.064 | 0.027 |

## Key comparisons

Neural models against XGBoost, then the temporal-history ablation: LSTM and TCN see the lap sequence, the MLP does not; all three see the same tabular inputs.

| comparison | MAE diff CI low (s) | CI high | verdict | races a better |
|---|---|---|---|---|
| mlp minus xgboost | -0.009 | 0.002 | no clear difference | 7/11 |
| lstm minus xgboost | -0.013 | 0.002 | no clear difference | 6/11 |
| tcn minus xgboost | -0.01 | -0.0 | tcn better | 7/11 |
| lstm minus mlp | -0.006 | 0.003 | no clear difference | 6/11 |
| tcn minus mlp | -0.008 | 0.002 | no clear difference | 6/11 |
| lstm minus tcn | -0.004 | 0.005 | no clear difference | 5/11 |

## Seed variability (single seeds, not the ensemble)

| model | seeds | mae_mean | mae_sd | mae_min | mae_max | skill_mean | ensemble_mae |
|---|---|---|---|---|---|---|---|
| mlp | 5 | 0.3819 | 0.0025 | 0.3785 | 0.3855 | 0.1012 | 0.3798 |
| lstm | 5 | 0.3799 | 0.003 | 0.3758 | 0.3838 | 0.1059 | 0.3778 |
| tcn | 5 | 0.3795 | 0.0024 | 0.3765 | 0.3819 | 0.1068 | 0.377 |

## Sensitivity: strict sample

| model | n | mae | rmse | skill_vs_persistence |
|---|---|---|---|---|
| tcn | 8479 | 0.347 | 0.71 | 0.126 |
| lstm | 8479 | 0.348 | 0.714 | 0.124 |
| mlp | 8479 | 0.351 | 0.719 | 0.117 |
| xgboost | 8479 | 0.352 | 0.72 | 0.114 |
| random_forest | 8479 | 0.357 | 0.72 | 0.101 |
| ridge | 8479 | 0.376 | 0.736 | 0.054 |
| compound_drift | 8479 | 0.397 | 0.788 | 0.002 |
| persistence | 8479 | 0.397 | 0.79 | 0.0 |
| mixed_effects | 8479 | 0.407 | 0.767 | -0.024 |

## MAE by tyre age of the predicted lap (s)

| tyre_age_bin | n | persistence | compound_drift | ridge | mixed_effects | random_forest | xgboost | mlp | lstm | tcn |
|---|---|---|---|---|---|---|---|---|---|---|
| (0, 5] | 1066 | 0.656 | 0.651 | 0.519 | 0.568 | 0.502 | 0.488 | 0.485 | 0.474 | 0.471 |
| (5, 10] | 1990 | 0.381 | 0.381 | 0.373 | 0.376 | 0.354 | 0.346 | 0.346 | 0.347 | 0.347 |
| (10, 15] | 1878 | 0.379 | 0.38 | 0.364 | 0.386 | 0.348 | 0.35 | 0.348 | 0.348 | 0.344 |
| (15, 20] | 1350 | 0.37 | 0.371 | 0.364 | 0.401 | 0.351 | 0.355 | 0.352 | 0.35 | 0.354 |
| (20, 30] | 1637 | 0.391 | 0.392 | 0.389 | 0.443 | 0.368 | 0.373 | 0.368 | 0.369 | 0.367 |
| (30, 80] | 806 | 0.495 | 0.494 | 0.512 | 0.548 | 0.488 | 0.47 | 0.469 | 0.462 | 0.462 |

## MAE by compound (s)

| compound_relative | n | persistence | compound_drift | ridge | mixed_effects | random_forest | xgboost | mlp | lstm | tcn |
|---|---|---|---|---|---|---|---|---|---|---|
| HARD | 4644 | 0.405 | 0.404 | 0.393 | 0.424 | 0.374 | 0.37 | 0.368 | 0.364 | 0.364 |
| MEDIUM | 3223 | 0.437 | 0.438 | 0.41 | 0.441 | 0.393 | 0.392 | 0.39 | 0.389 | 0.389 |
| SOFT | 860 | 0.484 | 0.487 | 0.432 | 0.457 | 0.417 | 0.408 | 0.402 | 0.407 | 0.405 |

## Chosen settings (tuned on 2024 blocks, seed 0)

| model | params | tuning MAE |
|---|---|---|
| mlp | {"hidden": 64, "dropout": 0.3} | 0.383 |
| lstm | {"hidden": 32, "dropout": 0.3} | 0.383 |
| tcn | {"hidden": 64, "dropout": 0.3} | 0.382 |

## Compute (CPU, summed over development folds and seeds)

Building lap sequences: 2.2 s.

| model | fit_s | predict_s | median_epochs |
|---|---|---|---|
| mlp | 310.92 | 0.93 | 10.0 |
| lstm | 600.21 | 1.01 | 10.0 |
| tcn | 3155.05 | 1.51 | 12.0 |
