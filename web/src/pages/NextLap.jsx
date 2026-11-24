import { useData, fmt } from "../data.js";
import IntervalChart from "../components/IntervalChart.jsx";
import Report, { Missing } from "../components/Report.jsx";
import { intervalRows, name } from "../models.js";

export default function NextLap() {
  const m = useData("results/final_test.json");
  const meta = useData("results/final_test_meta.json");
  const margin = meta.data?.margin_s ?? 0.01;
  return (
    <>
      <header className="page-head">
        <h1>The next lap</h1>
        <p className="lede">Task 1. At the end of each lap, forecast the driver’s next lap time. The models are tested on
          the second half of the 2025 season (rounds 13–24), which stayed locked until every model was frozen and the
          comparisons were registered.</p>
      </header>
      <section className="wide">
        <h2>Pre-registered comparisons</h2>
        {m.error ? <Missing what="final_test/metrics.json" /> : m.data && (
          <IntervalChart rows={intervalRows(m.data.primary, "MAE diff (s)")} margin={margin}
            note="Differences in mean absolute error, seconds per lap." />
        )}
      </section>
      {m.data?.summary && (
        <section>
          <h2>Every model on the test races</h2>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Model</th><th className="num">Mean abs. error (s)</th><th className="num">95% interval</th><th className="num">Error cut vs persistence</th></tr></thead>
              <tbody>
                {[...m.data.summary].sort((a, b) => a.mae - b.mae).map((r) => (
                  <tr key={r.model}><td>{name(r.model)}</td><td className="num">{fmt(r.mae)}</td>
                    <td className="num">[{fmt(r.mae_ci_low)}, {fmt(r.mae_ci_high)}]</td>
                    <td className="num">{fmt(100 * r.skill_vs_persistence, 1)}%</td></tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="note">Persistence repeats the driver’s last clean lap. “Error cut” is the share of its error that a
            model removes.</p>
        </section>
      )}
      <section><Report name="final_test" /></section>
    </>
  );
}
