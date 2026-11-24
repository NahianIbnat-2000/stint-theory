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
`python -m pipelines all`. The website will only publish derived results and
small aggregates.
