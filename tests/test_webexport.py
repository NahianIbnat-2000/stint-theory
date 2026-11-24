"""Website export and Python/JavaScript simulator parity. SIMULATED DATA ONLY."""
import json
import os
import shutil
import subprocess

import pytest

from simulation import params
from test_simulation import build_laps
from webexport.export import export_sim
from webexport.parity import write_parity


@pytest.fixture(scope="module")
def web(tmp_path_factory):
    root = tmp_path_factory.mktemp("web")
    lp = root / "laps.parquet"
    build_laps().to_parquet(lp, index=False)
    params.build_all(lp, out=root / "sim", log=lambda *a: None)
    export_sim(root / "sim", root / "data", log=lambda *a: None)
    return root


def test_export_has_no_lap_times(web):
    p = json.loads(next((web / "data" / "sim" / "races").glob("*.json")).read_text())
    d = next(iter(p["drivers"].values()))
    assert set(d) == {"stints", "stops", "finished", "last_lap", "status", "states"}
    assert "lap_time_s" not in json.dumps(p)
    assert len(d["states"]["mu"]) == len(d["states"]["lap"]) > 0


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_javascript_matches_python(web):
    ref = write_parity(web / "data", web / "parity.json")
    assert json.loads(ref.read_text())["cases"]
    test_file = os.path.join(os.path.dirname(__file__), "..", "web", "test", "parity.test.mjs")
    env = {**os.environ, "STINT_WEB_DATA": str(web / "data"), "STINT_PARITY": str(ref)}
    r = subprocess.run(["node", "--test", test_file], capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stdout + r.stderr


def test_nan_becomes_null(tmp_path):
    from webexport.export import copy_json
    src = tmp_path / "a.json"
    src.write_text('{"a": NaN, "b": [1.5, Infinity], "c": "x"}')
    copy_json(src, tmp_path / "b.json")
    assert json.loads((tmp_path / "b.json").read_text()) == {"a": None, "b": [1.5, None], "c": "x"}


def test_test_errors_aggregates_only():
    import numpy as np
    import pandas as pd
    from webexport.export import test_errors
    rng = np.random.default_rng(0)
    n = 400
    pred = pd.DataFrame({"race_id": rng.choice(["2025_13", "2025_14"], n), "target_tyre_life": rng.integers(1, 50, n),
                         "y": rng.normal(0, 1, n)})
    pred["pred_a"] = pred["y"] + rng.normal(0, 0.3, n)
    pred["pred_b"] = pred["y"] + rng.normal(0, 0.5, n)
    out = test_errors(pred)
    assert out["models"] == ["a", "b"] and out["n_laps"] == n
    assert sum(r["n"] for r in out["by_tyre_age"]) == n
    total = sum(r["n"] * r["mae"]["a"] for r in out["by_race"]) / n
    assert abs(total - (pred["pred_a"] - pred["y"]).abs().mean()) < 1e-9
    h = out["signed_error_hist"]["counts"]["b"]
    assert sum(h["inside"]) + h["below"] + h["above"] == n
    assert "y" not in json.dumps(out["by_race"])


def test_race_context(web):
    from webexport.export import race_context
    laps = build_laps()
    ctx = race_context(laps, {})
    r = next(iter(ctx.values()))
    assert r["drivers"] == 8 and r["pit_stops"] > 0
    assert set(r) >= {"track_temp_c", "sc_lap_share", "lap_completeness"}
    assert "lap_time_s" not in json.dumps(ctx)
