# Methodology: forecasting models (Tasks 1 and 2)

Status: all models below were developed, frozen and scored once on the locked test
races (Task 1: `research/results/final_test/report.md`; Task 2:
`research/results/task2_test/report.md`). Development results are in
`research/results/phase2_dev/`, `phase3_dev/` and `task2_dev/`.

## Task

Predict a driver's next lap time (lap t+1) from information available at the end
of lap t, given that the driver stays out on the same tyres. Scored only on laps
t+1 that are clean green laps (`target_valid`). Strict-sample results
(`target_valid_strict`, pace outliers removed) are reported as a sensitivity check.

## Split (fixed before any model was fitted)

| part | races | use |
|---|---|---|
| train | 2023 and 2024 seasons | fitting; hyperparameter tuning inside 2024 |
| dev | 2025 rounds 1-12 | rolling-origin evaluation: each race predicted from all earlier races |
| test | 2025 rounds 13-24 | **locked**: not loaded until every model, deep learning included, is final |

The lock is in code (`models/data.py`). Test rows are dropped on load. Opening the
lock needs an environment variable and is logged to `data/reports/test_access.log`.

Hyperparameters are chosen on four 2024 blocks (rounds 1-6, 7-12, 13-18, 19-24),
each predicted from every race before it. 2025 is never used for tuning, so the
development scores are not tuned to the races they are scored on.

## Reference pace and target

`ref` = the last real-time-green lap in the current stint, or, if the stint has
none yet, the median of other drivers' green laps in the last 120 s. Models other
than persistence predict `y - ref`, the change from that reference. This keeps
circuit lap-time levels out of the problem.

## Models

| model | family | what it is |
|---|---|---|
| persistence | benchmark | `ref` |
| compound_drift | benchmark | `ref` + average lap-to-lap change for the compound in training |
| ridge | statistical | linear model with tyre age and its square, fuel proxy, weather, recent pace, field pace, one-hot compound / circuit / team; alpha tuned |
| mixed_effects | statistical | linear mixed model: fixed effects as above (compound and circuit as factors), random intercept and random tyre-age slope by driver (falls back to intercept only if the slope fit fails; recorded) |
| random_forest | machine learning | 200 trees, half-sample bagging; leaf size and feature share tuned |
| xgboost | machine learning | gradient-boosted trees; depth, number of trees, min child weight tuned |

Imputation (median, with missing-value indicators), scaling and one-hot encoding
are fitted inside each training fold only. Unseen categories (for example a rookie
team name) are encoded as all zeros. Driver identity enters only the mixed model.

## Scoring

MAE, RMSE, median absolute error and bias (mean of prediction minus actual), with
skill = 1 - MAE / MAE(persistence). Intervals are 95% race-clustered bootstrap
intervals (whole races are resampled, 2000 times). Models are compared in pairs on
the same laps: the bootstrap interval of the MAE difference, and the number of
races where each model has the lower MAE. A model is called better only when the
whole interval is on one side of zero.

With 12 development races the intervals are rough. The test set (12 races) has
the same limit.

## Phase 3: neural models

Same task, scored laps, split, rolling-origin folds and 2024 tuning blocks as
Phase 2. The Phase 2 models are frozen after run 3; their stored predictions are
compared with the neural ones lap by lap.

| model | inputs | architecture |
|---|---|---|
| mlp | Phase 2 tabular inputs only | 2 hidden layers |
| lstm | tabular inputs + the driver's last 10 laps | LSTM encoder over the laps, joined with a tabular encoder |
| tcn | tabular inputs + the same 10 laps | 3 causal dilated convolution blocks (dilations 1, 2, 4), joined with a tabular encoder |

**Lap sequence.** For the origin lap t, laps t-9..t of the same driver in the same
race (front-padded early in the race). Per lap: lap time minus the origin's
reference pace (divided by 5, clipped to [-3, 6]), missing-time flag, real-time
green, pit in, pit out, SC, VSC, yellow, restart lap, same-stint-as-origin, tyre
life / 30, compound (soft / medium / hard), and a present-lap flag. Only laps up to
t are used; a test changes later laps and checks the sequence does not move.

**Design of the comparison.** The MLP sees exactly the inputs XGBoost sees, so
mlp vs xgboost compares the learners. LSTM and TCN add the raw lap sequence to the
same inputs, so lstm/tcn vs mlp measures what the sequence adds beyond the
hand-built summaries (last green lap, 3-lap mean, 5-lap spread and trend).

**Training.** Target y - ref, Huber loss (delta 0.5 s, matching the pseudo-Huber
loss XGBoost chose), AdamW (learning rate 1e-3, weight decay 1e-4), batch 256, up
to 40 epochs. Early stopping (patience 5) on the last 3 races of each training
fold; the tabular scaler and encoders are fitted on the remaining races. Hidden
size (32, 64) and dropout (0.1, 0.3) are tuned on the 2024 blocks with seed 0.

**Seeds.** Each development fold is trained with 5 seeds. The reported prediction
is the mean of the 5 (a seed ensemble); single-seed mean, spread, minimum and
maximum are reported next to it, because an ensemble of 5 networks is a different
model from one network and the random forest and XGBoost are single fitted models.

## Changes after looking at development results

Listed with the results that prompted them in [model_changes.md](model_changes.md).

## Known limits

- Scored laps are clean green laps. Errors on laps after pit stops, under safety
  car or in traffic-heavy restarts are not measured here.
- Next-lap prediction is dominated by the previous lap. Gains over persistence
  are expected to be small in seconds; the skill score makes them comparable.
- A model that predicts next-lap time well may still be poor at multi-lap
  forecasts (Phase 3, Task 2) or at strategy (Phase 4).

## Task 2: multi-lap stint forecasts

At the end of lap t, forecast laps t+1 to t+10 for a driver who stays out on the
same tyres. A pair (t, h) is scored when laps t+1 to t+h are consecutive laps of
the same stint, none of laps t+1 to t+h-1 is under SC, VSC, red flag or a restart,
and lap t+h is a clean green lap. Slow laps in between for other reasons (traffic,
yellows) stay in. Inputs are the origin-lap features plus the horizon h.

Models: persistence (`ref` for every h); compound drift (`ref` + h x average
one-lap change for the compound); trend extrapolation (`ref` + h x the recent
5-lap trend, clipped to the 1st-99th percentile of training slopes); XGBoost
direct (one model on stacked (origin, h) rows with h and tyre age at the target as
inputs, frozen Task 1 settings); MLP and LSTM with ten outputs and a masked Huber
loss (frozen Task 1 settings, 3 seeds). Settings are carried over from Task 1, not
retuned. The TCN is left out: in Task 1 it was equivalent to the LSTM at twice the
training cost.

Reported: MAE by horizon, XGBoost skill and LSTM minus XGBoost by horizon with
race-clustered intervals, and the error of the total time of the next ten laps
(the quantity a strategy simulator adds up). The test-set run for Task 2 will be
pre-registered after the development results, as in Task 1.
