# Methodology (Task 3: lap-time change associated with tyre age)

## Question

By how much does a lap get slower for each extra lap of tyre age, by compound,
once fuel burn, track evolution and the car-driver's pace are held fixed?

The answer is an **estimated association with tyre age**. Lap timing does not
measure tyre wear, grip or temperature. "Degradation" on the website always means
this estimate.

## Sample

Clean green dry laps on slicks (`is_clean_green`), 2023-2025, all 69 races that
pass validation. Pit laps, out-laps, first laps, safety car / VSC / red flag laps,
restart laps, yellow-flag laps, wet laps and laps beyond the race distance are
excluded by the cleaning flags. Groups with a single lap are dropped. Standard
errors are clustered by race (69 clusters).

## Model

lap_time = sum over compounds c of b_c x tyre_age x 1[compound = c]
         + race x lap effect + driver x race effect + race x compound effect + error

- **race x lap effects** absorb everything common to all cars on that lap: fuel
  burn, track evolution, temperature, wind.
- **driver x race effects** absorb the car-driver's pace at that race.
- **race x compound effects** absorb each compound's pace level at that race.

## Identification

Within a stint, tyre age = lap - (lap the stint started). With driver x stint
effects in place of driver x race effects, tyre age is an exact combination of
the fixed effects and the slope is **not identified** (the age-period-cohort
problem). The code checks this and refuses to report such estimates; the report
shows the check.

With driver x race effects, b_c is identified from the pace change at pit stops:
a driver who has run k laps on a set gains roughly b x k when fresh tyres go on,
and drivers stop after different k. Assumptions:

1. **Constant underlying pace across stints.** A driver's pace, apart from tyres,
   is the same in every stint of a race. Threat: drivers push harder or manage
   more in some stints. R6 adds race x stint-number effects, which absorb any such
   pattern common to all drivers; driver-specific patterns remain a threat.
2. **Common compound offsets.** The pace gap between compounds at a race is the
   same for all cars. Threat: cars that suit one compound.
3. **Exogenous stop timing given the controls.** Teams pit when tyres fade, so long
   stints come disproportionately from sets that held up, which biases slopes
   toward zero. R2 (tyre age up to 15 laps) limits the stints to the part most cars
   complete.
4. **Same relation for all drivers on a compound** (slopes pooled across drivers and,
   in the main model, across circuits). The circuit table shows how much this hides.

## Robustness

| label | change |
|---|---|
| naive | no race x lap effects: shows how much fuel burn and track evolution move the slope |
| R1 | first two laps of each stint dropped (tyre warm-up) |
| R2 | tyre age up to 15 laps (less selection from stop timing) |
| R4 | strict sample (pace outliers removed) |
| R5 | each season separately |
| R6 | adds race x stint-number effects |
| quadratic | tyre age and its square by compound; marginal effects at ages 5, 10, 20, 30 |
| curve | tyre-age dummies by compound (reference age 5), the shape used on the website |
| by circuit | one slope per circuit, compounds pooled |

## Checks of the estimator

`tests/test_tyre.py`: coefficients equal a dummy-variable regression; on simulated
races with known slopes (0.10 / 0.06 / 0.03 s per lap), race-specific compound
offsets, common lap shocks and a fuel effect of -0.06 s per lap, the main model
recovers the slopes and the naive model is biased by roughly the fuel effect; the
driver x stint model is refused as unidentified.
