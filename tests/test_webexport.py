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
