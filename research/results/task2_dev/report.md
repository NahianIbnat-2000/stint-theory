# Task 2: multi-lap forecasts on the development races

2025 rounds 1-12, one race at a time from all earlier races. Test set not loaded. Settings carried over from Task 1, not retuned.

- Origins: 9064 from 11 races; scored (origin, horizon) pairs: 67554. Every model forecasts the same pairs.

- Neural models: mean of 3 seeds, one network forecasting all 10 laps.

## MAE by horizon (s)

The sample shrinks with the horizon: long horizons need long stints without a neutralisation.

| h | n | persistence | compound_drift | trend_extrapolation | xgboost_direct | mlp_multi | lstm_multi |
|---|---|---|---|---|---|---|---|
| 1 | 8727.0 | 0.425 | 0.425 | 0.48 | 0.397 | 0.391 | 0.379 |
| 2 | 8317.0 | 0.522 | 0.522 | 0.661 | 0.459 | 0.466 | 0.452 |
| 3 | 7850.0 | 0.58 | 0.582 | 0.809 | 0.496 | 0.51 | 0.489 |
| 4 | 7389.0 | 0.625 | 0.627 | 0.948 | 0.533 | 0.546 | 0.525 |
| 5 | 6952.0 | 0.668 | 0.672 | 1.083 | 0.563 | 0.577 | 0.555 |
| 6 | 6518.0 | 0.702 | 0.705 | 1.215 | 0.588 | 0.601 | 0.576 |
| 7 | 6075.0 | 0.728 | 0.731 | 1.351 | 0.605 | 0.619 | 0.598 |
| 8 | 5644.0 | 0.746 | 0.748 | 1.473 | 0.622 | 0.635 | 0.614 |
| 9 | 5234.0 | 0.77 | 0.768 | 1.596 | 0.639 | 0.656 | 0.634 |
| 10 | 4848.0 | 0.798 | 0.793 | 1.734 | 0.667 | 0.682 | 0.654 |

## XGBoost skill and LSTM vs XGBoost by horizon (race-clustered 95% intervals)

| h | n | xgb skill | skill 95% low | skill 95% high | lstm minus xgb (s) | diff 95% low | diff 95% high |
|---|---|---|---|---|---|---|---|
| 1 | 8727 | 0.0663 | -0.0 | 0.1384 | -0.0172 | -0.035 | -0.0007 |
| 2 | 8317 | 0.1207 | 0.0681 | 0.1799 | -0.0072 | -0.0243 | 0.0101 |
| 3 | 7850 | 0.145 | 0.0975 | 0.1978 | -0.0065 | -0.0283 | 0.0168 |
| 4 | 7389 | 0.1462 | 0.0895 | 0.1979 | -0.0088 | -0.037 | 0.0196 |
| 5 | 6952 | 0.1563 | 0.0914 | 0.2104 | -0.0081 | -0.0411 | 0.028 |
| 6 | 6518 | 0.1628 | 0.0857 | 0.2088 | -0.0112 | -0.0507 | 0.0294 |
| 7 | 6075 | 0.1684 | 0.0798 | 0.2174 | -0.0068 | -0.0501 | 0.0394 |
| 8 | 5644 | 0.1667 | 0.0736 | 0.2193 | -0.0079 | -0.0571 | 0.0434 |
| 9 | 5234 | 0.1707 | 0.0772 | 0.2271 | -0.0045 | -0.0571 | 0.0525 |
| 10 | 4848 | 0.1635 | 0.0715 | 0.2205 | -0.0133 | -0.0768 | 0.0543 |

## Total time of the next 10 laps

Origins where all ten laps are scored. This is the quantity a strategy simulator adds up.

| model | origins | MAE of total (s) | median abs (s) | bias (s) |
|---|---|---|---|---|
| xgboost_direct | 4060 | 3.722 | 2.864 | 0.584 |
| lstm_multi | 4060 | 3.727 | 2.737 | 0.306 |
| mlp_multi | 4060 | 4.005 | 3.121 | 0.709 |
| persistence | 4060 | 4.838 | 3.291 | 0.793 |
| compound_drift | 4060 | 4.896 | 3.39 | -0.676 |
| trend_extrapolation | 4060 | 10.094 | 6.406 | -0.281 |

## Compute (seconds, summed over folds)

| persistence | compound_drift | trend_extrapolation | xgboost_direct | mlp_multi | lstm_multi |
|---|---|---|---|---|---|
| 0.0 | 0.1 | 0.0 | 83.0 | 196.8 | 765.9 |
