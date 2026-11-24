"""OpenF1 client, adapter and end-to-end build. No network: a fake client serves
payloads made from the synthetic race, whose true structure is known."""
import json

import numpy as np
import pandas as pd
import pytest

from openf1_fixture import DELETED, T0, FakeClient
from pipelines import build as build_mod
from pipelines import ingest, openf1
from pipelines.__main__ import parse_range
from pipelines.clean import clean_session, parse_track_status
from pipelines.features import build_features
from pipelines.schema import all_columns


@pytest.fixture
def ingested(tmp_path):
    client = FakeClient()
    raw_root, man = tmp_path / "raw", tmp_path / "manifests"
    ingest.run_ingest([2023], client=client, raw_root=raw_root, manifest_root=man)
    return client, raw_root, man, tmp_path


def _adapter_vs_truth(ingested):
    client, raw_root, _, _ = ingested
    got = ingest.load_raw_session(raw_root / "2023" / "R01_test_1_grand_prix")
    truth = client.races[202301][2]["_raw"]
    key = ["DriverNumber", "LapNumber"]
    return (got, got["laps"].sort_values(key).reset_index(drop=True),
            truth["laps"].sort_values(key).reset_index(drop=True))


def test_sprints_are_excluded_and_rounds_ordered(ingested):
    _, _, man, _ = ingested
    m = json.loads((man / "ingest_2023.json").read_text())
    assert m["races_listed"] == 2
    assert [s["round"] for s in m["sessions"]] == [1, 2]
    assert all(s["status"] == "downloaded" for s in m["sessions"])


def test_adapter_reproduces_known_race(ingested):
    got, g, t = _adapter_vs_truth(ingested)
    assert len(g) == len(t)
    assert (g.Driver == t.Driver).all() and (g.Team == t.Team).all()
    np.testing.assert_allclose(g.LapTime.dt.total_seconds(), t.LapTime.dt.total_seconds(), atol=1e-6)
    np.testing.assert_allclose(g.LapStartTime.dt.total_seconds(),
                               t.LapStartTime.dt.total_seconds(), atol=1e-3)
    assert (g.Stint == t.Stint).all()
    assert (g.Compound.astype(str) == t.Compound.astype(str)).all()
    assert (g.TyreLife == t.TyreLife).all()
    assert (g.PitOutTime.notna() == t.PitOutTime.notna()).all()
    assert (g.PitInTime.notna() == t.PitInTime.notna()).all()
    assert (g.Position == t.Position).all()
    pd.testing.assert_series_equal(parse_track_status(g.TrackStatus)["flag_sc"],
                                   parse_track_status(t.TrackStatus)["flag_sc"])


def test_reconstruction_checks_recorded(ingested):
    got, _, _ = _adapter_vs_truth(ingested)
    c = got["meta"]["checks"]
    assert c["laps_without_stint"] == 0
    assert c["pit_table_rows"] == c["pit_rows_on_inferred_in_lap"] == 4
    assert c["sc_unpaired"] == 0 and c["deleted_laps"] == 1
    assert got["meta"]["scheduled_laps"] == 30
    assert got["meta"]["scheduled_laps_source"] == "winner_laps_actual"


def test_cleaned_adapter_output_matches_cleaned_truth(ingested):
    client, raw_root, _, _ = ingested
    got = clean_session(ingest.load_raw_session(raw_root / "2023" / "R01_test_1_grand_prix"))
    truth = clean_session(client.races[202301][2]["_raw"])
    cols = ["flag_pit_in", "flag_pit_out", "flag_sc", "flag_post_neutralisation", "flag_first_lap"]
    key = ["driver", "lap_number"]
    pd.testing.assert_frame_equal(got.sort_values(key)[cols].reset_index(drop=True),
                                  truth.sort_values(key)[cols].reset_index(drop=True))
    d = got.set_index(["driver_number", "lap_number"])
    assert d.loc[(DELETED[0], DELETED[1]), "flag_deleted"]
    assert d["flag_deleted"].sum() == 1
    assert d["grid_position"].notna().all()


def test_end_to_end_build(ingested):
    _, raw_root, man, tmp = ingested
    out = build_mod.build([2023], raw_root=raw_root, processed_root=tmp / "proc",
                          reports_root=tmp / "rep", manifest_root=man)
    assert out["sessions_passed"] == 2 and out["clean_rows"] == 240
    cov = json.loads((tmp / "rep" / "coverage.json").read_text())
    assert cov["by_season"]["2023"]["races_in_sample"] == 2
    assert "reconstruction_checks" in cov
    assert (tmp / "rep" / "coverage_report.md").exists()


def test_rerun_skips_existing(ingested):
    client, raw_root, man, _ = ingested
    before = client.calls
    ingest.run_ingest([2023], client=client, raw_root=raw_root, manifest_root=man)
    assert client.calls - before == 2  # only sessions + meetings listing
    m = json.loads((man / "ingest_2023.json").read_text())
    assert all(s["status"] == "skipped_existing" for s in m["sessions"])


def test_scheduled_laps_reference_overrides(tmp_path):
    assert openf1.scheduled_laps([{"position": 1, "number_of_laps": 44}], None) == (44, "winner_laps_actual")
    assert openf1.scheduled_laps([{"position": 1, "number_of_laps": 44}], 57) == (57, "reference_file")
    assert openf1.scheduled_laps([], None) == (None, "missing")
    ref = tmp_path / "s.csv"
    ref.write_text("# note\nseason,round,event_name,scheduled_laps,source_url\n2023,1,X,57,u\n2023,2,Y,,\n")
    assert ingest.load_scheduled_laps_reference(ref) == {(2023, 1): 57}


# ---------------------------------------------------------------- race control
def _rc(t, message="", flag=None, scope=None, sector=None, category="Other"):
    return {"date": (T0 + pd.Timedelta(seconds=t)).isoformat(), "message": message,
            "flag": flag, "scope": scope, "sector": sector, "category": category}


def test_race_control_intervals():
    rc = [
        _rc(100, "VIRTUAL SAFETY CAR DEPLOYED", category="SafetyCar"),
        _rc(160, "VIRTUAL SAFETY CAR ENDING", category="SafetyCar"),
        _rc(300, "YELLOW IN TRACK SECTOR 7", "YELLOW", "Sector", 7),
        _rc(330, "CLEAR IN TRACK SECTOR 7", "CLEAR", "Sector", 7),
        _rc(400, "DOUBLE YELLOW IN TRACK SECTOR 3", "DOUBLE YELLOW", "Sector", 3),
        _rc(1000, "RED FLAG", "RED", "Track"),
        _rc(2000, "GREEN LIGHT - PIT EXIT OPEN", "GREEN", "Track"),
        _rc(2100, "SAFETY CAR DEPLOYED", category="SafetyCar"),
        _rc(2200, "SAFETY CAR THROUGH THE PIT LANE", category="SafetyCar"),
        _rc(2300, "SAFETY CAR BLUE MOON", category="SafetyCar"),
    ]
    iv, st = openf1.race_control_intervals(rc, T0, 9000)
    got = {(r.code, r.start_s, r.end_s) for r in iv.itertuples()}
    assert ("6", 100, 160) in got           # VSC is not mistaken for SC
    assert ("2", 300, 330) in got           # sector yellow closed by its clear
    assert ("2", 400, 700) in got           # unclosed yellow capped at 300 s
    assert ("5", 1000, 2000) in got         # red until track green
    assert ("4", 2100, 9000) in got         # unpaired SC runs to session end
    assert not any(c == "4" and s == 100 for c, s, _ in got)
    assert st["sc_unpaired"] == 1 and st["yellow_capped"] == 1
    assert st["safetycar_msgs_unmatched"] == 1  # only the unknown wording is surfaced


def test_lap_track_status_overlap():
    iv = pd.DataFrame({"start_s": [50.0], "end_s": [150.0], "code": ["4"], "source": ["sc"]})
    s = openf1.lap_track_status(pd.Series([0.0, 90.0, 150.0, np.nan]),
                                pd.Series([60.0, 180.0, 240.0, 1.0]), iv)
    assert s.tolist()[:3] == ["14", "14", "1"] and pd.isna(s.iloc[3])


def test_deleted_and_reinstated():
    rc = [_rc(10, "CAR 44 (HAM) TIME 1:32.100 DELETED - TRACK LIMITS AT TURN 4 LAP 23 15:03:12"),
          _rc(20, "CAR 1 (VER) TIME 1:31.000 DELETED - TRACK LIMITS AT TURN 9 LAP 5 15:04:00"),
          _rc(30, "CAR 1 (VER) LAP 5 TIME 1:31.000 REINSTATED")]
    assert openf1.deleted_laps(rc) == {("44", 23)}


# ---------------------------------------------------------------- HTTP client
class _Resp:
    def __init__(self, code, data=None, headers=None):
        self.status_code, self._data, self.headers = code, data, headers or {}

    def json(self):
        return self._data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)


class _Http:
    def __init__(self, responses):
        self.responses, self.urls = list(responses), []

    def get(self, url, timeout):
        self.urls.append(url)
        return self.responses.pop(0)


def test_client_caches_retries_and_handles_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(openf1.time, "sleep", lambda s: None)
    http = _Http([_Resp(429, headers={"Retry-After": "1"}), _Resp(200, [{"a": 1}]),
                  _Resp(404, {"detail": "No results found."})])
    c = openf1.OpenF1Client(tmp_path, min_interval_s=0, http=http)
    assert c.get("laps", session_key=1) == [{"a": 1}]
    assert c.get("laps", session_key=1) == [{"a": 1}]      # from cache
    assert c.get("pit", session_key=1) == []               # 404 means empty
    assert c.calls == 3 and c.cache_hits == 1
    assert http.urls[0] == "https://api.openf1.org/v1/laps?session_key=1"


# ---------------------------------------------------------------- misc
def test_every_output_column_is_documented():
    from fixtures import make_raw_race
    c = clean_session(make_raw_race())
    f = build_features(c)
    documented = set(all_columns())
    assert set(c.columns) <= documented, set(c.columns) - documented
    assert set(f.columns) <= documented, set(f.columns) - documented


def test_parse_range():
    assert parse_range("2023-2025") == [2023, 2024, 2025]
    assert parse_range(None) is None


def test_adapter_drops_api_duplicates_and_counts_them():
    from openf1_fixture import openf1_payloads
    p = openf1_payloads()
    laps = p["laps"] + [p["laps"][5], {**p["laps"][6], "driver_number": None}]
    iv, _ = openf1.race_control_intervals(p["race_control"], T0, 1e9)
    raw, checks = openf1.build_laps(laps, p["stints"], p["drivers"], p["pit"], p["position"],
                                    iv, set(), T0)
    assert len(raw) == 120
    assert checks["duplicate_lap_rows_dropped"] == 1
    assert checks["lap_rows_without_driver_or_lap"] == 1


def test_red_flag_closes_open_safety_car_and_sc_restart_closes_red():
    rc = [_rc(100, "SAFETY CAR DEPLOYED", category="SafetyCar"),
          _rc(200, "RED FLAG", "RED", "Track"),
          _rc(900, "SAFETY CAR DEPLOYED", category="SafetyCar"),
          _rc(1000, "SAFETY CAR IN THIS LAP", category="SafetyCar")]
    iv, st = openf1.race_control_intervals(rc, T0, 9000)
    got = {(r.code, r.start_s, r.end_s) for r in iv.itertuples()}
    assert got == {("4", 100, 200), ("5", 200, 900), ("4", 900, 1000)}
    assert st["sc_unpaired"] == st["red_unpaired"] == 0


def test_grid_fallback_uses_first_position_record():
    pos = [{"driver_number": 1, "position": 2, "date": "2023-03-05T15:00:01+00:00"},
           {"driver_number": 1, "position": 1, "date": "2023-03-05T15:10:00+00:00"},
           {"driver_number": 11, "position": 1, "date": "2023-03-05T15:00:00+00:00"}]
    g = {r["driver_number"]: r["position"] for r in openf1.grid_from_positions(pos)}
    assert g == {1: 2, 11: 1}


def test_lap_after_last_stint_end_is_attached_but_gaps_are_not():
    from openf1_fixture import openf1_payloads
    p = openf1_payloads()
    stints = [dict(s) for s in p["stints"]]
    for s in stints:
        if s["driver_number"] == 10 and s["stint_number"] == 2:
            s["lap_end"] = 29          # last lap (30) not covered: should be attached
        if s["driver_number"] == 11 and s["stint_number"] == 1:
            s["lap_end"] -= 2          # gap before stint 2: should stay missing
    iv, _ = openf1.race_control_intervals(p["race_control"], T0, 1e9)
    raw, checks = openf1.build_laps(p["laps"], stints, p["drivers"], p["pit"], p["position"],
                                    iv, set(), T0)
    assert checks["laps_stint_extended_by_one"] == 1
    assert checks["laps_without_stint"] == 2
    last = raw[(raw.DriverNumber == "10") & (raw.LapNumber == 30)].iloc[0]
    assert last.Stint == 2 and last.Compound == "HARD"


def test_diagnose_report(ingested):
    from pipelines.diagnose import diagnose
    _, raw_root, _, tmp = ingested
    p = diagnose([2023], raw_root=raw_root, out=tmp / "d.md")
    text = p.read_text()
    assert "SAFETY CAR DEPLOYED" in text and "R02" in text and "endpoint rows" in text


def test_vsc_upgraded_to_sc_is_closed():
    """British GP 2023 pattern: VSC deployed, then SC deployed, no VSC ending."""
    rc = [_rc(100, "VIRTUAL SAFETY CAR DEPLOYED", category="SafetyCar"),
          _rc(180, "SAFETY CAR DEPLOYED", category="SafetyCar"),
          _rc(800, "SAFETY CAR IN THIS LAP", category="SafetyCar")]
    iv, st = openf1.race_control_intervals(rc, T0, 9000)
    got = {(r.code, r.start_s, r.end_s) for r in iv.itertuples()}
    assert got == {("6", 100, 180), ("4", 180, 800)}
    assert st["vsc_unpaired"] == 0 and st["vsc_upgraded_to_sc"] == 1


def test_chequered_flag_closes_periods_and_nothing_opens_after():
    """Azerbaijan 2024 / Canada 2025: neutralisation still on at the flag;
    Australia 2023: a red flag after the chequered flag."""
    rc = [_rc(100, "SAFETY CAR DEPLOYED", category="SafetyCar"),
          _rc(400, "CHEQUERED FLAG", "CHEQUERED", "Track"),
          _rc(500, "RED FLAG", "RED", "Track"),
          _rc(600, "TRACK CLEAR", "CLEAR", "Track")]
    iv, st = openf1.race_control_intervals(rc, T0, 9000)
    assert {(r.code, r.start_s, r.end_s) for r in iv.itertuples()} == {("4", 100, 400)}
    assert st["sc_unpaired"] == st["red_unpaired"] == 0 and st["closed_by_chequered"] == 1


def test_restart_behind_safety_car_after_red():
    """Belgium 2025: red before the start, race starts behind the safety car,
    then 'ROLLING START'. Dutch 2023: 'SAFETY CAR WILL ENTER PITS' ends it."""
    rc = [_rc(100, "RED FLAG", "RED", "Track"),
          _rc(3000, "TRACK CLEAR", "CLEAR", "Track"),
          _rc(3600, "RACE WILL START BEHIND THE SAFETY CAR"),
          _rc(4500, "ROLLING START"),
          _rc(6000, "RED FLAG", "RED", "Track"),
          _rc(7000, "RACE WILL RESUME AT 17:14 - ROLLING START PROCEDURE"),
          _rc(7300, "TRACK CLEAR", "CLEAR", "Track"),
          _rc(7800, "SAFETY CAR WILL ENTER PITS: ROLLING START PROCEDURE"),
          _rc(7900, "SAFETY CAR THROUGH THE PIT LANE", category="SafetyCar")]
    iv, st = openf1.race_control_intervals(rc, T0, 9000)
    got = {(r.code, r.start_s, r.end_s) for r in iv.itertuples()}
    assert got == {("5", 100, 3000), ("4", 3600, 4500), ("5", 6000, 7000), ("4", 7000, 7800)}
    assert st["sc_restart_periods"] == 2 and st["safetycar_msgs_unmatched"] == 0
