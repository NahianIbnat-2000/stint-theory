import { useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { useData } from "../data.js";
import { fmt, signed } from "../format.js";
import ModelRanking from "../components/ModelRanking.jsx";
import BinLines from "../components/BinLines.jsx";
import Evidence, { shortHash, day } from "../components/Evidence.jsx";
import { Missing } from "../components/Report.jsx";
import { INFO, name, familyOf, comparison } from "../models.js";
import { svgToPng } from "../lib/export.js";

const METRICS = [
  { key: "mae", label: "Mean absolute error", ci: "mae_ci" },
  { key: "rmse", label: "Root mean squared error", ci: "rmse_ci" },
  { key: "median_ae", label: "Median absolute error" },
  { key: "bias", label: "Bias (prediction minus actual)", lowerIsBetter: false },
];
const NEURAL = ["mlp", "lstm", "tcn"];

function rowsFor(summary, boot, metric) {
  return summary.map((r) => {
    const ci = metric.ci ? boot?.models?.[r.model]?.[metric.ci] : null;
    return { model: r.model, value: r[metric.key], lo: ci ? ci[0] : null, hi: ci ? ci[1] : null };
  });
}

export default function Models() {
  const test = useData("results/final_test.json");
  const meta = useData("results/final_test_meta.json");
  const p2 = useData("results/phase2_dev.json");
  const p3 = useData("results/phase3_dev.json");
  const errs = useData("results/test_errors.json");
  const [tab, setTab] = useState("test");
  const [metricKey, setMetricKey] = useState("mae");
  const [sel, setSel] = useState("xgboost_ens5");
  const chartRef = useRef(null);
  const metric = METRICS.find((m) => m.key === metricKey);

  const dev = useMemo(() => {
    if (!p2.data || !p3.data) return null;
    const seen = new Set(), summary = [];
    for (const r of [...p2.data.summary, ...p3.data.summary]) if (!seen.has(r.model)) { seen.add(r.model); summary.push(r); }
    return { summary, boot: { models: { ...p2.data.bootstrap.models, ...p3.data.bootstrap.models } }, races: p2.data.bootstrap.races, b: p2.data.bootstrap.b };
  }, [p2.data, p3.data]);
  const cur = tab === "test" ? (test.data && { summary: test.data.summary, boot: test.data.bootstrap, races: test.data.bootstrap.races, b: test.data.bootstrap.b }) : dev;
  const selRow = cur?.summary.find((r) => r.model === sel) || cur?.summary[0];

  return (
    <div className="page">
      <header className="page-head">
        <h1>Model arena</h1>
        <p className="lede">Ten models, from repeating the last lap to recurrent and convolutional networks, forecasting the next
          lap time on the same laps. The locked test is the result; development scores are shown separately and were used
          to build the models.</p>
      </header>

      <div className="tabs" role="tablist">
        <button role="tab" aria-selected={tab === "test"} onClick={() => setTab("test")}>Locked test: 2025 rounds 13–24</button>
        <button role="tab" aria-selected={tab === "dev"} onClick={() => setTab("dev")}>Development: 2025 rounds 1–12</button>
      </div>
      {tab === "dev" && <p className="missing">Development results guided model building and freezing. They are not the test result and are slightly optimistic for the models that were adjusted after seeing them.</p>}

      {!cur ? (test.error ? <Missing what="final_test/metrics.json" /> : <div className="skeleton" />) : (
        <section className="wide">
          <div className="controls">
            <div className="field" role="group" aria-label="Metric">
              <span className="field-label">Metric</span>
              <div className="segmented">
                {METRICS.map((m) => <button key={m.key} aria-pressed={metricKey === m.key} onClick={() => setMetricKey(m.key)}>{m.label.split(" (")[0]}</button>)}
              </div>
            </div>
            <button className="btn btn-quiet" onClick={() => svgToPng(chartRef.current, `models_${tab}_${metricKey}.png`)}>Download PNG</button>
          </div>
          <ModelRanking rows={rowsFor(cur.summary, cur.boot, metric)} metric={metric} selected={selRow?.model} onSelect={setSel} svgRef={chartRef} />
          <p className="note">Lines: 95% race-clustered bootstrap intervals ({cur.b} resamples over {cur.races} races), shown where they were computed.
            Overlapping intervals here do not settle a comparison: models are compared in pairs on the same laps, which removes the shared race-to-race noise (see the <Link to="/next-lap">pre-registered comparisons</Link>). Select a model for details.</p>
          <Evidence items={tab === "test" ? [
            ["Source", "research/results/final_test/metrics.json"],
            ["Evaluation", "2025 rounds 13–24, scored once after all models were frozen"],
            ["Pre-registration", meta.data?.preregistration ? `docs/preregistration.md, commit ${shortHash(meta.data.preregistration.git_commit)}, sha256 ${shortHash(meta.data.preregistration.sha256)}` : null],
            ["Run finished", day(meta.data?.finished_utc)],
            ["Sample", `${cur.summary[0]?.n?.toLocaleString()} scored laps (clean green laps), ${cur.races} races`],
            ["Metric", `${metric.label}, seconds per lap`],
            ["Intervals", `race-clustered bootstrap, ${cur.b} resamples`],
          ] : [
            ["Source", "research/results/phase2_dev/metrics.json, phase3_dev/metrics.json"],
            ["Evaluation", "2025 rounds 1–12, rolling origin: each race predicted from all earlier races"],
            ["Sample", `${cur.summary[0]?.n?.toLocaleString()} scored laps, ${cur.races} races with bootstrap intervals`],
            ["Metric", `${metric.label}, seconds per lap`],
            ["Intervals", `race-clustered bootstrap, ${cur.b} resamples`],
          ]} doc={["methodology_models", "Models"]} />
        </section>
      )}

      {selRow && <ModelDetail row={selRow} tab={tab} meta={meta.data} seeds={tab === "test" ? test.data?.seeds : p3.data?.seeds} />}

      {test.data && <Complexity test={test.data} errs={errs} />}
    </div>
  );
}

function ModelDetail({ row, tab, meta, seeds }) {
  const info = INFO[row.model] || {};
  const hp = meta?.hyperparameters?.phase2?.[row.model] || meta?.hyperparameters?.phase3?.[row.model];
  const sd = seeds?.find((s) => s.model === row.model);
  return (
    <section className="wide" aria-labelledby="detail-h">
      <h2 id="detail-h">{name(row.model)}</h2>
      <div className="detail panel">
        <dl>
          <dt>Family</dt><dd>{familyOf(row.model)}</dd>
          <dt>Objective</dt><dd>{info.objective}</dd>
          <dt>Inputs</dt><dd>{info.inputs}</dd>
          <dt>Validation</dt><dd>{tab === "test" ? "Rolling origin: each 2025 R13–24 race predicted by the frozen model trained on every earlier race; scored once" : "Rolling origin over 2025 R1–12; tuned on 2024 blocks only"}</dd>
        </dl>
        <dl>
          <dt>Mean absolute error</dt><dd className="mono">{fmt(row.mae, 4)} s [{fmt(row.mae_ci_low, 3)}, {fmt(row.mae_ci_high, 3)}]</dd>
          <dt>RMSE / median absolute error</dt><dd className="mono">{fmt(row.rmse, 3)} / {fmt(row.median_ae, 3)} s</dd>
          <dt>Bias</dt><dd className="mono">{signed(row.bias, 4)} s</dd>
          <dt>Error cut against persistence</dt><dd className="mono">{fmt(100 * row.skill_vs_persistence, 1)}% [{fmt(100 * row.skill_ci_low, 1)}, {fmt(100 * row.skill_ci_high, 1)}]</dd>
          {sd && <><dt>Across 5 seeds (single networks)</dt><dd className="mono">MAE {fmt(sd.mae_mean, 4)} ± {fmt(sd.mae_sd, 4)} (range {fmt(sd.mae_min, 4)}–{fmt(sd.mae_max, 4)})</dd></>}
          {hp && tab === "test" && <><dt>Frozen settings</dt><dd className="mono" style={{ fontSize: ".82rem" }}>{Object.entries(hp).map(([k, v]) => `${k}=${v}`).join(", ")}</dd></>}
        </dl>
        <dl>
          <dt>Strengths</dt><dd>{info.strengths}</dd>
          <dt>Limitations</dt><dd>{info.limits}</dd>
          <dt>Runtime</dt><dd>Recorded per test fold in the <Link to="/next-lap">full test report</Link> (section S6).</dd>
        </dl>
      </div>
    </section>
  );
}

function Complexity({ test, errs }) {
  const prim = test.primary;
  const eq = prim.filter((r) => r.label.startsWith("equivalent")).length;
  const S = Object.fromEntries(test.summary.map((r) => [r.model, r]));
  const top = ["xgboost_ens5", ...NEURAL].filter((m) => S[m]);
  const spread = Math.max(...top.map((m) => S[m].mae)) - Math.min(...top.map((m) => S[m].mae));
  const gain = S.persistence && S.xgboost_ens5 ? S.persistence.mae - S.xgboost_ens5.mae : null;
  const seeds = test.seeds?.filter((s) => NEURAL.includes(s.model)) || [];
  const s1 = test.secondary?.filter((r) => r.analysis.startsWith("S1")) || [];
  const e = errs.data;
  const binsShown = e?.by_tyre_age;
  return (
    <section aria-labelledby="cx-h">
      <h2 id="cx-h">When does added complexity stop paying?</h2>
      <div className="callout">
        <p>On the locked test races:</p>
        <ul>
          <li>{eq} of {prim.length} pre-registered comparisons between the networks and XGBoost were <em>equivalent</em>: the 90% interval of the difference sat inside ±0.01 s per lap.</li>
          {gain != null && <li>The four strongest models (XGBoost averaged over 5 seeds, MLP, LSTM, TCN) are within <span className="mono">{fmt(spread, 4)} s</span> of each other. Going from repeating the last lap to XGBoost gains <span className="mono">{fmt(gain, 3)} s</span>: about {fmt(gain / spread, 0)} times more than the whole spread among them.</li>}
          {seeds.length > 0 && <li>Retraining the same network with another random seed moves its error by about <span className="mono">{seeds.map((s) => `${fmt(s.mae_sd, 4)} s (${name(s.model)})`).join(", ")}</span>: the same size as the gaps between architectures.</li>}
          {s1.map((r) => <li key={r.comparison}>Very old tyres (more than 30 laps, {r["n laps"]?.toLocaleString()} laps): {comparison(r.comparison)} {signed(r["MAE diff (s)"], 4)} s [{fmt(r["95% low"], 4)}, {fmt(r["95% high"], 4)}]. A secondary analysis, not corrected for multiple comparisons.</li>)}
        </ul>
        <p style={{ marginTop: ".6rem" }}>A plausible reading, not tested here: with these inputs the forecast is limited by what no model sees (traffic, driver intent, tyre temperature) rather than by the learner. What the results do show is that the raw lap sequence the LSTM and TCN add carried no measurable signal beyond the hand-built summaries.</p>
      </div>
      {binsShown ? (
        <>
          <h3 style={{ marginTop: "var(--space-6)" }}>Error by tyre age on the test races</h3>
          <BinLines bins={binsShown.map((b) => ({ label: `${b.lo + 1}–${b.hi}`, n: b.n }))}
            series={[
              { key: "persistence", label: "Persistence", color: "var(--text-2)", dash: "5 4", values: binsShown.map((b) => b.mae.persistence) },
              { key: "xgboost_ens5", label: "XGBoost ×5", color: "var(--series-a)", values: binsShown.map((b) => b.mae.xgboost_ens5) },
              { key: "tcn", label: "TCN", color: "var(--series-b)", values: binsShown.map((b) => b.mae.tcn) },
            ].filter((s) => s.values.every((v) => v != null))}
            axisLabel="Mean absolute error (s) by tyre age of the predicted lap (laps)" />
          <p className="note">Descriptive breakdown of the stored predictions from the single test run ({e.n_laps.toLocaleString()} laps, {e.races} races); no intervals, no new tests.</p>
        </>
      ) : <p className="note">The error-by-tyre-age chart appears after the next <code>python -m webexport</code> (it reads the stored test predictions on your machine).</p>}
    </section>
  );
}
