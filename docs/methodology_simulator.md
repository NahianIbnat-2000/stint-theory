# Methodology (Phase 4: strategy simulator)

> Strategy outcomes are model-based counterfactual estimates, not observations of
> what would necessarily have happened.

## What it simulates

One car, from a decision lap L to the chequered flag, for a chosen strategy (stop
laps and compounds). It reports race time, not finishing position: other cars,
traffic, track position, undercuts and team orders are not modelled, so a
position forecast would not be credible.

## Why not XGBoost

Tasks 1 and 2 found XGBoost the most accurate forecaster of the **current** stint.
It forecasts from the current stint's recent laps, so it cannot forecast a stint
that has not started (for example "stop on lap 20 for hards"). The simulator uses
the structural pace model below for every lap, and the backtest compares it with
simple benchmarks on real stints.

## Pace model (no hindsight)

Estimated for each race **without that race's laps** (leave-race-out), on clean
green dry laps on slicks:

lap_time = mu[driver x race] + beta x lap + kappa[compound]
           + s_circuit x (b1[compound] x age + b2[compound] x age^2) + e

- beta: common per-lap trend (fuel burn + track evolution).
- kappa: pace of soft and hard relative to medium (pooled across circuits; the
  relative labels map to different Pirelli compounds at different races).
- b1, b2: tyre-age curve by compound; quadratic up to age 40, linear beyond.
- s_circuit: this circuit's tyre-age slope in other years divided by the average
  slope, shrunk toward 1 with weight n/(n+1) (n = other years at this circuit).
- e: AR(1) within a driver's race (persistence of errors found in Task 2).
- mu (driver pace): from the driver's last 8 clean laps **up to lap L**, net of the
  model terms. Needs at least 3 clean laps, so very early decision laps are refused.

## Pit loss

Each real stop: in-lap + out-lap time minus twice the driver's median clean lap
within ±6 laps. Stops with a red-flag lap are excluded (tyre changes during a
stoppage cost no pit-lane time). Mean = median green-flag loss at this circuit in
other years (all other races if fewer than 5 stops); spread from the deviation of
stops around their circuit median; stops under SC/VSC cost `neutralised_factor`
times the green loss (median ratio, other races).

## Safety car

Modes: none; random (per-lap hazard and duration distribution from the race
leader's laps in other races); or forced at a chosen lap. SC laps are slowed by the
median ratio of SC lap time to the same driver's clean laps. VSC is not modelled.

## Uncertainty

Each Monte Carlo draw samples the pace coefficients from their estimated
covariance (race-clustered), the driver's pace from its standard error, an AR(1)
residual path, pit-loss shocks and the safety car. **Common random numbers**: within
a draw every strategy sees the same values, so differences between strategies
reflect the strategies, not luck. Reported: mean and 5th-95th percentile of total
time, mean difference to a reference strategy with its 5th-95th percentile, and
the share of draws in which a strategy is faster.

Not included: circuit-scale uncertainty, compound offsets specific to the race,
driver-specific tyre behaviour, tyre sets actually available, weather.

## Rules

Dry race: at least two different slick compounds. Minimum stint after a stop: 3
laps. Race-specific (verified against FIA, Pirelli and press reports):
2023 Qatar, at most 18 laps of tyre life per set; 2025 Monaco, at least two pit
stops; 2025 Qatar, at most 25 laps per set. Mostly wet races are not simulated.

## Best strategy

Dynamic programming over every stop lap and compound allowed by the rules, for
0 to 3 more stops, minimising expected time without a safety car. Driver pace and
the per-lap trend are the same for all strategies and drop out of the comparison.

## Random numbers

A mulberry32 generator with Box-Muller normals (`simulation/rng.py`), so the
website's JavaScript version can reproduce Python results draw for draw.

## Checks

`python -m simulation backtest`: next-stint pace after real stops vs repeating the
last clean lap; expected remaining time of the strategy actually run vs the actual
time (drivers with no neutralisation after the decision lap); pit-loss error.
Unit tests: leave-race-out (changing a race's laps does not change its
parameters), decision state uses only laps up to L, a stop adds its loss, same seed
gives the same result, common random numbers, a safety car makes a stop cheaper,
the optimiser equals brute-force search, and all rules.
