import { PAPER_URL } from "../lib/paper.js";
import { useMemo } from "react";
import { Link } from "react-router-dom";
import { useData } from "../data.js";
import { fmt, signed } from "../format.js";
import StrategyTimeline from "../components/StrategyTimeline.jsx";
import { Legend } from "../components/StintChart.jsx";
import { simulate, stateAt, describe } from "../sim/engine.js";
import { duelStats } from "../lib/stats.js";
import { encodeScenario } from "../lib/scenario.js";
import { comparison, name } from "../models.js";
import { candidates, N_DRAWS, SEED } from "../lib/candidates.js";

// Featured scenario: latest dry race in the data, first driver (alphabetical) whose
// actual plan can be compared at one third distance with the model's best plan
// using a different number of stops. Computed live by the simulator.
function useFeatured(races) {
  const latest = races.reduce((a, r) => (!a || r.season > a.season || (r.season === a.season && r.round > a.round) ? r : a), null);
  const q = useData(latest ? `sim/races/${latest.race_id}.json` : null);
  return useMemo(() => {
    const race = q.data;
    if (!race) return null;
    for (const d of Object.keys(race.drivers).sort()) {
      const s = race.drivers[d].states;
      if (!s.lap.length) continue;
      const i = s.lap.findIndex((l) => l >= Math.round(race.total_laps / 3));
      if (i < 0) continue;
      const st = stateAt(race, d, i);
      const cands = candidates(race, d, st, []);
      const ia = cands.findIndex((c) => c.id === "observed");
      if (ia < 0) continue;
      const ib = cands.map((c, j) => j).filter((j) => cands[j].id.startsWith("best") && cands[j].stop_laps.length !== cands[ia].stop_laps.length)
        .sort((x, y) => x - y)[0];
      if (ib === undefined) continue;
      const sim = simulate(race, st, cands, { n: N_DRAWS, seed: SEED });
      const stats = duelStats(sim.times, ia, ib);
      const A = { ...cands[ia], key: "A", color: "var(--series-a)" }, B = { ...cands[ib], key: "B", color: "var(--series-b)" };
      return { race, driver: d, st, A, B, stats,
        link: `/simulator?${encodeScenario({ race: race.race_id, driver: d, lap: st.decision_lap, a: A.id, b: B.id })}` };
    }
    return null;
  }, [q.data]);
}

export default function Home() {
  const idx = useData("sim/index.json");
  const races = useMemo(() => (idx.data || []).filter((r) => r.simulatable), [idx.data]);
  const featured = useFeatured(races);
  const cov = useData("results/coverage.json");
  const t1 = useData("results/final_test.json");
  const t2 = useData("results/task2_test_meta.json");
  const t3 = useData("results/task3.json");
  const seasons = cov.data ? Object.entries(cov.data.by_season) : [];
  const sum = (k) => seasons.reduce((a, [, v]) => a + (v[k] || 0), 0);
  const rob = t3.data?.robustness || [];
  const main = rob.filter((r) => r.specification.startsWith("main"));
  const naive = rob.filter((r) => r.specification.startsWith("naive"));
  const summary = t1.data?.summary ? [...t1.data.summary].sort((a, b) => a.mae - b.mae) : null;
  const persistence = summary?.find((r) => r.model === "persistence");

  return (
    <>
      <section className="hero">
        <div className="hero-inner">
          <div>
            <h1><span>Every lap is data.</span><span>Every pit stop is a decision.</span></h1>
            <p className="lede">Explore the science of Formula 1 strategy through historical race data, statistical forecasting, deep learning and simulation.</p>
            <div className="actions">
              <Link className="btn btn-primary" to="/simulator">Launch strategy simulator</Link>
              <Link className="btn btn-ghost" to="/next-lap">Explore research findings</Link>
              <Link className="text-link" to="/methods">View methodology</Link>
            </div>
            <p className="hero-newcomer">New to Formula 1 or machine learning? <Link to="/faq">Start with the questions, answered plainly</Link>.</p>
          </div>
          <div className="hero-card">
            {featured ? (
              <>
                <p className="kicker">Live from the simulator</p>
                <h2>{featured.race.season} {featured.race.event_name}: {featured.driver}, decision after lap {featured.st.decision_lap}</h2>
                <StrategyTimeline race={featured.race} driver={featured.driver} st={featured.st} plans={[featured.A, featured.B]} showPace={false} />
                <div className="verdict-chip">
                  <span>A {featured.A.label.toLowerCase()}: {describe(featured.A, featured.st.current_compound)}</span>
                  <span>B {featured.B.label.toLowerCase()}: {describe(featured.B, featured.st.current_compound)}</span>
                </div>
                <div className="verdict-chip">
                  <span>B minus A</span><b>{signed(featured.stats.mean, 1)} s</b>
                  <span>90% of {N_DRAWS} simulated races between {signed(featured.stats.p05, 1)} and {signed(featured.stats.p95, 1)} s</span>
                </div>
                <p className="verdict-chip"><Link to={featured.link} style={{ color: "#fff" }}>Open this scenario in the simulator</Link></p>
              </>
            ) : <div className="skeleton" style={{ opacity: 0.15 }} aria-label="Loading the featured race" />}
          </div>
        </div>
      </section>

      <div className="page">
        {cov.data && (
          <>
            <div className="stats" aria-label="Research sample">
              <div className="stat"><b>{sum("races_in_sample")}</b><span>races in the sample</span></div>
              <div className="stat"><b>{sum("driver_laps").toLocaleString()}</b><span>driver-laps</span></div>
              <div className="stat"><b>{sum("clean_green_laps").toLocaleString()}</b><span>clean green-flag laps used by the models</span></div>
              <div className="stat"><b>{seasons[0]?.[0]}–{seasons.at(-1)?.[0]}</b><span>seasons</span></div>
              {summary && <div className="stat"><b>{summary.length}</b><span>models scored on the locked test races</span></div>}
              <div className="stat"><b>{races.length}</b><span>dry races in the simulator</span></div>
            </div>
            <p className="provenance">From <code>data/reports/coverage.json</code> (generated {cov.data.generated_at_utc?.slice(0, 10)}) and <code>research/results/final_test</code>. Races failing the 90% lap-completeness check are excluded. <Link to="/data">Coverage report</Link></p>
          </>
        )}

        <h2>What the tests found</h2>
        <div className="findings">
          <Finding to="/next-lap" title="The next lap">
            {t1.data ? <Verdicts rows={t1.data.primary} /> : <Pending />}
          </Finding>
          <Finding to="/ten-laps" title="The next ten laps">
            {t2.data ? <Verdicts rows={t2.data.primary} /> : <Pending />}
          </Finding>
          <Finding to="/tyres" title="Tyre-age effect">
            {main.length ? (
              <p>Each extra lap on the same set adds about{" "}
                {main.map((r, i) => <span key={r.compound}>{i ? (i === main.length - 1 ? " and " : ", ") : ""}<b className="mono">{r.s_per_lap.toFixed(3)} s</b> ({r.compound.toLowerCase()})</span>)}{" "}
                to a lap, once fuel burn and track grip are taken out.</p>
            ) : <Pending />}
          </Finding>
        </div>

        <Story n="1" title="A small signal in noisy laps">
          <p>Tyres cost a few hundredths of a second per lap of age. A driver’s lap time moves by much more than that from one lap to the next: traffic, mistakes, wind and fuel all move it too.</p>
          {main.length > 0 && persistence && <p className="fact">Tyre-age effect: {main.map((r) => `${r.compound.toLowerCase()} ${r.s_per_lap.toFixed(3)}`).join(", ")} s per lap. Typical error of simply repeating the last lap: {persistence.mae.toFixed(3)} s.</p>}
        </Story>
        <Story n="2" title="Lap time is not tyre wear">
          <p>Public timing data shows how fast a car went, not the state of its tyres. As fuel burns off, cars get faster even while the tyres get older. Comparing every car on the same lap of the same race separates the two, but what remains is an association with tyre age, not a measurement of rubber.</p>
          {naive.length > 0 && main.length > 0 && <p className="fact">Raw slope (fuel and track left in): {naive.map((r) => `${r.compound.toLowerCase()} ${signed(r.s_per_lap, 3)}`).join(", ")} s per lap. After removing them: {main.map((r) => `${r.compound.toLowerCase()} ${signed(r.s_per_lap, 3)}`).join(", ")}.</p>}
          <p><Link to="/tyres">Tyre-age lab</Link></p>
        </Story>
        <Story n="3" title="Strategy is a decision under uncertainty">
          <p>A pit call trades time in the pit lane now for faster laps later, while a safety car can arrive at any moment and change the price of a stop. The simulator answers with a distribution of outcomes, not a single number.</p>
          {featured && <p className="fact">Featured case above: the gap between the two plans ranges from {signed(featured.stats.p05, 1)} to {signed(featured.stats.p95, 1)} s across 90% of simulated races; B was faster in {fmt(100 * featured.stats.pBFaster, 0)}% of them.</p>}
        </Story>
        <Story n="4" title="What the models show so far">
          <p>On the locked 2025 test races, the neural networks (MLP, LSTM, TCN) and gradient-boosted trees ended up within a hundredth of a second of each other per lap. All of them beat repeating the last lap. More architecture did not buy accuracy here, which is itself the finding: the question the site now asks is when added complexity stops paying.</p>
          {summary && <p className="fact">Lowest test errors: {summary.slice(0, 4).map((r) => `${name(r.model)} ${r.mae.toFixed(3)} s`).join("; ")}.</p>}
          <p><Link to="/next-lap">Next-lap results</Link> · <Link to="/ten-laps">Ten-lap results</Link> · <a href={PAPER_URL}>Full research report (PDF)</a></p>
        </Story>
        <Story n="5" title="Try a strategy yourself">
          <p>Pick a season, a Grand Prix, a driver and the lap you are deciding on. Compare what the driver did with the model’s best plan for each number of stops, or enter your own. Every result comes with its spread, a sensitivity check and a plain-language reading.</p>
          <p><Link className="btn btn-primary" to="/simulator">Launch strategy simulator</Link></p>
        </Story>
        <Story n="6" title="Limits and reproducibility">
          <p>The simulator is one car against the clock: no traffic, no finishing positions. Its errors were measured on real races before it was frozen, and every number on this site is generated from files in the public repository, with the full history of model changes.</p>
          <p><a href={PAPER_URL}>Research report (PDF)</a> · <Link to="/limits">Limits</Link> · <Link to="/methods">Methods</Link> · <a href="https://github.com/NahianIbnat-2000/stint-theory">Code and reports</a></p>
        </Story>
      </div>
    </>
  );
}

function Story({ n, title, children }) {
  return (
    <section className="story" aria-labelledby={`story-${n}`}>
      <h3 id={`story-${n}`}>{title}</h3>
      <div>{children}</div>
    </section>
  );
}
function Finding({ to, title, children }) {
  return <article className="finding"><h3><Link to={to}>{title}</Link></h3>{children}</article>;
}
function Pending() { return <span className="muted">Not exported yet.</span>; }
function Verdicts({ rows }) {
  return <ul className="verdicts">{rows.map((r) => <li key={r.comparison}><span>{comparison(r.comparison)}</span> <em>{r.label}</em></li>)}</ul>;
}
