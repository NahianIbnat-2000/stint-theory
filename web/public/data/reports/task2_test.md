# Task 2 final test: multi-lap stint forecasts (pre-registered)

Run 2026-11-24T11:06:00+00:00 to 2026-11-24T11:34:03+00:00. Test races 2025 R13-24. Rules: `docs/preregistration_task2.md`, SHA-256 `991df6177c18b37cfd75cac842eb187c6e0ee4812c62f8a5550a013a65e7ad73`, committed 2026-11-24T17:05:37+06:00, code commit `c662c5641693becb648676dd1c4a9c0a0239424d`.

- Origins with all 10 laps scored: 5241 from 12 races.

- Practical margin 0.1 s on the 10-lap total; Holm over three comparisons.

## Primary comparisons (10-lap total)

| # | comparison | 10-lap MAE diff (s) | 95% low | 95% high | 90% low | 90% high | p | Holm p | label |
|---|---|---|---|---|---|---|---|---|---|
| Q1 | xgboost_direct vs persistence | -1.0227 | -1.267 | -0.6943 | -1.2374 | -0.7457 | 0.0 | 0.0 | meaningful difference |
| Q2 | lstm_multi vs xgboost_direct | 0.1346 | 0.0299 | 0.2698 | 0.0417 | 0.2474 | 0.008 | 0.016 | statistically different, size unclear |
| Q3 | lstm_multi vs mlp_multi | -0.1508 | -0.4433 | 0.0092 | -0.3763 | -0.0013 | 0.09 | 0.09 | inconclusive |

## 10-lap total, all models

| model | origins | MAE of 10-lap total (s) | bias (s) |
|---|---|---|---|
| xgboost_direct | 5241 | 3.335 | 0.643 |
| lstm_multi | 5241 | 3.469 | 0.54 |
| mlp_multi | 5241 | 3.62 | 0.769 |
| persistence | 5241 | 4.357 | 1.196 |
| compound_drift | 5241 | 4.464 | -0.514 |
| trend_extrapolation | 5241 | 8.573 | -0.381 |

## Secondary: by horizon

| h | n | persistence | compound_drift | trend_extrapolation | xgboost_direct | mlp_multi | lstm_multi |
|---|---|---|---|---|---|---|---|
| 1 | 11041.0 | 0.382 | 0.381 | 0.425 | 0.345 | 0.346 | 0.343 |
| 2 | 10479.0 | 0.444 | 0.444 | 0.553 | 0.39 | 0.403 | 0.395 |
| 3 | 9920.0 | 0.496 | 0.497 | 0.682 | 0.428 | 0.449 | 0.437 |
| 4 | 9359.0 | 0.527 | 0.528 | 0.796 | 0.447 | 0.473 | 0.46 |
| 5 | 8835.0 | 0.55 | 0.552 | 0.904 | 0.464 | 0.489 | 0.477 |
| 6 | 8342.0 | 0.579 | 0.58 | 1.025 | 0.476 | 0.506 | 0.495 |
| 7 | 7860.0 | 0.606 | 0.606 | 1.142 | 0.495 | 0.531 | 0.519 |
| 8 | 7394.0 | 0.632 | 0.633 | 1.263 | 0.516 | 0.553 | 0.542 |
| 9 | 6929.0 | 0.663 | 0.661 | 1.389 | 0.537 | 0.573 | 0.563 |
| 10 | 6471.0 | 0.686 | 0.683 | 1.518 | 0.56 | 0.595 | 0.58 |

| h | n | xgb skill | skill 95% low | skill 95% high | lstm minus xgb (s) | diff 95% low | diff 95% high |
|---|---|---|---|---|---|---|---|
| 1 | 11041 | 0.0969 | 0.0337 | 0.1387 | -0.0018 | -0.0061 | 0.0016 |
| 2 | 10479 | 0.1208 | 0.0601 | 0.1634 | 0.0054 | -0.0009 | 0.0119 |
| 3 | 9920 | 0.1363 | 0.0718 | 0.1843 | 0.0087 | 0.0025 | 0.0157 |
| 4 | 9359 | 0.1519 | 0.0927 | 0.1982 | 0.0125 | 0.0051 | 0.0205 |
| 5 | 8835 | 0.1565 | 0.1017 | 0.1998 | 0.013 | 0.0057 | 0.0224 |
| 6 | 8342 | 0.1787 | 0.1314 | 0.2168 | 0.0196 | 0.0076 | 0.035 |
| 7 | 7860 | 0.1827 | 0.1363 | 0.2233 | 0.0236 | 0.008 | 0.0453 |
| 8 | 7394 | 0.1837 | 0.1345 | 0.2318 | 0.026 | 0.0068 | 0.0505 |
| 9 | 6929 | 0.1893 | 0.1321 | 0.2453 | 0.0252 | 0.0022 | 0.053 |
| 10 | 6471 | 0.1836 | 0.1261 | 0.2403 | 0.0205 | -0.0071 | 0.0552 |

## Secondary: sequence and model comparisons at horizons 5 and 10

| horizon | comparison | MAE diff (s) | 95% low | 95% high |
|---|---|---|---|---|
| 5 | lstm_multi vs mlp_multi | -0.0124 | -0.0371 | 0.0018 |
| 5 | lstm_multi vs xgboost_direct | 0.013 | 0.0056 | 0.0228 |
| 10 | lstm_multi vs mlp_multi | -0.0143 | -0.045 | 0.0027 |
| 10 | lstm_multi vs xgboost_direct | 0.0205 | -0.0064 | 0.0557 |

## Secondary: error correlation across laps (for the simulator)

| model | mean error correlation across the 10 laps |
|---|---|
| persistence | 0.756 |
| compound_drift | 0.757 |
| trend_extrapolation | 0.835 |
| xgboost_direct | 0.677 |
| mlp_multi | 0.694 |
| lstm_multi | 0.676 |

## Compute (seconds)

| persistence | compound_drift | trend_extrapolation | xgboost_direct | mlp_multi | lstm_multi |
|---|---|---|---|---|---|
| 0.0 | 0.1 | 0.0 | 177.7 | 308.5 | 1104.0 |
