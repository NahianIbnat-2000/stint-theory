# Known limitations

Current as of the final Task 1 and Task 2 tests, the Task 3 estimates and the frozen
simulator (November 2026). Dataset coverage figures live in one place,
`data/reports/coverage.json` (and the readable `coverage_report.md`); this file
describes what the results can and cannot support.

## Data

1. **Three seasons, one rules era.** OpenF1's free history starts in 2023 and
   FastF1's source now needs a paid F1 TV subscription. The sample is 2023 to 2025:
   results cannot be tested across a regulation change, and the neural models have
   less data to learn from than they would with a longer history.
2. **Unofficial source.** OpenF1 is a community project, not affiliated with
   Formula 1. Data can change or disappear. Raw and processed lap tables are not
   committed or published; the website carries derived results only.
3. **One race excluded.** Races with less than 90% of laps recorded are excluded
   (2025 Miami Grand Prix, 55.8%). The coverage report lists every check.
4. **Rebuilt fields.** Track status, in-laps and deleted laps are rebuilt from
   race-control messages and lap flags (methodology section 3). The rules were
   checked against real races (VSC-to-SC upgrades, behind-safety-car restarts,
   periods running at the flag), but unusual message wording can still be missed;
   the coverage report counts unmatched and unpaired messages.
5. **Race distance.** Without a hand-checked value, `scheduled_laps` is the
   winner's lap count, wrong for shortened races. `data/reference/scheduled_laps.csv`
   overrides it.
6. **Round numbers** are the order of races held, not necessarily official rounds.
7. **Tyre life of used sets** includes laps from earlier sessions as reported.
8. **No gaps to other cars.** Traffic and dirty air are not measured.
9. **Weather is session-level**, sampled about once a minute at one station.

## Forecasting results (Tasks 1 and 2)

10. **Scored sample.** Errors apply to clean green-flag laps (no pit, safety car,
    red flag, first lap or deleted lap). Hindsight flags are used only to choose the
    scored laps, never as features.
11. **One test, twelve races.** The locked test set is 2025 rounds 13-24, scored once
    under the pre-registrations. Intervals are race-clustered bootstraps over twelve
    races, so they are wide relative to the differences between the best models.
12. **Equivalence is relative to a margin.** "Equivalent" means the 90% interval of
    the difference lies inside ±0.01 s per lap (Task 1), a margin fixed before the
    test. It is not a claim that the models are identical.

## Tyre-age effect (Task 3)

13. **Association, not tyre wear.** Public timing shows lap time, not the state of
    the tyres. The estimates are lap-time changes associated with tyre age after
    removing race-lap, driver-race and race-compound effects.
14. **Identification.** The slope is identified from pace changes at pit stops,
    compared across drivers who stopped at different tyre ages. It assumes a
    driver's underlying pace is the same across stints and compound offsets are
    common to all cars at a race. Pit timing is chosen, not random.
15. **Curvature.** The effect is steeper early in a stint (tyre age <= 15 laps gives
    larger slopes); the headline is a linear average.
16. **Circuit table.** Two or three races per circuit; its intervals are too narrow.

## Strategy simulator (frozen after backtest 3)

17. **Single car against the clock.** No traffic, track position or other cars'
    strategies; it reports race time, never positions.
18. **Absolute accuracy.** Remaining race time from one-third distance (537 drivers,
    43 races, no neutralisation afterwards): mean absolute error 35.1 s, bias +19.1 s
    (too slow), 90% of errors within 50.9 s. Source:
    `research/results/simulator/backtest.md`.
19. **What that means for comparisons.** Those are errors in absolute time, not an
    interval for the gap between two plans: much of the error is shared by every
    plan for the same driver and cancels in a comparison. The part that does not
    cancel is the fresh-tyre bias: pace in the first laps of a stint is about
    0.4 s/lap too slow, so each extra stop is charged roughly 1-2 s too much.
20. **Uncertainty shown on the website** covers model parameters, the driver's pace,
    lap-to-lap noise, pit-stop variation and safety cars. It does not cover
    systematic model error (items 18-19). Parameter intervals are somewhat too narrow
    (block-diagonal covariance across the three estimation steps; no circuit-factor
    uncertainty).
21. **Dry races on slicks only.** VSC is not modelled; tyre sets actually available
    are not known; weather changes are not modelled.
