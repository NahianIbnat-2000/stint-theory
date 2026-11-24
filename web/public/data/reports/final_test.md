# Final test: next-lap prediction (pre-registered)

Run 2026-11-24T07:19:34+00:00 to 2026-11-24T10:18:33+00:00. Test set: 2025 rounds 13-24, opened once for this run. Rules: `docs/preregistration.md`, SHA-256 `98780c55b2eebef466704f11b0c390a565e4cffc2cfaaf12684c4bd9c9cce0ab`, committed 2026-11-24T13:15:25+06:00, code commit `5c481b0f76484027328e66487a8ba0fb749efe6a`.

- Scored laps: 11041 from 12 races. Every model predicts the same laps.

- Neural models: mean of 5 seeds. xgboost_ens5: mean of 5 XGBoost seeds.

- Practical margin: 0.01 s. Holm correction over the five primary comparisons.

## Primary comparisons (pre-registered, section 4)

Negative MAE difference: the first model is more accurate.

| # | comparison | MAE diff (s) | 95% low | 95% high | 90% low | 90% high | p | Holm p | label | races tcn better | races lstm better | races mlp better |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 | tcn vs xgboost_ens5 | 0.0004 | -0.0039 | 0.0041 | -0.0032 | 0.0036 | 0.803 | 1.0 | equivalent | 5/12 |  |  |
| P2 | lstm vs xgboost_ens5 | 0.0002 | -0.0043 | 0.0038 | -0.0035 | 0.0034 | 0.866 | 1.0 | equivalent |  | 4/12 |  |
| P3 | mlp vs xgboost_ens5 | 0.0016 | -0.0022 | 0.005 | -0.0015 | 0.0046 | 0.396 | 1.0 | equivalent |  |  | 4/12 |
| P4 | lstm vs mlp | -0.0014 | -0.0038 | 0.0011 | -0.0034 | 0.0007 | 0.256 | 1.0 | equivalent |  | 7/12 |  |
| P5 | tcn vs mlp | -0.0012 | -0.0029 | 0.0007 | -0.0027 | 0.0003 | 0.186 | 0.93 | equivalent | 6/12 |  |  |

## Accuracy, all models

| model | n | mae | mae_ci_low | mae_ci_high | rmse | median_ae | bias | skill_vs_persistence | skill_ci_low | skill_ci_high |
|---|---|---|---|---|---|---|---|---|---|---|
| xgboost_ens5 | 11041 | 0.333 | 0.291 | 0.384 | 0.96 | 0.201 | -0.016 | 0.127 | 0.078 | 0.16 |
| lstm | 11041 | 0.333 | 0.294 | 0.383 | 0.942 | 0.201 | -0.027 | 0.126 | 0.075 | 0.163 |
| tcn | 11041 | 0.333 | 0.295 | 0.383 | 0.943 | 0.201 | -0.025 | 0.126 | 0.076 | 0.162 |
| xgboost | 11041 | 0.334 | 0.292 | 0.385 | 0.96 | 0.201 | -0.013 | 0.125 | 0.077 | 0.158 |
| mlp | 11041 | 0.335 | 0.296 | 0.384 | 0.944 | 0.201 | -0.02 | 0.123 | 0.075 | 0.157 |
| random_forest | 11041 | 0.338 | 0.299 | 0.384 | 0.954 | 0.213 | 0.032 | 0.113 | 0.074 | 0.142 |
| ridge | 11041 | 0.36 | 0.321 | 0.407 | 0.955 | 0.229 | 0.036 | 0.058 | 0.02 | 0.087 |
| compound_drift | 11041 | 0.381 | 0.335 | 0.433 | 1.015 | 0.209 | 0.007 | 0.001 | -0.003 | 0.006 |
| persistence | 11041 | 0.382 | 0.336 | 0.435 | 1.016 | 0.21 | 0.037 | 0.0 | 0.0 | 0.0 |
| mixed_effects | 11041 | 0.39 | 0.347 | 0.44 | 0.987 | 0.251 | 0.024 | -0.022 | -0.055 | 0.006 |

## Secondary analyses (no multiplicity correction)

| analysis | comparison | n laps | MAE diff (s) | 95% low | 95% high |
|---|---|---|---|---|---|
| S1 tyres > 30 laps | lstm vs xgboost_ens5 | 1008 | 0.0068 | -0.0002 | 0.014 |
| S1 tyres > 30 laps | tcn vs xgboost_ens5 | 1008 | 0.0094 | 0.0027 | 0.0153 |
| S5 seed averaging | xgboost_ens5 vs xgboost | 11041 | -0.0005 | -0.001 | 0.0 |

S2. Single seeds (single XGBoost MAE: 0.3336 s):

| model | seeds | mae_mean | mae_sd | mae_min | mae_max | skill_mean | ensemble_mae |
|---|---|---|---|---|---|---|---|
| mlp | 5 | 0.3368 | 0.0014 | 0.3354 | 0.3388 | 0.1174 | 0.3347 |
| lstm | 5 | 0.3359 | 0.0016 | 0.3345 | 0.3384 | 0.1197 | 0.3333 |
| tcn | 5 | 0.3359 | 0.0016 | 0.3345 | 0.3386 | 0.1196 | 0.3335 |

S4. Strict sample:

| model | n | mae | rmse | skill_vs_persistence |
|---|---|---|---|---|
| xgboost_ens5 | 10713 | 0.289 | 0.512 | 0.146 |
| xgboost | 10713 | 0.29 | 0.512 | 0.145 |
| lstm | 10713 | 0.291 | 0.513 | 0.142 |
| tcn | 10713 | 0.291 | 0.513 | 0.142 |
| mlp | 10713 | 0.292 | 0.512 | 0.139 |
| random_forest | 10713 | 0.296 | 0.507 | 0.126 |
| ridge | 10713 | 0.319 | 0.536 | 0.058 |
| compound_drift | 10713 | 0.338 | 0.599 | 0.003 |
| persistence | 10713 | 0.339 | 0.601 | 0.0 |
| mixed_effects | 10713 | 0.349 | 0.578 | -0.03 |

## MAE by tyre age of the predicted lap (s)

| tyre_age_bin | n | persistence | compound_drift | ridge | mixed_effects | random_forest | xgboost | xgboost_ens5 | mlp | lstm | tcn |
|---|---|---|---|---|---|---|---|---|---|---|---|
| (0, 5] | 1234 | 0.641 | 0.633 | 0.518 | 0.576 | 0.488 | 0.486 | 0.484 | 0.489 | 0.485 | 0.481 |
| (5, 10] | 2107 | 0.374 | 0.373 | 0.372 | 0.381 | 0.345 | 0.347 | 0.35 | 0.348 | 0.35 | 0.35 |
| (10, 15] | 2207 | 0.301 | 0.303 | 0.298 | 0.319 | 0.278 | 0.272 | 0.272 | 0.275 | 0.274 | 0.274 |
| (15, 20] | 1949 | 0.32 | 0.32 | 0.305 | 0.328 | 0.295 | 0.288 | 0.286 | 0.28 | 0.279 | 0.28 |
| (20, 30] | 2536 | 0.362 | 0.362 | 0.351 | 0.394 | 0.332 | 0.324 | 0.323 | 0.326 | 0.324 | 0.325 |
| (30, 80] | 1008 | 0.423 | 0.424 | 0.402 | 0.446 | 0.375 | 0.366 | 0.364 | 0.374 | 0.371 | 0.374 |

## MAE by race (s)

| race_id | n | persistence | compound_drift | ridge | mixed_effects | random_forest | xgboost | xgboost_ens5 | mlp | lstm | tcn |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2025_13 | 691 | 0.563 | 0.561 | 0.577 | 0.63 | 0.557 | 0.596 | 0.594 | 0.589 | 0.598 | 0.593 |
| 2025_14 | 1257 | 0.4 | 0.401 | 0.353 | 0.408 | 0.331 | 0.326 | 0.325 | 0.327 | 0.325 | 0.327 |
| 2025_15 | 886 | 0.298 | 0.3 | 0.288 | 0.326 | 0.259 | 0.264 | 0.265 | 0.275 | 0.274 | 0.276 |
| 2025_16 | 861 | 0.286 | 0.281 | 0.309 | 0.315 | 0.287 | 0.26 | 0.261 | 0.265 | 0.266 | 0.263 |
| 2025_17 | 755 | 0.367 | 0.363 | 0.342 | 0.366 | 0.324 | 0.32 | 0.318 | 0.318 | 0.323 | 0.322 |
| 2025_18 | 1086 | 0.568 | 0.566 | 0.503 | 0.54 | 0.478 | 0.472 | 0.472 | 0.459 | 0.455 | 0.455 |
| 2025_19 | 864 | 0.349 | 0.35 | 0.337 | 0.36 | 0.301 | 0.296 | 0.295 | 0.303 | 0.3 | 0.299 |
| 2025_20 | 1046 | 0.388 | 0.39 | 0.344 | 0.383 | 0.328 | 0.319 | 0.318 | 0.318 | 0.319 | 0.315 |
| 2025_21 | 998 | 0.336 | 0.341 | 0.31 | 0.338 | 0.288 | 0.284 | 0.284 | 0.293 | 0.285 | 0.286 |
| 2025_22 | 716 | 0.295 | 0.292 | 0.303 | 0.308 | 0.296 | 0.285 | 0.285 | 0.282 | 0.28 | 0.282 |
| 2025_23 | 854 | 0.37 | 0.364 | 0.356 | 0.378 | 0.346 | 0.33 | 0.329 | 0.331 | 0.322 | 0.327 |
| 2025_24 | 1027 | 0.337 | 0.339 | 0.312 | 0.335 | 0.29 | 0.284 | 0.283 | 0.288 | 0.289 | 0.289 |

## S6. Compute (this machine, summed over test folds)

| model | fit_s | predict_s |
|---|---|---|
| persistence | 0.04 | 0.01 |
| compound_drift | 0.06 | 0.03 |
| ridge | 9.48 | 0.21 |
| mixed_effects | 63.58 | 0.51 |
| random_forest | 307.76 | 1.0 |
| xgboost | 16.44 | 0.27 |
| xgboost_ens5 | 75.5 | 1.32 |
| mlp | 903.82 | 2.15 |
| lstm | 2864.17 | 2.72 |
| tcn | 6479.67 | 3.75 |
