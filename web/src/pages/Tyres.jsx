import { useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { useData, COMPOUND } from "../data.js";
import { fmt } from "../format.js";
import TyreCurves from "../components/TyreCurves.jsx";
import DotCI from "../components/DotCI.jsx";
import BinLines from "../components/BinLines.jsx";
import Evidence from "../components/Evidence.jsx";
import Report, { Missing } from "../components/Report.jsx";
import { svgToPng } from "../lib/export.js";

const GROUPS = {
  main: { label: "Main estimate", test: (s) => s.startsWith("main") },
  season: { label: "By season", test: (s) => s.startsWith("main") || s.startsWith("R5") },
  robust: { label: "Robustness checks", test: (s) => s.startsWith("main") || /^R[1246]/.test(s) },
  naive: { label: "Main vs naive", test: (s) => s.startsWith("main") || s.startsWith("naive") },
};
const short = (s) => s.replace(/^main:.*$/, "Main").replace(/^naive:.*$/, "Naive (fuel and track left in)").replace(/^R5: season /, "Season ").replace(/^R(\d): /, "R$1 ");

export default function Tyres() {
  const est = useData("results/task3.json");
  const curve = useData("results/tyre_curves.json");
  const errs = useData("results/test_errors.json");
  const [visible, setVisible] = useState(Object.keys(COMPOUND));
  const [group, setGroup] = useState("season");
  const [circuitQ, setCircuitQ] = useState("");
  const [circuitSort, setCircuitSort] = useState("slope");
  const curveRef = useRef(null);
  const rob = est.data?.robustness;
  const slopeRows = useMemo(() => {
    if (!rob) return [];
    const specs = [...new Set(rob.map((r) => r.specification))].filter(GROUPS[group].test);
    return specs.flatMap((s) => Object.keys(COMPOUND).filter((c) => visible.includes(c)).map((c) => {
      const r = rob.find((v) => v.specification === s && v.compound === c);
      return r && { label: short(s), sub: COMPOUND[c].name, value: r.s_per_lap, lo: r.ci_low, hi: r.ci_high, color: COMPOUND[c].color, mark: COMPOUND[c].short, strong: s.startsWith("main"), n: `${r["n laps"]?.toLocaleString()} laps, ${r.races} races` };
    }).filter(Boolean));
  }, [rob, group, visible]);
  const circuits = useMemo(() => {
    const rows = (est.data?.by_circuit || []).filter((r) => r.circuit.toLowerCase().includes(circuitQ.toLowerCase()));
    return [...rows].sort((a, b) => (circuitSort === "slope" ? b.s_per_lap - a.s_per_lap : a.circuit.localeCompare(b.circuit)))
      .map((r) => ({ label: r.circuit.replace(" Grand Prix", ""), sub: `${r.races} races`, value: r.s_per_lap, lo: r.ci_low, hi: r.ci_high, n: `${r["n laps"]?.toLocaleString()} laps` }));
  }, [est.data, circuitQ, circuitSort]);
  const toggle = (c) => setVisible(visible.includes(c) ? (visible.length > 1 ? visible.filter((v) => v !== c) : visible) : [...visible, c]);
  const e = errs.data;

  return (
    <div className="page">
      <header className="page-head">
        <h1>Tyre-age lab</h1>
        <p className="lede">How much slower does a lap get for each extra lap on the same set of tyres? Cars also get faster
          as fuel burns off and the track gains grip, so a raw comparison mixes the two. The model compares all cars on the
          same lap of the same race to take that out. What remains is an association with tyre age, not a measurement of
          the tyre itself.</p>
      </header>

      <div className="controls" style={{ marginTop: "var(--space-6)" }}>
        <div className="field" role="group" aria-label="Compounds shown">
          <span className="field-label">Compounds</span>
          <div className="segmented">
            {Object.entries(COMPOUND).map(([k, c]) => <button key={k} aria-pressed={visible.includes(k)} onClick={() => toggle(k)}>{c.name}</button>)}
          </div>
        </div>
        <button className="link" onClick={() => setVisible(Object.keys(COMPOUND))}>Show all</button>
      </div>

      <section className="wide" aria-labelledby="curve-h">
        <h2 id="curve-h" style={{ marginTop: 0 }}>Adjusted lap time by tyre age</h2>
        {curve.error ? <Missing what="task3/tyre_age_curves.csv" /> : curve.data ? (
          <>
            <TyreCurves curve={curve.data} visible={visible} svgRef={curveRef} />
            <div className="chart-tools"><button className="btn btn-quiet" onClick={() => svgToPng(curveRef.current, "tyre_age_curves.png")}>Download PNG</button></div>
            <Evidence items={[
              ["Source", "research/results/task3/tyre_age_curves.csv"],
              ["What is plotted", "Estimated lap-time difference at each tyre age against age 5 of the same compound (tyre-age dummies)"],
              ["Held fixed", "race × lap (fuel, track, weather), driver × race (car and driver pace), race × compound (compound pace at that race)"],
              ["Sample", "Clean green-flag dry laps on slicks, 2023–2025; ages above 35 pooled"],
              ["Intervals", "95%, standard errors clustered by race"],
              ["Not shown", "Raw lap times (not published); per-driver curves (too few laps per driver to be reliable)"],
            ]} doc={["methodology_tyre", "Tyre-age model"]} />
          </>
        ) : <div className="skeleton" />}
      </section>

      {rob && (
        <section className="wide" aria-labelledby="slope-h">
          <h2 id="slope-h">Seconds per extra lap, and how stable it is</h2>
          <div className="controls">
            <div className="segmented" role="group" aria-label="Specifications">
              {Object.entries(GROUPS).map(([k, g]) => <button key={k} aria-pressed={group === k} onClick={() => setGroup(k)}>{g.label}</button>)}
            </div>
          </div>
          <DotCI rows={slopeRows} axisLabel="Seconds per extra lap of tyre age (95% interval, clustered by race)" ariaLabel="Tyre-age slopes by specification and compound" />
          <p className="note">The naive row leaves fuel burn and track evolution in: raw lap times barely slow, or even speed up, with tyre age. The
            early-stint robustness check (R2, ages up to 15) is steeper: wear is not linear. Full table in the report below.</p>
        </section>
      )}

      {e?.by_tyre_age && (
        <section className="wide" aria-labelledby="pe-h">
          <h2 id="pe-h">Forecast error as tyres age</h2>
          <p className="note">How well the next-lap models do by the tyre age of the predicted lap (locked test races).{" "}
            {(() => { const b = e.by_tyre_age, m = b.map((x) => x.mae.xgboost_ens5); const hi = b[m.indexOf(Math.max(...m))], lo = b[m.indexOf(Math.min(...m))];
              return `XGBoost’s error is highest for laps ${hi.lo + 1}–${hi.hi} of a stint (${fmt(Math.max(...m), 3)} s) and lowest for laps ${lo.lo + 1}–${lo.hi} (${fmt(Math.min(...m), 3)} s).`; })()}</p>
          <BinLines bins={e.by_tyre_age.map((b) => ({ label: `${b.lo + 1}–${b.hi}`, n: b.n }))}
            series={[
              { key: "persistence", label: "Persistence", color: "var(--text-2)", dash: "5 4", values: e.by_tyre_age.map((b) => b.mae.persistence) },
              { key: "xgboost_ens5", label: "XGBoost ×5", color: "var(--series-a)", values: e.by_tyre_age.map((b) => b.mae.xgboost_ens5) },
              { key: "lstm", label: "LSTM", color: "var(--series-b)", values: e.by_tyre_age.map((b) => b.mae.lstm) },
            ].filter((s) => s.values.every((v) => v != null))}
            axisLabel="Mean absolute error of the next-lap forecast (s), by tyre age (laps)" />
          <p className="note">Descriptive, from the stored predictions of the single test run. <Link to="/models">Model arena</Link></p>
        </section>
      )}

      {est.data?.by_circuit && (
        <section className="wide" aria-labelledby="circ-h">
          <h2 id="circ-h">By circuit</h2>
          <div className="controls">
            <label className="field">Find a circuit
              <input type="search" value={circuitQ} onChange={(ev) => setCircuitQ(ev.target.value)} placeholder="e.g. Bahrain" style={{ minHeight: 40, padding: ".45rem .6rem", border: "1px solid var(--border-strong)", borderRadius: 4, font: "inherit" }} />
            </label>
            <div className="segmented" role="group" aria-label="Sort">
              <button aria-pressed={circuitSort === "slope"} onClick={() => setCircuitSort("slope")}>Steepest first</button>
              <button aria-pressed={circuitSort === "name"} onClick={() => setCircuitSort("name")}>A–Z</button>
            </div>
            {circuitQ && <button className="link" onClick={() => setCircuitQ("")}>Clear</button>}
          </div>
          {circuits.length ? <DotCI rows={circuits} axisLabel="Seconds per extra lap, all slick compounds pooled" ariaLabel="Tyre-age slope by circuit" />
            : <p className="muted">No circuit matches “{circuitQ}”.</p>}
          <p className="note">Compounds pooled, so circuits where more soft tyres were run look steeper. Two or three races per circuit, with
            standard errors clustered by driver-race: the intervals are too narrow. Use this to rank circuits, not to test differences
            between them. Mean slope across circuits: {fmt(est.data.by_circuit.reduce((a, r) => a + r.s_per_lap, 0) / est.data.by_circuit.length, 3)} s per lap.</p>
        </section>
      )}

      <section><Report name="task3" /></section>
    </div>
  );
}
