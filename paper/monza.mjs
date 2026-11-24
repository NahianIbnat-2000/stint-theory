// Monza 2024 case-study numbers from the browser simulator (seed 2026), written to paper/data/monza.json
import { readFileSync, writeFileSync } from "node:fs";
import { simulate, stateAt, expectedTime, describe } from "../web/src/sim/engine.js";
import { candidates, N_DRAWS, SEED } from "../web/src/lib/candidates.js";
import { duelStats } from "../web/src/lib/stats.js";
import { withParams } from "../web/src/lib/sensitivity.js";
const race = JSON.parse(readFileSync(new URL("../web/public/data/sim/races/2024_16.json", import.meta.url)));
const LAP = 20, WEAR = Array.from({ length: 13 }, (_, i) => 1 + i * 0.25);
const out = { race_id: race.race_id, total_laps: race.total_laps, lap: LAP, circuit: race.circuit, pit_loss: race.pit_loss.mean_s,
  stints: Object.fromEntries(["LEC", "PIA", "NOR", "SAI", "HAM", "RUS", "VER"].map((d) => [d, race.drivers[d].stints])) };
for (const d of ["PIA", "LEC"]) {
  const s = race.drivers[d].states, st = stateAt(race, d, s.lap.indexOf(LAP));
  const c = candidates(race, d, st);
  const obs = c.find((x) => x.id === "observed"), alt = c.find((x) => x.id === (d === "PIA" ? "best0" : "best1"));
  const r = simulate(race, st, [obs, alt], { n: N_DRAWS, seed: SEED });
  const ds = duelStats(r.times, 0, 1);
  const one = d === "PIA" ? alt : obs, two = d === "PIA" ? obs : alt;
  const curve = WEAR.map((w) => { const q = withParams(race, { wearMult: w }); return expectedTime(q, st, one) - expectedTime(q, st, two); });
  let be = null; for (let i = 1; i < curve.length; i++) if (Math.sign(curve[i]) !== Math.sign(curve[i - 1])) { be = WEAR[i - 1] + 0.25 * (-curve[i - 1] / (curve[i] - curve[i - 1])); break; }
  out[d] = { age: st.current_age, n_pace: st.n_pace_laps, observed: describe(obs, st.current_compound), alternative: describe(alt, st.current_compound),
    mean: ds.mean, p05: ds.p05, p95: ds.p95, pAltFaster: ds.pBFaster, wear: WEAR, one_minus_two: curve, break_even: be };
}
writeFileSync(new URL("./data/monza.json", import.meta.url), JSON.stringify(out, null, 1));
console.log(JSON.stringify({ PIA: { ...out.PIA, wear: undefined, one_minus_two: undefined }, LEC: { ...out.LEC, wear: undefined, one_minus_two: undefined } }, null, 1));
