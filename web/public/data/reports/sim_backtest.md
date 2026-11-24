# Simulator backtest (leave-race-out parameters)

Each race is checked with parameters estimated without it. These checks cover the building blocks; a counterfactual strategy outcome itself cannot be checked.

## Pace-model parameters across the leave-race-out fits

`lap_number` is the common per-lap trend (fuel burn + track evolution; Task 3 implied about -0.065 s/lap). `k_*` are compound offsets against medium; `age_*`, `age2_*` the tyre-age curve (Task 3 spec); `tail_*` the linear Task 3 slopes used as the minimum slope beyond the curve's cap; `circuit_scale` should average about 1.

| parameter | mean | min | max |
|---|---|---|---|
| lap_number | -0.0568 | -0.0577 | -0.0549 |
| k_SOFT | -0.2509 | -0.2731 | -0.2159 |
| k_HARD | 0.0755 | 0.0619 | 0.1187 |
| age_SOFT | 0.0678 | 0.0653 | 0.0695 |
| age_MEDIUM | 0.0478 | 0.0471 | 0.0507 |
| age_HARD | 0.0424 | 0.0415 | 0.0437 |
| age2_SOFT | 0.0 | 0.0 | 0.0 |
| age2_MEDIUM | 0.0 | 0.0 | 0.0 |
| age2_HARD | 0.0 | 0.0 | 0.0 |
| tail_SOFT | 0.0678 | 0.0653 | 0.0695 |
| tail_MEDIUM | 0.0478 | 0.0471 | 0.0507 |
| tail_HARD | 0.0424 | 0.0415 | 0.0437 |
| circuit_scale | 1.0087 | 0.5 | 1.9049 |
| pit_loss | 24.8956 | 18.878 | 46.994 |

## 1. Pace of the next stint after a real pit stop (clean laps, s)

37586 laps after 1807 stops. Overall MAE: model 0.876, persistence 1.597; bias: model +0.177, persistence +1.456.

| bin | laps | model_mae | model_bias | persistence_mae | persistence_bias |
|---|---|---|---|---|---|
| (0, 3] | 2989 | 0.904 | 0.395 | 1.718 | 1.589 |
| (3, 6] | 4736 | 0.802 | 0.269 | 1.591 | 1.451 |
| (6, 10] | 6426 | 0.765 | 0.214 | 1.534 | 1.414 |
| (10, 15] | 7520 | 0.787 | 0.169 | 1.542 | 1.412 |
| (15, 20] | 6150 | 0.829 | 0.092 | 1.524 | 1.405 |
| (20, 30] | 6979 | 1.055 | 0.117 | 1.685 | 1.521 |
| (30, 80] | 2786 | 1.12 | 0.058 | 1.716 | 1.486 |

## 2. Remaining race time of the strategy actually run (s)

537 drivers in 43 races, decision lap at one third distance, no neutralisation afterwards for that driver.

| MAE (s) | median abs (s) | bias (s) | MAE per lap (s) | 90% of errors within (s) |
|---|---|---|---|---|
| 35.053 | 19.187 | 19.062 | 1.003 | 50.885 |

Strategy differences smaller than these errors are not separable by the model.

## 3. Pit loss of green-flag stops (s)

| stops | MAE | median abs | bias |
|---|---|---|---|
| 1572 | 5.586 | 2.008 | -0.883 |
