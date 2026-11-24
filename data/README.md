# data/

| folder | in git? | contents |
|---|---|---|
| `raw/` | no | One folder per race: tables built from OpenF1 as Parquet plus `session_meta.json` (OpenF1 session key, retrieval time, row counts, SHA-256 of each file, reconstruction checks, errors). |
| `processed/` | no | `laps_clean.parquet` (one row per driver-lap, nothing dropped, all flags kept) and `features_next_lap.parquet` (one row per prediction origin). |
| `manifests/` | yes | `ingest_<season>.json`: which races were requested, downloaded, skipped or failed. |
| `reports/` | yes | `coverage_report.md`, `coverage.json`, `validation_issues.csv`. |
| `schemas/` | yes | `columns.json`, generated from `pipelines/schema.py`. |
| `reference/` | yes | `scheduled_laps.csv`: race distances checked by hand. |

Raw and processed lap tables stay out of the repository because the timing data
belongs to Formula 1 and its data partners (served here through OpenF1). Anyone can rebuild them with
`python -m pipelines all`. The website (`web/public/data`, written by `python -m webexport`) publishes derived
results and small aggregates only: model parameters, tyre stints and pit-stop laps, and
per-lap decision states whose pace term is an average over up to 30 laps. No lap times.

## Note on an early commit

Commit `f8f82ca` ("Phase 4: strategy simulator") briefly placed per-driver lap
histories and per-stop rows in `research/results/simulator/`. They were removed
from the repository in the next commit and are now written to the git-ignored
`data/processed/simulator/`. Git history was not rewritten, because the
pre-registered test reports cite commit hashes that a rewrite would change.
