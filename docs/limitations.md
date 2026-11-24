# Known limitations (Phase 1)

1. **No real data processed yet.** The code is tested on a synthetic race and fake
   OpenF1 responses only. Real coverage is unknown until the first ingest run.
2. **Three seasons, one rules era.** OpenF1's free history starts in 2023, and
   FastF1's source now needs a paid F1 TV subscription. The sample is 2023 to 2025,
   so results cannot be tested across rule changes, and deep-learning models have
   less data to learn from.
3. **Unofficial source.** OpenF1 is a community project, not affiliated with
   Formula 1. Data can change or disappear. Raw and processed lap tables are not
   committed or published.
4. **Rebuilt fields.** Track status, in-laps and deleted laps are rebuilt from
   race-control messages and lap flags (methodology section 3). Message wording
   may differ from what the rules expect; the coverage report counts unmatched
   and unpaired messages, and these need checking on real races.
5. **Race distance.** Without a hand-checked value, `scheduled_laps` is the
   winner's lap count, which is wrong for shortened races and leaks a little
   end-of-race information. Fill `data/reference/scheduled_laps.csv` for those.
6. **Round numbers** are the order of races held, not necessarily official rounds.
7. **Tyre life of used sets** includes laps from earlier sessions.
8. **No gaps to other cars yet.** Traffic and dirty air are not measured. OpenF1
   `intervals` could add this later.
9. **Weather is session-level**, sampled about once a minute at one station.
10. **Hindsight flags** (`flag_deleted`, `flag_pace_outlier`) are used only to pick
    the scored sample. Reported errors apply to normal green-flag laps, not every lap.
11. **Pit timing is chosen,** not random, which biases simple tyre-age slopes (see
    methodology section 9).
