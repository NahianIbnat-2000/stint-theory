"""Command line entry point.

    python -m pipelines ingest --seasons 2023 --rounds 1-3
    python -m pipelines build  --seasons 2023
    python -m pipelines all    --seasons 2023-2025
    python -m pipelines diagnose --seasons 2023
    python -m pipelines dictionary
"""
from __future__ import annotations

import argparse
import json
import logging


def parse_range(text: str | None) -> list[int] | None:
    if not text:
        return None
    out: list[int] = []
    for part in text.split(","):
        if "-" in part:
            a, b = part.split("-")
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def main(argv=None) -> None:
    p = argparse.ArgumentParser(prog="pipelines")
    p.add_argument("command", choices=["ingest", "build", "all", "diagnose", "dictionary"])
    p.add_argument("--seasons", default="2023-2025", help="e.g. 2023 or 2023-2025 or 2023,2025")
    p.add_argument("--rounds", default=None, help="e.g. 1-3 (ingest only)")
    p.add_argument("--force", action="store_true", help="re-download sessions already on disk")
    p.add_argument("--min-interval", type=float, default=2.1,
                   help="seconds between OpenF1 requests (free tier is about 30/min)")
    p.add_argument("-v", "--verbose", action="store_true")
    a = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO if a.verbose else logging.WARNING,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    seasons = parse_range(a.seasons)

    if a.command == "diagnose":
        from .diagnose import diagnose
        print(diagnose(seasons))
        return
    if a.command == "dictionary":
        from .schema import write_docs
        print(write_docs())
        return
    if a.command in ("ingest", "all"):
        from . import config
        from .ingest import run_ingest
        from .openf1 import OpenF1Client
        client = OpenF1Client(config.CACHE, min_interval_s=a.min_interval)
        paths = run_ingest(seasons, parse_range(a.rounds), force=a.force, client=client)
        print("Manifests:", *map(str, paths), sep="\n  ")
    if a.command in ("build", "all"):
        from .build import build
        print(json.dumps(build(seasons), indent=2))


if __name__ == "__main__":
    main()
