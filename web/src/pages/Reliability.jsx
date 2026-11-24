import { Link } from "react-router-dom";
import { useData } from "../data.js";
import { fmt, signed } from "../format.js";
import Report from "../components/Report.jsx";
import Evidence, { shortHash, day } from "../components/Evidence.jsx";
import { name } from "../models.js";

const pct = (x, d = 1) => (x == null ? "–" : `${fmt(100 * x, d)}%`);

export default function Reliability() {
  const cov = useData("results/coverage.json");
  const test = useData("results/final_test.json");
  const meta = useData("results/final_test_meta.json");
  const meta2 = useData("results/task2_test_meta.json");
  const p2 = useData("results/phase2_dev.json");
  const p3 = useData("results/phase3_dev.json");
  const bt = useData("results/sim_backtest.json");
  const seasons = cov.data ? Object.entries(cov.data.by_season) : [];
  const excluded = cov.data?.lap_completeness?.filter((r) => !r.passed) || [];
  const nonNull = cov.data?.field_non_null_share || [];
  const dev = p2.data && p3.data ? [...p2.data.summary, ...p3.data.summary] : null;
  const gen = test.data && dev ? test.data.summary.map((t) => ({ t, d: dev.find((x) => x.model === t.model) })).filter((r) => r.d) : null;
  const b = bt.data;

  return (
    <div className="page">
      <header className="page-head">
        <h1>Research reliability</h1>
        <p className="lede">What the evidence behind this site can carry, section by section: the data, the validation design, how
          the models held up on races they never saw, how the simulator did against real races, and what is not covered.
          Every figure is read from a file in the repository. There is no overall score: reliability differs by question.</p>
      </header>

      <section aria-labelledby="r1">
        <h2 id="r1">Dataset quality</h2>
        {cov.data ? (
          <>
            <div className="table-wrap">
              <table>
                <thead><tr><th>Season</th><th className="num">Races listed</th><th className="num">In sample</th><th className="num">Driver-laps</th><th className="num">Clean green share</th><th className="num">Lap times present</th></tr></thead>
                <tbody>{seasons.map(([s, v]) => {
                  const nn = nonNull.find((r) => String(r.season) === s);
                  return <tr key={s}><td>{s}</td><td className="num">{v.races_listed}</td><td className="num">{v.races_in_sample}</td>
                    <td className="num">{v.driver_laps?.toLocaleString()}</td><td className="num">{pct(v.clean_green_share)}</td><td className="num">{pct(nn?.lap_time_s)}</td></tr>;
                })}</tbody>
              </table>
            </div>
            <p className="note">Excluded for incomplete data (under 90% of expected laps): {excluded.length ? excluded.map((r) => `${r.season} ${r.event_name} (${pct(r.lap_completeness)})`).join("; ") : "none"}.
              Safety-car periods, in-laps and deleted laps are rebuilt from race-control messages; the counts of every rebuilt or unmatched item are in the <Link to="/data">coverage report</Link>.</p>
            <Evidence items={[["Source", "data/reports/coverage.json"], ["Generated", day(cov.data.generated_at_utc)], ["Data", "OpenF1 API (community-run, not official)"]]} doc={["methodology", "Data and validation"]} />
          </>
        ) : <div className="skeleton" />}
      </section>

      <section aria-labelledby="r2">
        <h2 id="r2">Validation design</h2>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Part</th><th>Races</th><th>Use</th></tr></thead>
            <tbody>
              <tr><td>Train</td><td>2023 and 2024</td><td>Fitting; hyperparameters tuned inside 2024 only</td></tr>
              <tr><td>Development</td><td>2025 rounds 1–12</td><td>Rolling origin: each race predicted from all earlier races; models built and frozen here</td></tr>
              <tr><td>Test</td><td>2025 rounds 13–24</td><td>Locked in code, every opening logged; scored once per task under a committed pre-registration</td></tr>
            </tbody>
          </table>
        </div>
        <ul>
          {meta.data?.preregistration && <li>Task 1 (next lap): pre-registration commit <span className="mono">{shortHash(meta.data.preregistration.git_commit)}</span>, file hash <span className="mono">{shortHash(meta.data.preregistration.sha256)}</span>; test run finished {day(meta.data.finished_utc)}.</li>}
          {meta2.data?.preregistration && <li>Task 2 (ten laps): pre-registration commit <span className="mono">{shortHash(meta2.data.preregistration.git_commit)}</span>; test run finished {day(meta2.data.finished_utc)}.</li>}
          <li>Every change made after looking at development results is listed with the run that prompted it (<Link to="/methods?doc=model_changes">change log</Link>).</li>
        </ul>
      </section>

      <section className="wide" aria-labelledby="r3">
        <h2 id="r3">Out-of-sample performance</h2>
        {gen ? (
          <>
            <div className="table-wrap">
              <table>
                <thead><tr><th>Model</th><th className="num">Development MAE (s)</th><th className="num">Test MAE (s)</th><th className="num">Cut vs persistence, dev.</th><th className="num">Cut vs persistence, test</th></tr></thead>
                <tbody>{[...gen].sort((x, y) => x.t.mae - y.t.mae).map(({ t, d }) => (
                  <tr key={t.model}><td>{name(t.model)}</td><td className="num">{fmt(d.mae, 3)}</td><td className="num">{fmt(t.mae, 3)}</td>
                    <td className="num">{pct(d.skill_vs_persistence)}</td><td className="num">{pct(t.skill_vs_persistence)}</td></tr>
                ))}</tbody>
              </table>
            </div>
            <p className="note">XGBoost averaged over 5 seeds was added as the control for the final test only, so it has no development row. Absolute errors differ between the two halves of 2025 because the races differ (circuits, weather, incidents); the
              comparable quantity is the error cut against persistence on the same laps. The ranking of model families held from
              development to test; the <Link to="/models">model arena</Link> has the intervals.</p>
          </>
        ) : <div className="skeleton" />}
      </section>

      <section aria-labelledby="r4">
        <h2 id="r4">Simulator against real races</h2>
        {b ? (
          <>
            <div className="overview">
              <div className="stat"><b className="mono">{fmt(b.next_stint.model_mae, 3)} s</b><span>next-stint lap error (persistence {fmt(b.next_stint.persistence_mae, 3)})</span></div>
              <div className="stat"><b className="mono">{signed(b.next_stint.model_bias, 3)} s</b><span>next-stint bias per lap</span></div>
              <div className="stat"><b className="mono">{fmt(b.remaining.mae_s, 1)} s</b><span>remaining-race error, {b.remaining.drivers} drivers</span></div>
              <div className="stat"><b className="mono">{signed(b.remaining.bias_s, 1)} s</b><span>remaining-race bias (positive: too slow)</span></div>
              <div className="stat"><b className="mono">{signed(b.pit_loss.bias_s, 2)} s</b><span>pit-loss bias, {b.pit_loss.stops.toLocaleString()} stops</span></div>
            </div>
            <p>Remaining-race checks start at one third distance ({b.remaining.decision}). These are errors in absolute time. Most of
              that error is shared by every plan for the same driver and cancels in a strategy comparison; the strategy-specific
              part is the fresh-tyre bias, which charges each extra stop about 1–2 s too much.</p>
          </>
        ) : <Report name="sim_backtest" title="Simulator backtest report" />}
      </section>

      <section aria-labelledby="r5">
        <h2 id="r5">Uncertainty and calibration</h2>
        <ul>
          <li>Model comparisons: 95% (and 90% for equivalence) race-clustered bootstrap intervals, whole races resampled {test.data?.bootstrap?.b?.toLocaleString() || ""} times; Holm correction across the pre-registered primary comparisons.</li>
          <li>Tyre-age effects: standard errors clustered by race; the circuit table’s intervals are too narrow (two or three races per circuit).</li>
          <li>Simulator ranges: simulated from parameter uncertainty, driver pace, lap noise, pit-stop variation and safety cars; they leave out systematic model error.</li>
        </ul>
        {b?.calibration ? (
          <div className="callout">
            <p><b>Calibration check of the simulator’s ranges</b> (added after the simulator was frozen; nothing was changed in response).
              Over {b.calibration.drivers} real drivers, the actual remaining time fell inside the simulator’s 50% range {pct(b.calibration.coverage50)} of the time and inside its 90% range {pct(b.calibration.coverage90)} of the time
              (median width of the 90% range {fmt(b.calibration.median_width90_s, 1)} s). It fell below the range (faster than simulated) {pct(b.calibration.below90)} of the time and above it {pct(b.calibration.above90)}.</p>
            <p style={{ marginBottom: 0 }}>{b.calibration.coverage90 < 0.8
              ? "The ranges are far too narrow for absolute race time: they should not be read as a forecast interval for a finishing time. They describe the spread the model knows about, which is what a comparison of two plans uses."
              : b.calibration.coverage90 < 0.88 ? "The ranges are somewhat too narrow for absolute race time." : "The ranges cover about as often as they should."}</p>
          </div>
        ) : <p className="note">The calibration check appears after <code>python -m simulation backtest</code> and <code>python -m webexport</code> are rerun.</p>}
      </section>

      <section aria-labelledby="r6">
        <h2 id="r6">Main limitations</h2>
        <ul>
          <li>Three seasons from one rules era; an unofficial data source; one race excluded.</li>
          <li>Twelve test races per task: intervals are wide relative to the gaps between the best models.</li>
          <li>Tyre-age effects are associations in lap time, not measurements of tyre wear; wear is steeper early in a stint than the linear headline.</li>
          <li>The simulator is one car against the clock: no traffic, track position or finishing places; it cannot see race-specific conditions such as graining on a new surface (see the <Link to="/case-study">Monza case study</Link>).</li>
        </ul>
        <p><Link to="/limits">All limitations</Link></p>
      </section>

      <section aria-labelledby="r7">
        <h2 id="r7">Reproducibility</h2>
        <ul>
          <li>Code, reports, pre-registrations and the change log are public; raw lap data is not redistributed but can be rebuilt from OpenF1 with the pipeline.</li>
          <li>Every push runs the Python test suite and the website build on GitHub Actions; the website build also checks the JavaScript simulator against the Python simulator, draw by draw, on the exported races.</li>
          <li>Simulator runs use fixed seeds; the same scenario link reproduces the same numbers.</li>
        </ul>
        <p><Link to="/limits">How to rerun everything</Link></p>
      </section>
    </div>
  );
}
