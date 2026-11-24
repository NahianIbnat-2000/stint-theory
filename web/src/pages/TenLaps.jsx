import { useData } from "../data.js";
import IntervalChart from "../components/IntervalChart.jsx";
import Report, { Missing } from "../components/Report.jsx";
import { intervalRows } from "../models.js";

export default function TenLaps() {
  const meta = useData("results/task2_test_meta.json");
  return (
    <>
      <header className="page-head">
        <h1>The next ten laps</h1>
        <p className="lede">Task 2. Forecast the next ten laps at once, the horizon a strategist needs. Scored on the total
          time over the ten laps, on the same locked test races, with its own pre-registration.</p>
      </header>
      <section className="wide">
        <h2>Pre-registered comparisons</h2>
        {meta.error ? <Missing what="task2_test/run_meta.json" /> : meta.data && (
          <IntervalChart rows={intervalRows(meta.data.primary, "10-lap MAE diff (s)")} margin={meta.data.margin_total_s}
            note="Differences in mean absolute error of the ten-lap total, seconds." />
        )}
      </section>
      <section><Report name="task2_test" /></section>
    </>
  );
}
