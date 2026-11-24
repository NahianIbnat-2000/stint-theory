import { useDeferredValue, useEffect, useMemo, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useData, COMPOUND } from "../data.js";
import { fmt, signed } from "../format.js";
import StintChart from "../components/StintChart.jsx";
import StrategyTimeline from "../components/StrategyTimeline.jsx";
import { DuelHistogram, StopLapCurve, GapHeatmap } from "../components/DuelCharts.jsx";
import { simulate, summarise, stateAt, describe, DISCLAIMER } from "../sim/engine.js";
import { check, SLICKS } from "../sim/constraints.js";
import { decodeScenario, encodeScenario } from "../lib/scenario.js";
import { duelStats } from "../lib/stats.js";
import { stopLapCurve, gapGrid } from "../lib/sensitivity.js";
import { explainDuel } from "../lib/explain.js";
import { toCSV, download, svgToPng } from "../lib/export.js";
import { candidates, N_DRAWS, SEED } from "../lib/candidates.js";

const PIT_DELTAS = [-4, -2, 0, 2, 4];
const WEAR = [0.6, 0.8, 1, 1.2, 1.4];

export default function Simulator() {
  const [params, setParams] = useSearchParams();
  const sc0 = useMemo(() => decodeScenario(params.toString()), []); // eslint-disable-line react-hooks/exhaustive-deps
  const idx = useData("sim/index.json");
  const races = useMemo(() => (idx.data || []).filter((r) => r.simulatable).sort((a, b) => b.season - a.season || b.round - a.round), [idx.data]);
  const seasons = [...new Set(races.map((r) => r.season))].sort();

  const [raceId, setRaceId] = useState(sc0.race || null);
  useEffect(() => { if (races.length && !races.some((r) => r.race_id === raceId)) setRaceId(races[0].race_id); }, [races, raceId]);
  const meta = races.find((r) => r.race_id === raceId);
  const raceQ = useData(raceId ? `sim/races/${raceId}.json` : null);
  const race = raceQ.data?.race_id === raceId ? raceQ.data : null;

  const drivers = useMemo(() => (race ? Object.keys(race.drivers).filter((d) => race.drivers[d].states.lap.length).sort() : []), [race]);
  const [driver, setDriver] = useState(sc0.driver || null);
  useEffect(() => { if (race && !drivers.includes(driver)) setDriver(drivers[0] || null); }, [race, drivers, driver]);
  const states = race && driver && drivers.includes(driver) ? race.drivers[driver].states : null;
  const [k, setK] = useState(null);
  const [wantLap, setWantLap] = useState(sc0.lap ?? null);
  useEffect(() => {
    if (!states) return;
    const i = wantLap != null ? states.lap.findIndex((l) => l >= wantLap) : -1;
    const third = states.lap.findIndex((l) => l >= Math.round(race.total_laps / 3));
    setK(i >= 0 ? i : Math.max(third, 0));
    setWantLap(null);
  }, [states]); // eslint-disable-line react-hooks/exhaustive-deps
  // slider moves stay smooth: the simulation follows the latest settled value
  const kSim = useDeferredValue(k);
  const st = states && kSim != null && kSim < states.lap.length ? stateAt(race, driver, kSim) : null;

  const [sc, setSc] = useState(sc0.sc || "none");
  const [scLap, setScLap] = useState(sc0.scLap ?? null);
  const [plan, setPlan] = useState(sc0.plan || []);
  const [pick, setPick] = useState({ a: sc0.a, b: sc0.b });
  const [copied, setCopied] = useState("");
  const rules = race ? { min_stops: race.rules.min_stops, max_set_life: race.rules.max_set_life } : null;
  const planStrategy = { stop_laps: plan.map((p) => p.lap), compounds: plan.map((p) => p.comp) };
  const planErrors = st && plan.length ? check(planStrategy, st, rules) : [];
  const scAt = st && sc === "at_lap" ? Math.min(Math.max(scLap ?? st.decision_lap + 5, st.decision_lap + 1), st.total_laps - 1) : null;

  // keep the URL in step with the scenario (shareable)
  useEffect(() => {
    if (!st) return;
    setParams(encodeScenario({ race: raceId, driver, lap: st.decision_lap, sc, scLap: scAt, plan, a: pick.a, b: pick.b }), { replace: true });
  }, [raceId, driver, st?.decision_lap, sc, scAt, plan, pick]); // eslint-disable-line react-hooks/exhaustive-deps

  const result = useMemo(() => {
    if (!st) return null;
    const cands = candidates(race, driver, st, plan);
    if (!cands.length) return null;
    const r = simulate(race, st, cands, { n: N_DRAWS, seed: SEED, scMode: sc, scLap: scAt });
    return { cands, sim: r, rows: summarise(r, cands) };
  }, [race, driver, st?.decision_lap, sc, scAt, plan]); // eslint-disable-line react-hooks/exhaustive-deps

  // duel: A defaults to what happened, B to the best plan with a different number of stops
  const duel = useMemo(() => {
    if (!result) return null;
    const { cands, rows, sim } = result;
    const has = (id) => cands.some((c) => c.id === id);
    let a = has(pick.a) ? pick.a : (has("observed") ? "observed" : cands[0].id);
    const ia0 = cands.findIndex((c) => c.id === a);
    let b = has(pick.b) && pick.b !== a ? pick.b : null;
    if (!b) {
      const others = cands.map((c, i) => ({ c, i })).filter(({ c }) => c.id !== a && c.stop_laps.join() + c.compounds.join() !== cands[ia0].stop_laps.join() + cands[ia0].compounds.join());
      const diffStops = others.filter(({ c }) => c.stop_laps.length !== cands[ia0].stop_laps.length);
      const pool = diffStops.length ? diffStops : others.length ? others : cands.map((c, i) => ({ c, i })).filter(({ c }) => c.id !== a);
      b = pool.sort((x, y) => rows[x.i].mean - rows[y.i].mean)[0]?.c.id;
    }
    if (!b) return null;
    const ia = cands.findIndex((c) => c.id === a), ib = cands.findIndex((c) => c.id === b);
    const A = { ...cands[ia], key: "A", color: "var(--series-a)" }, B = { ...cands[ib], key: "B", color: "var(--series-b)" };
    const stats = duelStats(sim.times, ia, ib);
    return { A, B, stats, explain: explainDuel({ a: A, b: B, stats }) };
  }, [result, pick]);

  const [moveWhich, setMoveWhich] = useState("B");
  const sens = useMemo(() => {
    if (!duel || !st) return null;
    let target = moveWhich === "A" ? duel.A : duel.B;
    if (!target.stop_laps.length) target = moveWhich === "A" ? duel.B : duel.A;   // a plan with no stop has nothing to move
    const curve = target.stop_laps.length ? stopLapCurve(race, st, target, rules, 0) : [];
    const grid = gapGrid(race, st, duel.A, duel.B, PIT_DELTAS, WEAR);
    return { target, curve, grid };
  }, [duel, moveWhich]); // eslint-disable-line react-hooks/exhaustive-deps

  const timelineRef = useRef(null), histRef = useRef(null);
  const reset = () => { setPlan([]); setSc("none"); setScLap(null); setPick({}); if (states) setK(Math.max(states.lap.findIndex((l) => l >= Math.round(race.total_laps / 3)), 0)); };
  const copyLink = async () => {
    try { await navigator.clipboard.writeText(window.location.href); setCopied("Link copied"); }
    catch { setCopied("Copy the address bar to share"); }
    setTimeout(() => setCopied(""), 2500);
  };
  const exportCSV = () => {
    const ref = result.rows[0];
    download(`stint-theory_${raceId}_${driver}_lap${st.decision_lap}.csv`, toCSV(result.rows.map((r, i) => ({ ...r, i })), [
      { label: "plan", value: (r) => r.strategy.label },
      { label: "tyres_and_stops", value: (r) => describe(r.strategy, st.current_compound) },
      { label: "expected_remaining_time_s", value: (r) => r.mean.toFixed(2) },
      { label: "p05_s", value: (r) => r.p05.toFixed(2) }, { label: "p95_s", value: (r) => r.p95.toFixed(2) },
      { label: `gap_vs_${ref.strategy.id}_s`, value: (r) => r.delta.toFixed(2) },
      { label: "gap_p05_s", value: (r) => r.d05.toFixed(2) }, { label: "gap_p95_s", value: (r) => r.d95.toFixed(2) },
      { label: "share_faster", value: (r) => (r.pFaster === null ? "" : r.pFaster.toFixed(3)) },
    ]), "text/csv");
  };
  const exportSummary = () => {
    const { A, B, stats } = duel;
    download(`stint-theory_${raceId}_${driver}_summary.md`, [
      `# STINT THEORY strategy duel`, ``,
      `${race.season} ${race.event_name}, ${driver}, decision after lap ${st.decision_lap} of ${st.total_laps} on ${st.current_compound.toLowerCase()} tyres (age ${st.current_age}).`,
      `Safety car: ${sc === "none" ? "none" : sc === "random" ? "historical rate" : `from lap ${scAt}`}. ${N_DRAWS} simulated races, seed ${SEED}.`, ``,
      `- A: ${A.label}, ${describe(A, st.current_compound)}: expected remaining time ${fmt(stats.meanA, 1)} s`,
      `- B: ${B.label}, ${describe(B, st.current_compound)}: expected remaining time ${fmt(stats.meanB, 1)} s`,
      `- B minus A: mean ${signed(stats.mean, 1)} s, 90% of races between ${signed(stats.p05, 1)} and ${signed(stats.p95, 1)} s, B faster in ${fmt(100 * stats.pBFaster, 0)}% of races`, ``,
      ...duel.explain.map((s) => `- ${s}`), ``, DISCLAIMER, ``, `Scenario: ${window.location.href}`, "",
    ].join("\n"), "text/markdown");
  };

  if (idx.error) return <div className="page"><p className="missing">Simulator data has not been exported yet.</p></div>;
  return (
    <div className="page">
      <header className="page-head">
        <h1>Strategy simulator</h1>
        <p className="lede">Pick a real dry race, a driver and a lap. The simulator plays out the rest of that race {N_DRAWS.toLocaleString()} times
          for each plan, using a model fitted <em>without</em> that race and the driver’s pace from laps already run.</p>
      </header>

      <div className="sim">
        <aside className="sim-config panel" aria-label="Scenario">
          <h2>Scenario</h2>
          <div className="field" role="group" aria-label="Season">
            <span className="field-label">Season</span>
            <div className="segmented">
              {seasons.map((s) => (
                <button key={s} aria-pressed={meta?.season === s} onClick={() => setRaceId(races.find((r) => r.season === s)?.race_id)}>{s}</button>
              ))}
            </div>
          </div>
          <label className="field">Grand Prix
            <select value={raceId || ""} onChange={(e) => setRaceId(e.target.value)}>
              {races.filter((r) => r.season === meta?.season).sort((a, b) => a.round - b.round).map((r) => <option key={r.race_id} value={r.race_id}>{r.event_name}</option>)}
            </select>
          </label>
          <label className="field">Driver
            <select value={driver || ""} onChange={(e) => setDriver(e.target.value)}>
              {drivers.map((d) => <option key={d}>{d}</option>)}
            </select>
          </label>
          {states && k != null && (
            <label className="field">Decision after lap
              <span className="lap-value">{states.lap[k]} <small className="muted">of {race.total_laps}</small></span>
              <input type="range" min={0} max={states.lap.length - 1} value={k} onChange={(e) => setK(+e.target.value)}
                aria-valuetext={`lap ${states.lap[k]}`} />
            </label>
          )}
          <div className="field" role="group" aria-label="Safety car">
            <span className="field-label">Safety car</span>
            <div className="segmented">
              {[["none", "None"], ["random", "Historical rate"], ["at_lap", "On a lap"]].map(([v, l]) => (
                <button key={v} aria-pressed={sc === v} onClick={() => setSc(v)}>{l}</button>
              ))}
            </div>
            {sc === "at_lap" && st && (
              <label className="field">Safety car from lap
                <input type="number" min={st.decision_lap + 1} max={st.total_laps - 1} value={scAt} onChange={(e) => setScLap(+e.target.value)} />
              </label>
            )}
          </div>
          {st && (
            <p className="state">
              {driver} on {COMPOUND[st.current_compound].name.toLowerCase()} tyres, {st.current_age} laps old, {st.stops_so_far} {st.stops_so_far === 1 ? "stop" : "stops"} made.
              Pace from {st.n_pace_laps} clean laps.{race.rules.note && <><br />Race rule: {race.rules.note}.</>}
            </p>
          )}
          {st && <PlanEditor plan={plan} setPlan={setPlan} st={st} errors={planErrors} />}
          <div className="toolbar">
            <button className="btn btn-quiet" onClick={copyLink}>Copy link</button>
            <button className="btn btn-quiet" onClick={reset}>Reset</button>
            <span className="toast" role="status">{copied}</span>
          </div>
        </aside>

        <div className="sim-main">
          {!result || !duel ? <div className="skeleton" aria-label="Loading" /> : (
            <>
              <section aria-labelledby="duel-h">
                <h2 id="duel-h">Strategy duel</h2>
                <div className="duel-pick">
                  {["a", "b"].map((side) => {
                    const cur = side === "a" ? duel.A : duel.B;
                    return (
                      <label key={side} className="field">
                        <span><span className="swatch" style={{ background: cur.color }} />Strategy {side.toUpperCase()}</span>
                        <select value={cur.id} onChange={(e) => setPick({ ...pick, [side]: e.target.value, ...(side === "a" && e.target.value === duel.B.id ? { b: duel.A.id } : {}), ...(side === "b" && e.target.value === duel.A.id ? { a: duel.B.id } : {}) })}>
                          {result.cands.map((c) => <option key={c.id} value={c.id}>{c.label}: {describe(c, st.current_compound)}</option>)}
                        </select>
                      </label>
                    );
                  })}
                </div>
                <div className="duel-numbers">
                  <div className="stat"><span>A: expected remaining time</span><b>{fmt(duel.stats.meanA, 1)} s</b></div>
                  <div className="stat"><span>B: expected remaining time</span><b>{fmt(duel.stats.meanB, 1)} s</b></div>
                  <div className="stat"><span>B minus A, mean</span><b>{signed(duel.stats.mean, 1)} s</b></div>
                  <div className="stat"><span>90% of races between</span><b>{signed(duel.stats.p05, 1)} / {signed(duel.stats.p95, 1)}</b></div>
                  <div className="stat"><span>B faster in</span><b>{fmt(100 * duel.stats.pBFaster, 0)}%</b></div>
                </div>
                <div className="explain" aria-live="polite">
                  <h3>What this says</h3>
                  <ul>{duel.explain.map((s) => <li key={s}>{s}</li>)}</ul>
                </div>
              </section>

              <section aria-labelledby="tl-h">
                <h2 id="tl-h">Race timeline</h2>
                <StrategyTimeline race={race} driver={driver} st={st} plans={[duel.A, duel.B]} svgRef={timelineRef} />
                <div className="chart-tools"><button className="btn btn-quiet" onClick={() => svgToPng(timelineRef.current, `timeline_${raceId}_${driver}.png`)}>Download PNG</button></div>
              </section>

              <section aria-labelledby="dist-h">
                <h2 id="dist-h">Outcome distribution</h2>
                <p className="note">Each bar counts simulated races by how much faster or slower B was than A. Both plans face the same draws of pace, safety
                  cars and pit-stop times in every race, so the spread reflects the plans, not luck.</p>
                <DuelHistogram stats={duel.stats} a={duel.A} b={duel.B} svgRef={histRef} />
                <div className="chart-tools"><button className="btn btn-quiet" onClick={() => svgToPng(histRef.current, `duel_${raceId}_${driver}.png`)}>Download PNG</button></div>
              </section>

              <section aria-labelledby="sens-h">
                <h2 id="sens-h">Sensitivity</h2>
                <p className="note">Expected values from the same engine with one input changed at a time, no safety car.</p>
                <div className="field" role="group" aria-label="Plan whose stop moves">
                  <span className="field-label">Move the first stop of</span>
                  <div className="segmented">
                    {["A", "B"].map((s) => {
                      const has = (s === "A" ? duel.A : duel.B).stop_laps.length > 0;
                      return <button key={s} disabled={!has} aria-pressed={sens?.target.key === s} onClick={() => setMoveWhich(s)}>Strategy {s}{has ? "" : " (no stop)"}</button>;
                    })}
                  </div>
                </div>
                {sens && <StopLapCurve curve={sens.curve} current={sens.target.stop_laps[0]} color={sens.target.color} label={sens.target.label} />}
                <h3 style={{ marginTop: "var(--space-5)" }}>B minus A if pit loss or tyre wear were different</h3>
                {sens && <GapHeatmap grid={sens.grid} pitDeltas={PIT_DELTAS} wearMults={WEAR} a={duel.A} b={duel.B} />}
                <p className="note">Pit loss as fitted for this circuit: {fmt(race.pit_loss.mean_s, 1)} s per stop. Tyre wear × scales the tyre-age effect
                  (circuit factor {fmt(race.circuit.scale, 2)}). Negative: B faster. The outlined cell is the model as fitted.</p>
              </section>

              <section aria-labelledby="all-h">
                <h2 id="all-h">Every plan compared</h2>
                <div className="table-wrap">
                  <table>
                    <thead><tr><th>Plan</th><th>Tyres and stops</th><th className="num">Expected remaining (s)</th><th className="num">Gap to first row (s)</th><th className="num">90% of races</th><th className="num">Faster than first row</th></tr></thead>
                    <tbody>
                      {result.rows.map((r, i) => (
                        <tr key={r.strategy.id} className={[duel.A.id, duel.B.id].includes(r.strategy.id) ? "highlight" : undefined}>
                          <td>{r.strategy.label}{r.strategy.alsoIs.length ? <small> (= {r.strategy.alsoIs.join(", ").toLowerCase()})</small> : null}</td>
                          <td>{describe(r.strategy, st.current_compound)}</td>
                          <td className="num">{fmt(r.mean, 1)}</td>
                          <td className="num">{i === 0 ? "reference" : signed(r.delta, 1)}</td>
                          <td className="num">{i === 0 ? "–" : `${signed(r.d05, 1)} / ${signed(r.d95, 1)}`}</td>
                          <td className="num">{r.pFaster === null ? "–" : `${fmt(100 * r.pFaster, 0)}%`}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="chart-tools">
                  <button className="btn btn-quiet" onClick={exportCSV}>Download CSV</button>
                  <button className="btn btn-quiet" onClick={exportSummary}>Download summary</button>
                </div>
              </section>

              <section aria-labelledby="ev-h">
                <details className="report">
                  <summary id="ev-h">Evidence and assumptions</summary>
                  <div className="table-wrap" style={{ marginTop: "var(--space-4)" }}>
                    <table><tbody>
                      <tr><th>Model</th><td>Simulator pace model v{race.pace.version ?? "1–2"}, frozen after backtest 3 ({race.pace.method || "see methodology"})</td></tr>
                      <tr><th>Estimation</th><td>{race.estimation}; {race.pace.n?.toLocaleString()} clean laps from {race.pace.races} races</td></tr>
                      <tr><th>Tyre wear at this circuit</th><td>circuit factor {fmt(race.circuit.scale, 2)} ({race.circuit.years} other year{race.circuit.years === 1 ? "" : "s"} here)</td></tr>
                      <tr><th>Pit loss</th><td>{fmt(race.pit_loss.mean_s, 1)} s per green-flag stop; source: {race.pit_loss.source}</td></tr>
                      <tr><th>Safety car</th><td>{fmt(100 * race.safety_car.hazard_per_lap, 2)}% chance per lap from {race.safety_car.periods_other_races} periods in other races</td></tr>
                      <tr><th>Simulation</th><td>{N_DRAWS} races, seed {SEED}, common random numbers; the JavaScript engine is checked draw by draw against the Python simulator</td></tr>
                      <tr><th>Tested accuracy</th><td>See the <Link to="/methods?doc=sim_backtest">simulator backtest</Link>: remaining-race time from one-third distance was off by 35 s on average and too slow by 19 s. Much of that is common to every plan and cancels in a duel; the part that does not is the extra-stop penalty described above.</td></tr>
                      <tr><th>Not modelled</th><td>Traffic, track position, other cars’ strategies, finishing places, tyre sets actually available, weather changes, VSC.</td></tr>
                    </tbody></table>
                  </div>
                  <p className="note" style={{ marginTop: "var(--space-3)" }}>{DISCLAIMER}</p>
                </details>
              </section>
            </>
          )}
        </div>
      </div>

      {race && st && (
        <section>
          <h2>Everyone’s tyres in this race</h2>
          <StintChart race={race} highlight={driver} decisionLap={st.decision_lap} onPick={setDriver} />
        </section>
      )}
    </div>
  );
}

function PlanEditor({ plan, setPlan, st, errors }) {
  const add = () => {
    const last = plan.length ? plan.at(-1).lap : st.decision_lap;
    setPlan([...plan, { lap: Math.min(last + 12, st.total_laps - 3), comp: "HARD" }]);
  };
  const set = (i, v) => setPlan(plan.map((p, j) => (j === i ? { ...p, ...v } : p)));
  return (
    <div className="field" role="group" aria-label="Your plan">
      <span className="field-label">Your plan (optional)</span>
      {plan.map((p, i) => (
        <div className="plan-row" key={i}>
          Stop {i + 1}, lap
          <input type="number" aria-label={`Stop ${i + 1} lap`} value={p.lap} min={st.decision_lap + 1} max={st.total_laps - 1} onChange={(e) => set(i, { lap: +e.target.value })} />
          <select aria-label={`Stop ${i + 1} compound`} value={p.comp} onChange={(e) => set(i, { comp: e.target.value })}>
            {SLICKS.map((c) => <option key={c} value={c}>{COMPOUND[c].name}</option>)}
          </select>
          <button className="link" onClick={() => setPlan(plan.filter((_, j) => j !== i))}>Remove</button>
        </div>
      ))}
      {plan.length < 3 && <div><button className="link" onClick={add}>Add a stop</button></div>}
      {errors.length > 0 && <ul className="errors">{errors.map((e) => <li key={e}>Not allowed: {e}.</li>)}</ul>}
      {plan.length > 0 && !errors.length && <span className="note">Your plan is now in the comparison.</span>}
    </div>
  );
}
