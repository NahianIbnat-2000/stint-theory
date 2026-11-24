import { useMemo } from "react";
import { Link } from "react-router-dom";
import { useData } from "../data.js";
import { fmt, signed } from "../format.js";
import StintChart from "../components/StintChart.jsx";
import StrategyTimeline from "../components/StrategyTimeline.jsx";
import { DuelHistogram } from "../components/DuelCharts.jsx";
import BinLines from "../components/BinLines.jsx";
import { simulate, stateAt, describe, expectedTime } from "../sim/engine.js";
import { candidates, N_DRAWS, SEED } from "../lib/candidates.js";
import { duelStats } from "../lib/stats.js";
import { withParams } from "../lib/sensitivity.js";
import { encodeScenario } from "../lib/scenario.js";

const RACE = "2024_16";       // 2024 Italian Grand Prix
const LAP = 20;               // both drivers on hard tyres after their first stop
const WEAR = Array.from({ length: 13 }, (_, i) => 1 + i * 0.25);
const SOURCES = [
  ["Autosport: Leclerc one-stop strategy defeats McLarens", "https://autosport.com/f1/news/f1-italian-gp-leclerc-one-stop-strategy-defeats-mclarens/10650239"],
  ["Autosport: the risk that kept McLaren off the best Monza strategy", "https://www.autosport.com/f1/news/the-50-cent-coin-disaster-risk-that-kept-mclaren-off-the-best-monza-strategy/10650508/"],
  ["FIA: Ferrari’s one-stop Monza gamble pays off", "https://www.fia.com/news/f1-leclerc-wins-ahead-mclaren-duo-ferraris-one-stop-monza-gamble-pays"],
  ["Formula 1: Leclerc triumphs at Monza ahead of Piastri and Norris", "https://www.formula1.com/en/latest/article/leclerc-thrills-the-tifosi-to-triumph-at-monza-ahead-of-piastri-and-norris.1aiYZF3rWZp2Q9yQtcuvqV"],
  ["Road & Track: hotter conditions and new tarmac caused graining", "https://autos.yahoo.com/charles-leclerc-gives-ferrari-home-173100706.html"],
];

// one-stop minus two-stop for a driver, under a tyre-wear multiplier
function oneMinusTwo(race, st, one, two, w) {
  const q = withParams(race, { wearMult: w });
  return expectedTime(q, st, one) - expectedTime(q, st, two);
}
function breakEven(xs, ys) {
  for (let i = 1; i < ys.length; i++) if (Math.sign(ys[i]) !== Math.sign(ys[i - 1])) return xs[i - 1] + (xs[i] - xs[i - 1]) * (-ys[i - 1] / (ys[i] - ys[i - 1]));
  return null;
}

function useCase(race) {
  return useMemo(() => {
    if (!race) return null;
    const out = {};
    for (const d of ["PIA", "LEC"]) {
      const s = race.drivers[d]?.states;
      const i = s ? s.lap.indexOf(LAP) : -1;
      if (i < 0) return null;
      const st = stateAt(race, d, i);
      const c = candidates(race, d, st);
      const obs = c.find((x) => x.id === "observed");
      const alt = d === "PIA" ? c.find((x) => x.id === "best0") : c.find((x) => x.id === "best1");
      if (!obs || !alt) return null;
      const sim = simulate(race, st, [obs, alt], { n: N_DRAWS, seed: SEED });
      const stats = duelStats(sim.times, 0, 1);
      const one = d === "PIA" ? alt : obs, two = d === "PIA" ? obs : alt;
      const curve = WEAR.map((w) => oneMinusTwo(race, st, one, two, w));
      out[d] = { st, A: { ...obs, key: "A", color: "var(--series-a)" }, B: { ...alt, key: "B", color: "var(--series-b)" }, stats, curve, be: breakEven(WEAR, curve),
        link: `/simulator?${encodeScenario({ race: RACE, driver: d, lap: LAP, a: "observed", b: alt.id })}` };
    }
    return out;
  }, [race]);
}

export default function CaseStudy() {
  const q = useData(`sim/races/${RACE}.json`);
  const race = q.data;
  const cs = useCase(race);
  const P = cs?.PIA, L = cs?.LEC;
  const share = (st) => `${fmt(100 * st.pBFaster, 0)}%`;

  return (
    <div className="page">
      <header className="page-head">
        <div className="crumbs"><Link to="/races?race=2024_16">Race explorer</Link> / 2024 Italian Grand Prix</div>
        <h1>Monza 2024: one stop or two?</h1>
        <p className="lede">Ferrari kept Charles Leclerc on one stop while McLaren stopped twice with both cars, and Leclerc won.
          What does a model that never saw this race say about that call, and where does it go wrong?</p>
      </header>

      <section aria-labelledby="c1">
        <h2 id="c1">The race</h2>
        <p>Hot conditions and a newly resurfaced track brought graining on the front tyres, and most teams expected two stops. McLaren,
          with the faster car, stopped Oscar Piastri and Lando Norris twice. Ferrari ran Leclerc to the finish on one set of hards after
          a single stop, and he held off the closing Piastri to win by 2.664 s. Autosport’s analysis judged the one-stop marginally
          faster than the two-stop. (Sources at the end.)</p>
      </section>
      {race && (
        <section className="wide">
          <StintChart race={race} highlight={null} decisionLap={LAP} />
        </section>
      )}

      {!cs ? <div className="skeleton" /> : (
        <>
          <section aria-labelledby="c2">
            <h2 id="c2">The decision</h2>
            <p>After lap {LAP}, both drivers are on hard tyres after their first stop: Leclerc’s are {L.st.current_age} laps old,
              Piastri’s {P.st.current_age}. {race.total_laps - LAP} laps remain. Stop again for fresh tyres, at the cost of
              about {fmt(race.pit_loss.mean_s, 0)} s in the pit lane, or nurse this set to the flag?</p>
            <div className="table-wrap">
              <table>
                <thead><tr><th>Driver</th><th>What happened</th><th>Alternative tested</th></tr></thead>
                <tbody>
                  <tr><td>Piastri</td><td>{describe(P.A, P.st.current_compound)}</td><td>{P.B.label}: {describe(P.B, P.st.current_compound)}</td></tr>
                  <tr><td>Leclerc</td><td>{describe(L.A, L.st.current_compound)}</td><td>{L.B.label}: {describe(L.B, L.st.current_compound)}</td></tr>
                </tbody>
              </table>
            </div>
          </section>

          <section aria-labelledby="c3">
            <h2 id="c3">What the model assumes</h2>
            <ul>
              <li>Every parameter is estimated <em>without</em> the 2024 Italian Grand Prix. The tyre-wear factor for Monza ({fmt(race.circuit.scale, 2)} times the average) comes from the other {race.circuit.years} years at the circuit.</li>
              <li>Each driver’s pace comes only from clean laps already run at lap {LAP}: {P.st.n_pace_laps} for Piastri, {L.st.n_pace_laps} for Leclerc.</li>
              <li>Pit-lane time: {fmt(race.pit_loss.mean_s, 1)} s per stop on average, with spread, from other Monza races.</li>
              <li>One car against the clock: no traffic, no battle for position, no tyre management beyond what the average curve contains. No safety car is drawn here; this race had none.</li>
            </ul>
          </section>

          <section className="wide" aria-labelledby="c4">
            <h2 id="c4">Piastri: what if he had stayed out?</h2>
            <div className="duel-numbers">
              <div className="stat"><span>Staying out minus two stops, mean</span><b>{signed(P.stats.mean, 1)} s</b></div>
              <div className="stat"><span>90% of simulated races</span><b>{signed(P.stats.p05, 1)} / {signed(P.stats.p95, 1)}</b></div>
              <div className="stat"><span>Staying out faster in</span><b>{share(P.stats)}</b></div>
            </div>
            <StrategyTimeline race={race} driver="PIA" st={P.st} plans={[P.A, P.B]} />
            <DuelHistogram stats={P.stats} a={P.A} b={P.B} />
            <p className="note"><Link to={P.link}>Open Piastri’s scenario in the simulator</Link></p>
          </section>

          <section aria-labelledby="c5">
            <h2 id="c5">Leclerc: was one stop right?</h2>
            <p>For Leclerc, the plan he actually ran is the model’s own best plan. Adding a second stop ({describe(L.B, L.st.current_compound)}) is
              {" "}<span className="mono">{signed(L.stats.mean, 1)} s</span> slower on average (90% of simulated races between {signed(L.stats.p05, 1)} and {signed(L.stats.p95, 1)} s);
              the two-stop is faster in {share(L.stats)} of them.</p>
            <p className="note"><Link to={L.link}>Open Leclerc’s scenario in the simulator</Link></p>
          </section>

          <section className="wide" aria-labelledby="c6">
            <h2 id="c6">How much tyre wear would flip the answer?</h2>
            <p>The same comparison with the tyre-age effect at Monza scaled up. Below zero, one stop is faster.</p>
            <BinLines bins={WEAR.map((w) => ({ label: `×${w.toFixed(2)}` }))}
              series={[
                { key: "PIA", label: "Piastri", color: "var(--series-b)", values: P.curve },
                { key: "LEC", label: "Leclerc", color: "var(--series-a)", values: L.curve },
              ]}
              marker={P.be ? { at: (P.be - 1) / 0.25, label: `break-even about ×${fmt(P.be, 1)}` } : null}
              digits={0}
              axisLabel="One stop minus two stops, expected remaining time (s), by tyre-wear multiplier at Monza" />
            <p>Two stops become the faster plan only if tyres wore about {fmt(P.be, 1)} times faster than the model’s Monza estimate
              (Leclerc: about {fmt(L.be, 1)} times).</p>
          </section>

          <section aria-labelledby="c7">
            <h2 id="c7">What can and cannot be concluded</h2>
            <div className="callout">
              <ul>
                <li><b>Direction: agrees.</b> Without seeing the race, the model prefers one stop for both drivers, the call Ferrari made and the one published analysis judged faster.</li>
                <li><b>Size: overstated.</b> The model puts the one-stop {fmt(Math.abs(P.stats.mean), 0)} s ahead for Piastri; the real race was close enough that a two-stopping car finished 2.664 s behind a one-stopper after a fight for position. A plausible reading, not tested here: tyres wore roughly {fmt(P.be, 0)} times faster than the model’s average for Monza, as the reports of graining on new tarmac suggest, which the model could not know before the race.</li>
                <li><b>What a one-car model leaves out.</b> Track position, the battle between Piastri and Norris, and whether a driver could actually manage a set for {race.total_laps - LAP} laps while graining. Norris said one stop was not possible with his graining.</li>
                <li><b>Known model biases point the same way.</b> The backtest found each extra stop charged about 1–2 s too much, a small part of the gap here.</li>
                <li><b>Not a verdict on McLaren.</b> A team reading live tyre data had information this model does not have.</li>
              </ul>
            </div>
          </section>

          <section aria-labelledby="c8">
            <h2 id="c8">Sources</h2>
            <ul>{SOURCES.map(([t, u]) => <li key={u}><a href={u} rel="noopener">{t}</a></li>)}</ul>
            <p className="note">Race facts (finishing order, the winning margin, team strategies, conditions) come from these reports. Stints and stops come from OpenF1;
              every model number on this page is computed in your browser by the simulator with seed {SEED}.</p>
          </section>
        </>
      )}
    </div>
  );
}
