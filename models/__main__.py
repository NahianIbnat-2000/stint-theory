"""python -m models dev|deep [--quick]   |   python -m models test  (locked)"""
from __future__ import annotations

import argparse
import logging


def main(argv=None):
    p = argparse.ArgumentParser(prog="models")
    p.add_argument("command", choices=["dev", "deep", "test", "horizon"])
    p.add_argument("--quick", action="store_true", help="smoke test: small grids, 2 folds")
    p.add_argument("--seeds", type=int, default=None,
                   help="seeds per neural model (default 5 for deep, 3 for horizon)")
    p.add_argument("--force", action="store_true",
                   help="test only: rerun after a logged crash (pre-registration section 7)")
    p.add_argument("-v", "--verbose", action="store_true")
    a = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO if a.verbose else logging.WARNING,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    if a.command == "dev":
        from .run import run_dev
        print(run_dev(quick=a.quick))
    elif a.command == "horizon":
        from .horizon_run import run_horizon_dev
        print(run_horizon_dev(quick=a.quick, n_seeds=a.seeds or 3))
    elif a.command == "deep":
        from .deep_run import run_deep
        print(run_deep(quick=a.quick, n_seeds=a.seeds or 5))
    else:
        from .final_test import run_test
        print(run_test(force=a.force))


if __name__ == "__main__":
    main()
