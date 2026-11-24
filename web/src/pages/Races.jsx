import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useData } from "../data.js";
import { fmt } from "../format.js";
import StintChart, { compoundInfo } from "../components/StintChart.jsx";
import { encodeScenario } from "../lib/scenario.js";

const pct = (x, d = 1) => (x == null ? "–" : `${fmt(100 * x, d)}%`);
const range = (r, unit) => (r ? `${fmt(r.median, 1)} ${unit} (${fmt(r.min, 1)}–${fmt(r.max, 1)})` : "–");

export default function Races() {
  const [params, setParams] = useSearchParams();
  const idx = useData("sim/index.json");
  const races = useMemo(() => [...(idx.data || [])].sort((a, b) => a.season - b.season || a.round - b.round), [idx.data]);
  const seasons = [...new Set(races.map((r) => r.season))];
  const [raceId, setRaceId] = useState(params.get("race"));
  useEffect(() => { if (races.length && !races.some((r) => r.race_id === raceId)) setRaceId(races.at(-1).race_id); }, [races, raceId]);
  useEffect(() => { if (raceId) setParams({ race: raceId }, { replace: true }); }, [raceId]); // eslint-disable-line react-hooks/exhaustive-deps
  const meta = races.find((r) => r.race_id === raceId);
  const q = useData(raceId ? `sim/races/${raceId}.json` : null);
  const race = q.data?.race_id === raceId ? q.data : null;
  const [focus, setFocus] = useState(null);
  const c = race?.context;
  const N = race?.total_laps;

  return (
    <div className="page">
      <header className="page-head">
        <h1>Race explorer</h1>
        <p className="lede">Every race in the sample: who ran which tyres when, the conditions, and how much of the race the
          data covers. Open any dry race in the strategy simulator from here.</p>
      </header>
      <div className="controls">
        <div className="field" role="group" aria-label="Season">
          <span className="field-label">Season</span>
          <div className="segmented">
            {seasons.map((s) => <button key={s} aria-pressed={meta?.season === s} onClick={() => setRaceId(races.filter((r) => r.season === s).at(-1).race_id)}>{s}</button>)}
          </div>
        </div>
        <label className="field">Grand Prix
          <select value={raceId || ""} onChange={(e) => setRaceId(e.target.value)}>
            {races.filter((r) => r.season === meta?.season).map((r) => <option key={r.race_id} value={r.race_id}>Round {r.round}: {r.event_name}{r.simulatable ? "" : " (wet)"}</option>)}
          </select>
        </label>
      </div>

      {!race ? <div className="skeleton" /> : (
        <>
          <section className="wide" aria-labelledby="ov-h">
            <h2 id="ov-h" style={{ marginTop: "var(--space-5)" }}>{race.season} {race.event_name}
              {" "}<span className={`chip ${race.simulatable ? "ok" : "warn"}`}>{race.simulatable ? "in the simulator" : "wet: not simulated"}</span></h2>
            <div className="overview">
              <div className="stat"><b className="mono">{N}</b><span>laps</span></div>
              {c && <div className="stat"><b className="mono">{c.drivers}</b><span>drivers</span></div>}
              {c && <div className="stat"><b className="mono">{c.pit_stops}</b><span>pit stops</span></div>}
              <div className="stat"><b className="mono">{pct(c?.lap_completeness ?? null)}</b><span>laps recorded</span></div>
              <div className="stat"><b className="mono">{pct(race.dry_slick_share, 0)}</b><span>laps on slick tyres</span></div>
              {c && <div className="stat"><b className="mono">{pct(c.sc_lap_share)} / {pct(c.vsc_lap_share)}</b><span>laps under safety car / VSC</span></div>}
              {c && <div className="stat"><b className="mono">{pct(c.red_lap_share)}</b><span>laps under red flag</span></div>}
              {c && <div className="stat"><b className="mono">{pct(c.clean_green_share, 0)}</b><span>clean green-flag laps</span></div>}
            </div>
            {c ? (
              <p className="note">Track {range(c.track_temp_c, "°C")}; air {range(c.air_temp_c, "°C")}; humidity {range(c.humidity_pct, "%")};
                wind {range(c.wind_speed_ms, "m/s")}; rain reported on {pct(c.rain_lap_share)} of laps. Median and range over the race, from OpenF1 weather samples (one station, about once a minute).</p>
            ) : <p className="note">Conditions and coverage figures appear after the next <code>python -m webexport</code>.</p>}
            {race.rules.note && <p className="note">Race rule: {race.rules.note}.</p>}
            {c?.lap_completeness != null && c.lap_completeness < 1 && <p className="missing">{pct(1 - c.lap_completeness)} of expected driver-laps are missing from the source for this race.</p>}
          </section>

          <section className="wide" aria-labelledby="st-h">
            <h2 id="st-h">Tyre strategy, driver by driver</h2>
            <StintChart race={race} highlight={focus} onPick={(d) => setFocus(focus === d ? null : d)} />
          </section>

          <section className="wide" aria-labelledby="dr-h">
            <h2 id="dr-h">Drivers</h2>
            <div className="table-wrap">
              <table>
                <thead><tr><th>Driver</th><th>Tyres (laps)</th><th className="num">Stops</th><th>Classification</th><th>Simulator</th></tr></thead>
                <tbody>
                  {Object.entries(race.drivers).sort((a, b) => b[1].last_lap - a[1].last_lap || a[0].localeCompare(b[0])).map(([d, v]) => {
                    const s = v.states;
                    const i = s.lap.findIndex((l) => l >= Math.round(N / 3));
                    const lap = i >= 0 ? s.lap[i] : s.lap[0];
                    return (
                      <tr key={d} className={focus === d ? "highlight" : undefined}>
                        <td><button className="link" onClick={() => setFocus(focus === d ? null : d)}>{d}</button></td>
                        <td className="mono" style={{ fontSize: ".85rem" }}>{v.stints.map(([cmp, a, b]) => `${compoundInfo(cmp).short} ${a}–${b}`).join("  ·  ")}</td>
                        <td className="num">{v.stops.filter(([l]) => l < N).length}</td>
                        <td>{v.status === "classified" ? "Classified" : v.status ? v.status.toUpperCase() : "–"}</td>
                        <td>{race.simulatable && s.lap.length
                          ? <Link to={`/simulator?${encodeScenario({ race: race.race_id, driver: d, lap })}`}>Decide at lap {lap}</Link>
                          : <span className="muted">{race.simulatable ? "too few clean laps" : "wet race"}</span>}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            <p className="note">Stops counted from pit-entry laps before the finish. Tyre stints come from OpenF1 stint records; lap times are not published here.</p>
          </section>
        </>
      )}
    </div>
  );
}
