# Simulator backtest (leave-race-out parameters)

Each race is checked with parameters estimated without it. These checks cover the building blocks; a counterfactual strategy outcome itself cannot be checked.

## 1. Pace of the next stint after a real pit stop (clean laps, s)

37586 laps after 1807 stops. Overall MAE: model 0.887, persistence 1.597; bias: model +0.298, persistence +1.456.

| bin | laps | model_mae | model_bias | persistence_mae | persistence_bias |
|---|---|---|---|---|---|
| (0, 3] | 2989 | 0.913 | 0.239 | 1.718 | 1.589 |
| (3, 6] | 4736 | 0.818 | 0.183 | 1.591 | 1.451 |
| (6, 10] | 6426 | 0.764 | 0.224 | 1.534 | 1.414 |
| (10, 15] | 7520 | 0.794 | 0.281 | 1.542 | 1.412 |
| (15, 20] | 6150 | 0.848 | 0.314 | 1.524 | 1.405 |
| (20, 30] | 6979 | 1.065 | 0.448 | 1.685 | 1.521 |
| (30, 80] | 2786 | 1.153 | 0.364 | 1.716 | 1.486 |

## 2. Remaining race time of the strategy actually run (s)

537 drivers in 43 races, decision lap at one third distance, no neutralisation afterwards for that driver.

| MAE (s) | median abs (s) | bias (s) | MAE per lap (s) | 90% of errors within (s) |
|---|---|---|---|---|
| 34.487 | 17.967 | 22.204 | 1.001 | 48.568 |

Strategy differences smaller than these errors are not separable by the model.

## 3. Pit loss of green-flag stops (s)

| stops | MAE | median abs | bias |
|---|---|---|---|
| 1572 | 5.081 | 1.378 | -2.014 |
