import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useData, fmt, signed, COMPOUND } from "../data.js";
import StintChart from "../components/StintChart.jsx";
import { simulate, summarise, stateAt, observedStrategy, describe, DISCLAIMER } from "../sim/engine.js";
import { bestByStops } from "../sim/strategy.js";
import { check, SLICKS } from "../sim/constraints.js";

const N_DRAWS = 1000;

export default function Simulator() {
  const idx = useData("sim/index.json");
  const races = useMemo(() => (idx.data || []).filter((r) => r.simulatable)
    .sort((a, b) => b.season - a.season || b.round - a.round), [idx.data]);
  const [raceId, setRaceId] = useState(null);
  useEffect(() => { if (!raceId && races.length) setRaceId(races[0].race_id); }, [races, raceId]);
  const race = useData(raceId ? `sim/races/${raceId}.json` : null).data;

  const drivers = useMemo(() => (race ? Object.keys(race.drivers).filter((d) => race.drivers[d].states.lap.length).sort() : []), [race]);
  const [driver, setDriver] = useState(null);
  useEffect(() => { if (race && !drivers.includes(driver)) setDriver(drivers[0] || null); }, [race, drivers, driver]);
  const states = race && driver ? race.drivers[driver].states : null;
  const [k, setK] = useState(0);
  useEffect(() => { if (states) setK(Math.floor(states.lap.length / 3)); }, [states]);
  const st = states && k < states.lap.length ? stateAt(race, driver, k) : null;

  const [sc, setSc] = useState("none");
  const [scLap, setScLap] = useState(null);
  const [plan, setPlan] = useState([]);
  const [res, setRes] = useState(null);
  useEffect(() => { setRes(null); }, [raceId, driver, k, sc, scLap, plan]);
  useEffect(() => { setPlan([]); setScLap(null); }, [raceId, driver]);

  const rules = race ? { min_stops: race.rules.min_stops, max_set_life: race.rules.max_set_life } : null;
  const planStrategy = { stop_laps: plan.map((p) => p.lap), compounds: plan.map((p) => p.comp) };
  const planErrors = st && plan.length ? check(planStrategy, st, rules) : [];

  const run = () => {
    const cands = [];
    const obs = observedStrategy(race, driver, st.decision_lap);
    if (obs) cands.push({ ...obs, label: "What the driver did" });
    if (plan.length && !planErrors.length) cands.push({ ...planStrategy, label: "Your plan" });
    Object.entries(bestByStops(race, st, rules, 3)).forEach(([n, s]) => cands.push({ ...s, label: `Best ${n}-stop` }));
    // the same plan reached two ways (e.g. what the driver did = best 0-stop) is shown once
    const uniq = [];
    for (const c of cands) {
      const key = `${c.stop_laps.join(",")}|${c.compounds.join(",")}`;
      const seen = uniq.find((u) => u.key === key);
      if (seen) seen.label += `; ${c.label.charAt(0).toLowerCase()}${c.label.slice(1)}`;
      else uniq.push({ ...c, key });
    }
    cands.splice(0, cands.length, ...uniq);
    const at = sc === "at_lap" ? (scLap ?? st.decision_lap + 5) : null;
    const r = simulate(race, st, cands, { n: N_DRAWS, seed: 2026, scMode: sc, scLap: at });
    setRes({ rows: summarise(r, cands), scDraws: r.scDraws, scAt: at });
  };

  if (idx.error) return <p className="missing">Simulator data not exported yet.</p>;
  return (
    <>
      <header className="page-head">
        <h1>Strategy simulator</h1>
        <p className="lede">Stand on the pit wall at any lap of a real dry race. The simulator plays out the rest of the
          race 1,000 times for each plan, with the model fitted <em>without</em> that race, and the driver’s pace taken
          only from laps already run.</p>
      </header>

      <section className="sim-controls" aria-label="Simulation settings">
        <label>Race
          <select value={raceId || ""} onChange={(e) => setRaceId(e.target.value)}>
            {races.map((r) => <option key={r.race_id} value={r.race_id}>{r.season} {r.event_name}</option>)}
          </select>
        </label>
        <label>Driver
          <select value={driver || ""} onChange={(e) => setDriver(e.target.value)}>
            {drivers.map((d) => <option key={d}>{d}</option>)}
          </select>
        </label>
        {states && (
          <label className="lap">Decision after lap <b>{states.lap[k]}</b>
            <input type="range" min={0} max={states.lap.length - 1} value={k} onChange={(e) => setK(+e.target.value)} />
          </label>
        )}
        <label>Safety car
          <select value={sc} onChange={(e) => setSc(e.target.value)}>
            <option value="none">None</option>
            <option value="random">At the historical rate</option>
            <option value="at_lap">On a lap I choose</option>
          </select>
        </label>
        {sc === "at_lap" && st && (
          <label>Safety car on lap
            <input type="number" min={st.decision_lap + 1} max={st.total_laps - 1} value={scLap ?? st.decision_lap + 5}
              onChange={(e) => setScLap(+e.target.value)} />
          </label>
        )}
      </section>

      {race && (
        <section className="wide">
          <StintChart race={race} highlight={driver} decisionLap={st?.decision_lap} onPick={setDriver} />
        </section>
      )}

      {st && (
        <section>
          <p className="state">
            {driver} after lap {st.decision_lap} of {st.total_laps}: on {COMPOUND[st.current_compound].name.toLowerCase()} tyres,{" "}
            {st.current_age} laps old, {st.stops_so_far} {st.stops_so_far === 1 ? "stop" : "stops"} made. Pace taken from {st.n_pace_laps} clean laps.
            {race.rules.note && <><br />Race rule: {race.rules.note}.</>}
          </p>
          <PlanEditor plan={plan} setPlan={setPlan} st={st} errors={planErrors} />
          <button className="run" onClick={run} disabled={plan.length > 0 && planErrors.length > 0}>Run {N_DRAWS.toLocaleString()} races</button>
        </section>
      )}

      {res && <Results res={res} current={st.current_compound} />}
    </>
  );
}

function PlanEditor({ plan, setPlan, st, errors }) {
  const add = () => {
    const last = plan.length ? plan.at(-1).lap : st.decision_lap;
    setPlan([...plan, { lap: Math.min(last + 15, st.total_laps - 3), comp: "HARD" }]);
  };
  const set = (i, v) => setPlan(plan.map((p, j) => (j === i ? { ...p, ...v } : p)));
  return (
    <div className="plan">
      <h3>Your plan (optional)</h3>
      {plan.map((p, i) => (
        <div className="plan-row" key={i}>
          <label>Stop {i + 1} on lap
            <input type="number" value={p.lap} min={st.decision_lap + 1} max={st.total_laps - 1} onChange={(e) => set(i, { lap: +e.target.value })} />
          </label>
          <label>for
            <select value={p.comp} onChange={(e) => set(i, { comp: e.target.value })}>
              {SLICKS.map((c) => <option key={c} value={c}>{COMPOUND[c].name}</option>)}
            </select>
          </label>
          <button className="link" onClick={() => setPlan(plan.filter((_, j) => j !== i))}>Remove</button>
        </div>
      ))}
      {plan.length < 3 && <button className="link" onClick={add}>Add a stop</button>}
      {plan.length === 0 && <span className="muted"> No more stops is also a plan: the best 0-stop option is always shown if the rules allow it.</span>}
      {errors.length > 0 && <ul className="errors">{errors.map((e) => <li key={e}>Not allowed: {e}.</li>)}</ul>}
    </div>
  );
}

function Results({ res, current }) {
  const ref = res.rows[0];
  return (
    <section className="wide results">
      <h2>Results, compared with: {ref.strategy.label.toLowerCase()}</h2>
      <div className="table-wrap">
        <table>
          <thead><tr><th>Plan</th><th>Tyres and stop laps</th><th className="num">Time gap (s)</th><th className="num">90% of races between</th><th className="num">Share of races faster</th></tr></thead>
          <tbody>
            {res.rows.map((r, i) => (
              <tr key={i}>
                <td>{r.strategy.label}</td>
                <td>{describe(r.strategy, current)}</td>
                <td className="num">{i === 0 ? "reference" : signed(r.delta, 1)}</td>
                <td className="num">{i === 0 ? "–" : `${signed(r.d05, 1)} to ${signed(r.d95, 1)}`}</td>
                <td className="num">{r.pFaster === null ? "–" : `${fmt(100 * r.pFaster, 0)}%`}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="note">
        Negative gap: faster than the reference. Every plan faces the same 1,000 draws of pace, safety cars and pit-stop
        times, so the gaps compare plans, not luck.{res.scAt ? ` Safety car from lap ${res.scAt}.` : ""}{" "}
        {res.scDraws > 0 && !res.scAt ? `A safety car came out in ${res.scDraws} of the ${N_DRAWS} races. ` : ""}
        The model is a single car against the clock: no traffic, no track position, no finishing places. Its tested
        error is on the <Link to="/methods">simulator backtest</Link>; small gaps, especially between plans with a
        different number of stops, are within that error. {DISCLAIMER}
      </p>
    </section>
  );
}
