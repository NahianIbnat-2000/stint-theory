import { useData, fmt, COMPOUND } from "../data.js";
import TyreCurves from "../components/TyreCurves.jsx";
import Report, { Missing } from "../components/Report.jsx";

export default function Tyres() {
  const est = useData("results/task3.json");
  const curve = useData("results/tyre_curves.json");
  const rob = est.data?.robustness;
  const specs = rob ? [...new Set(rob.map((r) => r.specification))] : [];
  return (
    <>
      <header className="page-head">
        <h1>Tyre wear lab</h1>
        <p className="lede">Task 3. How much slower does a lap get for each extra lap on the same set of tyres? Cars also
          get faster as fuel burns off and the track gains grip, so a raw comparison mixes the two. The model compares
          all cars on the same lap of the same race to take that out.</p>
      </header>
      <section className="wide">
        <h2>Lap time by tyre age</h2>
        {curve.error ? <Missing what="task3/tyre_age_curves.csv" /> : curve.data && <TyreCurves curve={curve.data} />}
      </section>
      {rob && (
        <section>
          <h2>Seconds per extra lap of tyre age, and how robust it is</h2>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Specification</th>{Object.keys(COMPOUND).map((c) => <th key={c} className="num">{COMPOUND[c].name}</th>)}</tr></thead>
              <tbody>
                {specs.map((s) => (
                  <tr key={s}><td>{s}</td>{Object.keys(COMPOUND).map((c) => {
                    const r = rob.find((v) => v.specification === s && v.compound === c);
                    return <td key={c} className="num">{r ? <>{fmt(r.s_per_lap)}<small> [{fmt(r.ci_low)}, {fmt(r.ci_high)}]</small></> : "–"}</td>;
                  })}</tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="note">95% intervals clustered by race. The naive row leaves fuel and track in: it shows how
            much of the raw lap-to-lap change is not the tyres. These are associations with tyre age, not measured tyre
            wear; the assumptions are on the Methods page.</p>
        </section>
      )}
      {est.data?.by_circuit && (
        <section>
          <h2>By circuit</h2>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Circuit</th><th className="num">Races</th><th className="num">s per lap</th><th className="num">95% interval</th></tr></thead>
              <tbody>{est.data.by_circuit.map((r) => (
                <tr key={r.circuit}><td>{r.circuit}</td><td className="num">{r.races}</td><td className="num">{fmt(r.s_per_lap)}</td><td className="num">[{fmt(r.ci_low)}, {fmt(r.ci_high)}]</td></tr>
              ))}</tbody>
            </table>
          </div>
          <p className="note">Compounds pooled, so circuits with more soft running look steeper. Two or three races per
            circuit: the intervals are too narrow. Use this to rank circuits, not to test differences between them.</p>
        </section>
      )}
      <section><Report name="task3" /></section>
    </>
  );
}
