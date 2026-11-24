"""Run validate -> clean -> features -> audit over every raw session on disk."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Iterable

import pandas as pd

from . import audit, config, features
from .clean import clean_session
from .ingest import iter_raw_sessions, load_raw_session
from .validate import summarise, validate_session

log = logging.getLogger(__name__)


def build(seasons: Iterable[int] | None = None, raw_root: Path | None = None,
          processed_root: Path | None = None, reports_root: Path | None = None,
          manifest_root: Path | None = None) -> dict:
    processed_root = processed_root or config.PROCESSED
    processed_root.mkdir(parents=True, exist_ok=True)
    validation, frames = [], []
    for sdir in iter_raw_sessions(raw_root, seasons):
        raw = load_raw_session(sdir)
        rep = validate_session(raw)
        validation.append(rep)
        if not rep["passed"]:
            log.warning("Excluded %s R%s (validation errors)", rep["season"], rep["round"])
            continue
        frames.append(clean_session(raw))

    clean = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    feats = features.build_features(clean) if not clean.empty else pd.DataFrame()
    if not clean.empty:
        clean.to_parquet(processed_root / "laps_clean.parquet", index=False)
        feats.to_parquet(processed_root / "features_next_lap.parquet", index=False)

    manifest_root = manifest_root or config.MANIFESTS
    manifests = [json.loads(p.read_text()) for p in sorted(manifest_root.glob("ingest_*.json"))]
    if seasons:
        manifests = [m for m in manifests if m["season"] in set(seasons)]
    cov = audit.coverage_tables(clean, manifests, validation)
    report = audit.write_report(cov, summarise(validation), reports_root)
    return {"clean_rows": len(clean), "feature_rows": len(feats),
            "sessions_validated": len(validation),
            "sessions_passed": sum(v["passed"] for v in validation), "report": str(report)}
