# Website and repository audit, 2026-11-24

Scope: the live site as deployed from commit `c8a07f1`, rebuilt locally from the
repository with its real exported data (`web/public/data`, 69 races) and checked in
Chrome at 1280 px and 390 px; the React code in `web/src`; the export pipeline
(`webexport/`); research artifacts in `research/results`; docs; tests; the Pages
workflow. The test set was not touched: no model was rerun.

Status: **fixed** in this round, **deferred** to a later round (with the reason).

## Critical defects

| # | finding | file | evidence | change | status |
|---|---|---|---|---|---|
| C1 | Report tables unreadable: wide tables squeezed into a 70-character column, letters stacked one per line | `web/src/styles.css` (`.prose { overflow-wrap: anywhere }` inside `section { max-width: 70ch }`) | Data page screenshot: column headers broken into single letters | Tables scroll sideways inside their own frame; cells do not wrap | fixed |
| C2 | Comparison chart cut off its own labels ("TCN vs XGBoost…" lost its first letters) | `components/IntervalChart.jsx` (fixed 250 px label column) | Next-lap page screenshot | Label column sized to the longest label | fixed |
| C3 | "out" shown for lapped cars (COL, GAS, HAD, LAW at Abu Dhabi 2025) | `webexport/export.py`, `StintChart.jsx` | Your screenshot; finishing status was inferred from lap count | Official classification from OpenF1 results (fixed in v2, verified: all 20 cars "classified") | fixed |
| C4 | Task 1 results did not load ("Not exported yet") | `webexport/export.py` | `NaN` in `metrics.json` is not valid JSON in browsers | NaN/inf written as null; test added | fixed |

## Research integrity issues

| # | finding | file | evidence | change | status |
|---|---|---|---|---|---|
| R1 | The backtest's absolute-time error was presented as if it bounded strategy gaps ("differences smaller than these errors are not separable") | `simulation/backtest.py`, `research/results/simulator/backtest.md`, simulator page note | The 35 s MAE is error in absolute remaining time; most of it is shared by plans for the same driver and cancels in a comparison | Wording corrected everywhere; the strategy-specific part (fresh-tyre bias, about 1-2 s per extra stop) is now the caveat shown in every duel. Logged in `docs/model_changes.md`; no number changed | fixed |
| R2 | `docs/limitations.md` opened with Phase 1 text ("No real data processed yet") | `docs/limitations.md` | File header said "(Phase 1)" | Rewritten for the current state; sample counts point to `coverage.json` as the single source | fixed |
| R3 | README status was stale: Phase 2 "tested on synthetic races", final tests and Tasks 2-3 missing, "70 races" while the sample has 69 (Miami 2025 excluded) | `README.md` | Status table | Rewritten: findings with sources, status, architecture, licensing; counts deferred to the coverage report | fixed |
| R4 | Simulator showed "share faster" for plans that differ by one lap (57% for a −0.0 s gap) with no warning | `pages/Simulator.jsx` | Screenshot, Abu Dhabi ALB lap 21 | Deterministic explanation: "no reliable winner" when the gap is under 1 s and the 90% range spans zero; duplicates marked | fixed |
| R5 | Single-car limitation not visible where it bites (Monaco: model prefers a 1-stop by 18 s over Leclerc's winning no-stop race) | `lib/explain.js` | Browser check of a shared link | Track-position caveat in every explanation | fixed |
| R6 | Development and test results are mixed only in the Methods document list | `pages/Methods.jsx` | Development reports sit next to test reports | Labelled "Development results"; result pages show test results only | fixed (labels); a dedicated model arena is deferred |
| R8 | `docs/methodology_models.md` still said "code written and tested on synthetic races; no model has been run on the real data" | `docs/methodology_models.md` | File header | Header rewritten with the actual status and result paths | fixed (round 2) |
| R7 | GitHub description "A personal Project" | repository settings | GitHub page | Needs the owner: Settings → General → Description (text in the final report) | owner action |

## Usability issues

| # | finding | change | status |
|---|---|---|---|
| U1 | Simulator needed a "Run" click, results lost on any change, no way to share or reset | Results update automatically; scenario kept in the URL; copy link; reset | fixed |
| U2 | No way to compare two plans directly | Strategy duel: pick A and B, expected times, gap, 90% range, share of races, distribution | fixed |
| U3 | Season had to be found in a long race list | Season control, then Grand Prix | fixed |
| U4 | Charts unreadable on phones (820 px charts scaled to 340 px) | Minimum chart width with sideways scroll; simulator stacks configuration, duel, visuals, details | fixed |
| U5 | No downloads | CSV of derived results, Markdown summary, PNG of timeline and distribution | fixed |
| U6 | Methods documents could not be linked | `?doc=` in the Methods URL | fixed |
| U7 | A shared link pasted into a tab that already shows the simulator changes the address but not the page (same route, no reload) | Opening the link normally works; a reload fixes the edge case | deferred: low impact |

## Visual design weaknesses

| # | finding | change | status |
|---|---|---|---|
| V1 | Generic look; two type families, no numeric face; card and heading hierarchy flat | Token system in `web/src/tokens.css` (canvas #F5F6F3, graphite #14202C, racing red #C9363E for interaction only, steel #47778A), Space Grotesk / Inter / JetBrains Mono with tabular figures | fixed |
| V2 | Home page led with a large title and a static chart | Graphite hero with the brief's headline, actions and a live simulator case (actual vs model plan with its 90% range); sample counts from `coverage.json`; six short sections | fixed |
| V3 | Tyre chart end labels overlapped (Medium/Hard) | Labels spaced at least 15 px apart | fixed |
| V4 | Medium bars used white text on yellow (low contrast) | Dark text on medium; S/M/H marks in legends | fixed |
| V5 | Soft compound red and the interaction red are close | Interaction red is used only for buttons, active navigation, the selected point and changed segments; compounds always carry S/M/H | accepted trade-off |

## Performance

| # | finding | change | status |
|---|---|---|---|
| P1 | One 118 kB (gzip) bundle including the Markdown renderer on every page | Pages load on demand; the home bundle is 74 kB gzip, the renderer loads only with reports | fixed |
| P2 | Simulator recomputation: about 90-150 ms for the optimiser plus 110-130 ms for 1,000 races (measured on three real races) | Slider updates deferred so dragging stays smooth | fixed |
| P3 | Data: 3.0 MB of JSON, fetched per race (about 40 kB each) | Acceptable; cached by the browser | no change |

## Round 2 (Priority 3), 2026-11-24

| feature | files | data behind it | status |
|---|---|---|---|
| Model arena: ranked chart, MAE / RMSE / median / bias switch, 95% intervals where computed, locked test and development on separate tabs, model detail panels (family, objective, inputs, validation, metrics, seed spread, frozen settings, strengths, limits), "when does complexity stop paying" summary | `pages/Models.jsx`, `components/ModelRanking.jsx`, `models.js` | `final_test.json`, `final_test_meta.json`, `phase2_dev.json`, `phase3_dev.json` | done |
| Evidence inspector (source, evaluation period, pre-registration hash, run date, sample, metric, interval method, method doc) | `components/Evidence.jsx` | the same artifacts | done on the model arena and tyre lab; the simulator has its own evidence table |
| Error by tyre age, by race, quantiles, signed-error histogram from the stored test predictions (descriptive; nothing refitted or rescored) | `webexport/export.py` (`test_errors`), `components/BinLines.jsx` | `research/results/final_test/predictions.parquet` (local, git-ignored) | done; appears after the next export |
| Tyre lab: compound filter, laps-per-age bars, specification groups (main, season, robustness, naive), circuit ranking with search and sort, forecast error by tyre age | `pages/Tyres.jsx`, `components/DotCI.jsx`, `components/TyreCurves.jsx` | `task3.json`, `tyre_curves.json`, `test_errors.json` | done |
| Race explorer: season and Grand Prix selection, race overview, weather medians and ranges, neutralisation shares, lap completeness, stint chart, driver table with classification and a link into the simulator | `pages/Races.jsx`, `webexport/export.py` (`race_context`) | race files; weather and flags aggregated from `laps_clean.parquet` (local) | done; conditions appear after the next export |

Tests added: `tests/test_webexport.py` (test-error aggregates sum back to the overall error and carry no lap values; race context has no lap times).

## Still deferred

1. Featured race case study (Priority 4).
2. Research reliability page: needs `simulation/backtest.py` to also write JSON so the numbers load from an artifact.
3. Per-circuit tyre curves (needs a new Task 3 export; the circuit slopes are already shown).
4. Pasting a shared simulator link into a tab already on the simulator needs a reload (U7).
