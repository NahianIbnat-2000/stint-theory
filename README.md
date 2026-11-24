# STINT THEORY

**Every Lap Is Data. Every Pit Stop Is a Decision.**

An open research project asking whether deep learning forecasts Formula 1 lap times
and tyre-related pace loss better than statistical and standard machine-learning
models, and whether better forecasts lead to better modelled strategy decisions.

STINT THEORY is an independent educational and research project. It is not
affiliated with or endorsed by Formula 1, the FIA, Pirelli, any team, or their
rights holders.

## Status

| phase | what | status |
|---|---|---|
| 1 | Data pipeline: ingest (OpenF1, 2023 to 2025), validate, clean, features, coverage audit | **Done.** 70 races, 77,373 driver-laps, 60,701 clean green laps. See `data/reports/coverage_report.md`. |
| 2 | Benchmarks, ridge, mixed-effects, random forest, XGBoost; locked test set | **Code done and tested on synthetic races.** Development results: `research/results/phase2_dev/report.md` after `python -m models dev`. |
| 3 | MLP, LSTM, TCN on the same design | **Development done.** Neural models tie XGBoost within about 0.005 s; the lap sequence adds nothing measurable. Final test pre-registered in `docs/preregistration.md`. |
| 4 | Strategy simulator | planned |
| 5 | Website | planned |
| 6 | Publication and deployment | planned |

Development results are in `research/results/phase2_dev/` and `phase3_dev/`
(2025 rounds 1-12). The 2025 rounds 13-24 test set is locked in code and is scored
once, under the rules in `docs/preregistration.md`.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate            # Windows Git Bash: source .venv/Scripts/activate
pip install -r requirements-dev.txt
python -m pytest -q                  # all tests run offline

# Feasibility run: three races from one season (about 1 minute)
python -m pipelines ingest --seasons 2023 --rounds 1-3 -v
python -m pipelines build --seasons 2023
python -m pipelines diagnose --seasons 2023
# -> data/reports/coverage_report.md and data/reports/diagnostics.md

# Full sample, 2023 to 2025 (roughly 25 minutes the first time; responses are cached)
python -m pipelines all --seasons 2023-2025 -v
```

Data comes from the free OpenF1 historical API. No account or key is needed.
Requests are spaced 2.1 s apart to stay inside the free tier. Set `STINT_CACHE`
to keep the response cache somewhere other than `.cache/`.

### Why not FastF1

Since mid-October 2026, Formula 1's timing archive (FastF1's source) requires a
paid F1 TV subscription, and GitHub Actions runners are blocked from it. That
breaks the zero-cost rule, so the pipeline reads OpenF1 instead. The price is a
shorter sample: 2023 to 2025 only.

### Run in GitHub Actions instead

Actions → **ingest** → Run workflow, enter seasons (and optionally rounds). Not yet
tested from Actions. The job caches OpenF1 responses between runs, uploads the processed tables as a private
build artifact for 30 days, and commits only the manifests and reports.

## Pipeline

```
OpenF1 ──ingest──> data/raw/<season>/R<nn>_<event>/   (Parquet + session_meta.json)
                      │
                  validate ──> errors exclude a race; warnings become row flags
                      │
                    clean ───> data/processed/laps_clean.parquet   (no rows dropped)
                      │
                  features ──> data/processed/features_next_lap.parquet
                      │
                    audit ───> data/reports/coverage_report.md, coverage.json
```

| module | job |
|---|---|
| `pipelines/openf1.py` | OpenF1 client (throttle, retries, JSON cache) and the adapter that rebuilds stints, in-laps, track status, deleted laps and positions. |
| `pipelines/ingest.py` | Download race sessions, store tables, write provenance (session key, time, row counts, SHA-256, reconstruction checks). Skips races already on disk. |
| `pipelines/validate.py` | Schema, duplicates, lap and stint consistency, tyre-life steps, sector sums, scheduled distance. |
| `pipelines/clean.py` | Harmonised driver-lap table with quality and exclusion flags. |
| `pipelines/features.py` | Next-lap features under a strict information rule, plus the target. |
| `pipelines/audit.py` | Coverage and quality report. |
| `pipelines/schema.py` | Data dictionary source; generates `docs/data_dictionary.md`. |

## Models (Phase 2)

```bash
python -m models dev --quick -v   # smoke test on the real data, a few minutes
python -m models dev -v           # full run: tuning on 2024 + 12 development races
python -m models deep --quick -v  # Phase 3 smoke test
python -m models deep -v          # Phase 3 full run (needs the Phase 2 predictions)
# final test: once, after committing docs/preregistration.md
STINT_UNLOCK_TEST=I_HAVE_FROZEN_ALL_MODELS python -m models test -v
```

See [docs/methodology_models.md](docs/methodology_models.md) for the split, the
reference pace, each model and how they are compared.

## Documentation

- [Methodology](docs/methodology.md): sample, cleaning rules, information rule, why lap time is not tyre wear.
- [Data dictionary](docs/data_dictionary.md)
- [Limitations](docs/limitations.md)
- [data/README.md](data/README.md): what is and is not committed.

## Tests

`python -m pytest -q` covers validation, track-status parsing, compound mapping,
weather alignment, flagging without dropping, the OpenF1 client (cache, retries,
empty results), the OpenF1 adapter against a race with known stints, pit stops,
safety car and a deleted lap, race-control period rules, an end-to-end build, documentation of every column, and leakage. The leakage test
changes the future and checks that features do not move; a second test plants a
leak and checks that the first test catches it.

## Licence

Code: MIT (see `LICENSE`). Formula 1 timing data (via OpenF1) is not covered by
this licence and is not redistributed here.
