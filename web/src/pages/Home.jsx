import { Link } from "react-router-dom";
import { useData } from "../data.js";
import StintChart from "../components/StintChart.jsx";
import { comparison } from "../models.js";

export default function Home() {
  const idx = useData("sim/index.json");
  const races = (idx.data || []).filter((r) => r.simulatable);
  const latest = races.reduce((a, r) => (!a || r.season > a.season || (r.season === a.season && r.round > a.round) ? r : a), null);
  const race = useData(latest ? `sim/races/${latest.race_id}.json` : null);
  const t1 = useData("results/final_test.json");
  const t2 = useData("results/task2_test_meta.json");
  const t3 = useData("results/task3.json");
  const main = t3.data?.robustness?.filter((r) => r.specification.startsWith("main"));
  return (
    <>
      <header className="hero">
        <h1>STINT THEORY</h1>
        <p className="tagline">Every lap is data. Every pit stop is a decision.</p>
        <p className="lede">
          Can deep learning predict Formula 1 lap times and tyre wear better than simpler statistical and machine
          learning models? Every model here was tested on races it had never seen, with the tests written down before the
          test data was opened.
        </p>
      </header>
      {race.data && (
        <section className="wide">
          <h2>{race.data.event_name} {race.data.season}, tyre by tyre</h2>
          <StintChart race={race.data} />
        </section>
      )}
      <section className="wide">
        <h2>What the tests found</h2>
        <div className="findings">
          <Finding to="/next-lap" title="The next lap">
            {t1.data ? <Verdicts rows={t1.data.primary} /> : <span className="muted">Not exported yet.</span>}
          </Finding>
          <Finding to="/ten-laps" title="The next ten laps">
            {t2.data ? <Verdicts rows={t2.data.primary} /> : <span className="muted">Not exported yet.</span>}
          </Finding>
          <Finding to="/tyres" title="Tyre wear">
            {main ? (
              <p>Each extra lap on the same set adds about{" "}
                {main.map((r, i) => <span key={r.compound}>{i ? (i === main.length - 1 ? " and " : ", ") : ""}<b>{r.s_per_lap.toFixed(3)} s</b> ({r.compound.toLowerCase()})</span>)}{" "}
                to a lap, once fuel burn and track grip are taken out.</p>
            ) : <span className="muted">Not exported yet.</span>}
          </Finding>
          <Finding to="/simulator" title="Strategy">
            <p>Pick a real race, a driver and a lap, then compare pit-stop plans in 1,000 simulated races.</p>
          </Finding>
        </div>
      </section>
    </>
  );
}

function Finding({ to, title, children }) {
  return (
    <article className="finding">
      <h3><Link to={to}>{title}</Link></h3>
      {children}
    </article>
  );
}

function Verdicts({ rows }) {
  return (
    <ul className="verdicts">
      {rows.map((r) => <li key={r.comparison}><span>{comparison(r.comparison)}</span> <em>{r.label}</em></li>)}
    </ul>
  );
}
