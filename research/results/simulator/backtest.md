# Simulator backtest (leave-race-out parameters)

Each race is checked with parameters estimated without it. These checks cover the building blocks; a counterfactual strategy outcome itself cannot be checked.

## Pace-model parameters across the leave-race-out fits

`lap_number` is the common per-lap trend (fuel burn + track evolution; Task 3 implied about -0.065 s/lap). `k_*` are compound offsets against medium; `age_*`, `age2_*` the tyre-age curve.

| parameter | mean | min | max |
|---|---|---|---|
| lap_number | -0.053 | -0.054 | -0.0517 |
| k_SOFT | -0.0449 | -0.1414 | 0.1266 |
| k_HARD | -0.2185 | -0.2667 | -0.0615 |
| age_SOFT | 0.0302 | 0.023 | 0.0345 |
| age_MEDIUM | 0.043 | 0.0237 | 0.0581 |
| age_HARD | 0.0596 | 0.0503 | 0.0623 |
| age2_SOFT | 0.0005 | 0.0003 | 0.0006 |
| age2_MEDIUM | -0.0004 | -0.0005 | 0.0003 |
| age2_HARD | -0.0005 | -0.0006 | -0.0003 |
| circuit_scale | 1.491 | 0.3333 | 3.1889 |
| pit_loss | 24.8956 | 18.878 | 46.994 |

## 1. Pace of the next stint after a real pit stop (clean laps, s)

37586 laps after 1807 stops. Overall MAE: model 0.910, persistence 1.597; bias: model +0.329, persistence +1.456.

| bin | laps | model_mae | model_bias | persistence_mae | persistence_bias |
|---|---|---|---|---|---|
| (0, 3] | 2989 | 0.909 | 0.289 | 1.718 | 1.589 |
| (3, 6] | 4736 | 0.81 | 0.233 | 1.591 | 1.451 |
| (6, 10] | 6426 | 0.782 | 0.271 | 1.534 | 1.414 |
| (10, 15] | 7520 | 0.821 | 0.327 | 1.542 | 1.412 |
| (15, 20] | 6150 | 0.886 | 0.341 | 1.524 | 1.405 |
| (20, 30] | 6979 | 1.106 | 0.444 | 1.685 | 1.521 |
| (30, 80] | 2786 | 1.178 | 0.359 | 1.716 | 1.486 |

## 2. Remaining race time of the strategy actually run (s)

537 drivers in 43 races, decision lap at one third distance, no neutralisation afterwards for that driver.

| MAE (s) | median abs (s) | bias (s) | MAE per lap (s) | 90% of errors within (s) |
|---|---|---|---|---|
| 37.327 | 20.721 | 26.346 | 1.071 | 53.102 |

Strategy differences smaller than these errors are not separable by the model.

## 3. Pit loss of green-flag stops (s)

| stops | MAE | median abs | bias |
|---|---|---|---|
| 1572 | 5.586 | 2.008 | -0.883 |
