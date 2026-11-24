# Task 3: lap-time change associated with tyre age

Generated 2026-11-24T12:32:57+00:00. Sample: clean green dry laps on slicks, 2023-2025, 60248 laps in 68 races after dropping singleton groups. Standard errors clustered by race. These are estimated associations with tyre age, not measured tyre wear; see docs/methodology_tyre.md for the assumptions.

## Main estimate and robustness (seconds per extra lap of tyre age)

Positive = laps get slower as the tyres age, holding fixed the race lap (fuel, track), the driver's pace in that race and the compound's pace level at that race.

| specification | compound | s_per_lap | se | ci_low | ci_high | n laps | races |
|---|---|---|---|---|---|---|---|
| main: race-lap + driver-race + race-compound FE | SOFT | 0.0679 | 0.0063 | 0.0555 | 0.0803 | 60248 | 68 |
| main: race-lap + driver-race + race-compound FE | MEDIUM | 0.0478 | 0.0037 | 0.0405 | 0.055 | 60248 | 68 |
| main: race-lap + driver-race + race-compound FE | HARD | 0.0424 | 0.0028 | 0.037 | 0.0479 | 60248 | 68 |
| naive: no race-lap FE (fuel and track not removed) | SOFT | -0.0007 | 0.0143 | -0.0287 | 0.0274 | 60264 | 68 |
| naive: no race-lap FE (fuel and track not removed) | MEDIUM | -0.0232 | 0.013 | -0.0487 | 0.0023 | 60264 | 68 |
| naive: no race-lap FE (fuel and track not removed) | HARD | -0.0189 | 0.0053 | -0.0293 | -0.0084 | 60264 | 68 |
| R1: first 2 laps of each stint dropped | SOFT | 0.066 | 0.0061 | 0.0541 | 0.0778 | 58030 | 68 |
| R1: first 2 laps of each stint dropped | MEDIUM | 0.0458 | 0.0037 | 0.0386 | 0.053 | 58030 | 68 |
| R1: first 2 laps of each stint dropped | HARD | 0.0412 | 0.0027 | 0.036 | 0.0464 | 58030 | 68 |
| R2: tyre age <= 15 laps | SOFT | 0.0951 | 0.0081 | 0.0792 | 0.111 | 33685 | 68 |
| R2: tyre age <= 15 laps | MEDIUM | 0.0804 | 0.0061 | 0.0684 | 0.0924 | 33685 | 68 |
| R2: tyre age <= 15 laps | HARD | 0.0681 | 0.0054 | 0.0576 | 0.0786 | 33685 | 68 |
| R4: strict sample (pace outliers out) | SOFT | 0.0645 | 0.0059 | 0.053 | 0.0759 | 58049 | 68 |
| R4: strict sample (pace outliers out) | MEDIUM | 0.0469 | 0.0033 | 0.0405 | 0.0534 | 58049 | 68 |
| R4: strict sample (pace outliers out) | HARD | 0.0416 | 0.0027 | 0.0362 | 0.047 | 58049 | 68 |
| R6: + race x stint-number FE (common push/manage pattern by stint) | SOFT | 0.0703 | 0.0051 | 0.0604 | 0.0803 | 60243 | 68 |
| R6: + race x stint-number FE (common push/manage pattern by stint) | MEDIUM | 0.05 | 0.0041 | 0.042 | 0.0579 | 60243 | 68 |
| R6: + race x stint-number FE (common push/manage pattern by stint) | HARD | 0.0468 | 0.0034 | 0.04 | 0.0535 | 60243 | 68 |
| R5: season 2023 | SOFT | 0.0606 | 0.0101 | 0.0408 | 0.0803 | 19186 | 22 |
| R5: season 2023 | MEDIUM | 0.0492 | 0.0065 | 0.0365 | 0.0619 | 19186 | 22 |
| R5: season 2023 | HARD | 0.0427 | 0.0054 | 0.0322 | 0.0532 | 19186 | 22 |
| R5: season 2024 | SOFT | 0.0802 | 0.0132 | 0.0544 | 0.106 | 20792 | 23 |
| R5: season 2024 | MEDIUM | 0.0522 | 0.0089 | 0.0348 | 0.0695 | 20792 | 23 |
| R5: season 2024 | HARD | 0.0515 | 0.0044 | 0.0428 | 0.0601 | 20792 | 23 |
| R5: season 2025 | SOFT | 0.0707 | 0.0072 | 0.0567 | 0.0848 | 20270 | 23 |
| R5: season 2025 | MEDIUM | 0.0451 | 0.0038 | 0.0378 | 0.0525 | 20270 | 23 |
| R5: season 2025 | HARD | 0.0333 | 0.0035 | 0.0265 | 0.0401 | 20270 | 23 |

## Identification check

Same model with driver-stint instead of driver-race effects: not identified, as expected: with driver-stint effects, tyre age is an exact combination of the race-lap and stint effects. The main slope is therefore identified only from pace gains at pit stops compared across drivers who stopped at different tyre ages, under two assumptions: a driver's underlying pace is the same across stints, and compound offsets at a race are common to all cars.

## What the race-lap fixed effects remove

The naive slope mixes tyre ageing with everything that changes lap by lap for all cars (mostly fuel burn, which makes cars faster). The difference is roughly the common per-lap trend.

| compound | naive minus main (s/lap) |
|---|---|
| SOFT | -0.0685 |
| MEDIUM | -0.071 |
| HARD | -0.0613 |

## Curvature: quadratic specification, marginal effect at given tyre ages

| compound | tyre_age | marginal s_per_lap | se | ci_low | ci_high |
|---|---|---|---|---|---|
| SOFT | 5 | 0.0873 | 0.011 | 0.0658 | 0.1089 |
| SOFT | 10 | 0.0786 | 0.008 | 0.0629 | 0.0943 |
| SOFT | 20 | 0.0612 | 0.0043 | 0.0528 | 0.0697 |
| SOFT | 30 | 0.0438 | 0.0079 | 0.0283 | 0.0594 |
| MEDIUM | 5 | 0.0763 | 0.0054 | 0.0658 | 0.0869 |
| MEDIUM | 10 | 0.0664 | 0.0039 | 0.0587 | 0.0741 |
| MEDIUM | 20 | 0.0465 | 0.0022 | 0.0421 | 0.0509 |
| MEDIUM | 30 | 0.0266 | 0.0041 | 0.0185 | 0.0347 |
| HARD | 5 | 0.0641 | 0.0049 | 0.0545 | 0.0737 |
| HARD | 10 | 0.0573 | 0.0038 | 0.0498 | 0.0648 |
| HARD | 20 | 0.0437 | 0.0025 | 0.0387 | 0.0487 |
| HARD | 30 | 0.0301 | 0.0034 | 0.0234 | 0.0368 |

## Heterogeneity by circuit (all slick compounds pooled)

One slope per circuit, compounds pooled, so circuits with more soft running look steeper. Only 2-3 races per circuit, so standard errors are clustered by driver-race, not race: they ignore conditions shared within a race and are too narrow. Use this table to rank circuits, not to test differences between them.

| circuit | races | driver-race clusters | n laps | s_per_lap | se | ci_low | ci_high |
|---|---|---|---|---|---|---|---|
| Bahrain Grand Prix | 3 | 60 | 2778 | 0.1135 | 0.0051 | 0.1036 | 0.1235 |
| Belgian Grand Prix | 3 | 59 | 2019 | 0.0783 | 0.0099 | 0.059 | 0.0976 |
| Japanese Grand Prix | 3 | 57 | 2380 | 0.0725 | 0.0073 | 0.0582 | 0.0868 |
| Spanish Grand Prix | 3 | 59 | 3334 | 0.0657 | 0.0072 | 0.0515 | 0.0798 |
| Hungarian Grand Prix | 3 | 58 | 3630 | 0.059 | 0.0041 | 0.051 | 0.067 |
| Austrian Grand Prix | 3 | 57 | 3281 | 0.0587 | 0.003 | 0.0527 | 0.0646 |
| Abu Dhabi Grand Prix | 3 | 59 | 2924 | 0.0568 | 0.0032 | 0.0506 | 0.063 |
| São Paulo Grand Prix | 2 | 35 | 1990 | 0.0536 | 0.0037 | 0.0464 | 0.0609 |
| Chinese Grand Prix | 2 | 39 | 1665 | 0.0534 | 0.0084 | 0.0369 | 0.07 |
| Emilia Romagna Grand Prix | 2 | 40 | 2069 | 0.0516 | 0.0036 | 0.0446 | 0.0587 |
| Las Vegas Grand Prix | 3 | 57 | 2175 | 0.05 | 0.0071 | 0.0362 | 0.0639 |
| Singapore Grand Prix | 3 | 58 | 3005 | 0.0489 | 0.0045 | 0.04 | 0.0578 |
| United States Grand Prix | 3 | 59 | 2608 | 0.0481 | 0.006 | 0.0363 | 0.0599 |
| Mexico City Grand Prix | 3 | 56 | 3127 | 0.043 | 0.003 | 0.0371 | 0.0489 |
| Dutch Grand Prix | 3 | 60 | 2991 | 0.0401 | 0.0037 | 0.0328 | 0.0473 |
| Italian Grand Prix | 3 | 58 | 2658 | 0.0363 | 0.0052 | 0.0262 | 0.0464 |
| Australian Grand Prix | 3 | 42 | 1593 | 0.0348 | 0.006 | 0.0231 | 0.0466 |
| Monaco Grand Prix | 3 | 56 | 3250 | 0.0345 | 0.0043 | 0.026 | 0.043 |
| British Grand Prix | 3 | 54 | 1420 | 0.0322 | 0.0076 | 0.0172 | 0.0471 |
| Saudi Arabian Grand Prix | 3 | 57 | 2350 | 0.031 | 0.004 | 0.0231 | 0.0388 |
| Miami Grand Prix | 2 | 40 | 1951 | 0.023 | 0.0032 | 0.0168 | 0.0291 |
| Canadian Grand Prix | 3 | 58 | 2427 | 0.0226 | 0.0031 | 0.0166 | 0.0287 |
| Azerbaijan Grand Prix | 3 | 59 | 2354 | 0.0216 | 0.0047 | 0.0123 | 0.0309 |
| Qatar Grand Prix | 3 | 55 | 2269 | 0.0181 | 0.0075 | 0.0034 | 0.0328 |

## Non-parametric curve

Effect of each tyre age relative to age 5, by compound, saved in `tyre_age_curves.csv` (used by the website). Ages above 35 pooled.

| compound | tyre_age | effect_s | se | ci_low | ci_high | laps |
|---|---|---|---|---|---|---|
| SOFT | 2 | -0.198 | 0.127 | -0.446 | 0.05 | 232 |
| SOFT | 3 | -0.129 | 0.063 | -0.254 | -0.005 | 244 |
| SOFT | 10 | 0.436 | 0.073 | 0.293 | 0.58 | 369 |
| SOFT | 15 | 0.994 | 0.114 | 0.771 | 1.218 | 270 |
| SOFT | 20 | 1.101 | 0.115 | 0.876 | 1.327 | 169 |
| SOFT | 25 | 1.394 | 0.179 | 1.044 | 1.744 | 82 |
| SOFT | 30 | 1.75 | 0.166 | 1.426 | 2.075 | 28 |
| SOFT | 35 | 2.095 | 0.087 | 1.924 | 2.266 | 41 |
| MEDIUM | 2 | -0.393 | 0.071 | -0.533 | -0.252 | 800 |
| MEDIUM | 3 | -0.245 | 0.088 | -0.418 | -0.072 | 935 |
| MEDIUM | 10 | 0.424 | 0.042 | 0.341 | 0.506 | 1086 |
| MEDIUM | 15 | 0.678 | 0.057 | 0.567 | 0.79 | 888 |
| MEDIUM | 20 | 0.968 | 0.064 | 0.842 | 1.095 | 598 |
| MEDIUM | 25 | 1.098 | 0.077 | 0.947 | 1.249 | 364 |
| MEDIUM | 30 | 1.238 | 0.086 | 1.069 | 1.407 | 174 |
| MEDIUM | 35 | 1.385 | 0.101 | 1.186 | 1.583 | 548 |
| HARD | 1 | -0.074 | 0.233 | -0.531 | 0.382 | 2 |
| HARD | 2 | -0.397 | 0.064 | -0.522 | -0.272 | 768 |
| HARD | 3 | -0.132 | 0.057 | -0.244 | -0.019 | 960 |
| HARD | 10 | 0.291 | 0.062 | 0.17 | 0.412 | 1153 |
| HARD | 15 | 0.565 | 0.054 | 0.46 | 0.67 | 1095 |
| HARD | 20 | 0.79 | 0.058 | 0.676 | 0.904 | 910 |
| HARD | 25 | 0.98 | 0.077 | 0.829 | 1.132 | 699 |
| HARD | 30 | 1.09 | 0.084 | 0.925 | 1.254 | 507 |
| HARD | 35 | 1.329 | 0.093 | 1.148 | 1.511 | 2847 |
