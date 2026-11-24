// Python/JavaScript parity: same inputs, same seeds, same numbers (to 1e-6 s).
// Reference file: python -m webexport parity  (web/test/parity.json)
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { Mulberry32 } from "../src/sim/rng.js";
import { simulate, expectedTime, stateAt } from "../src/sim/engine.js";
import { bestByStops, bestStrategies } from "../src/sim/strategy.js";

const DATA = process.env.STINT_WEB_DATA || fileURLToPath(new URL("../public/data", import.meta.url));
const REF = process.env.STINT_PARITY || fileURLToPath(new URL("./parity.json", import.meta.url));

test("mulberry32 golden values", () => {
  const r = new Mulberry32(1);
  assert.deepEqual([r.nextU32(), r.nextU32(), r.nextU32()], [2693262067, 11749833, 2265367787]);
});

test("simulator matches Python", { skip: !existsSync(REF) && "no parity.json" }, () => {
  const ref = JSON.parse(readFileSync(REF, "utf8"));
  assert.ok(ref.cases.length > 0, "no parity cases");
  for (const c of ref.cases) {
    const p = JSON.parse(readFileSync(join(DATA, "sim", "races", `${c.race_id}.json`), "utf8"));
    const st = stateAt(p, c.driver, c.state_index);
    const rules = { min_stops: p.rules.min_stops, max_set_life: p.rules.max_set_life };
    const best = bestByStops(p, st, rules, 2);
    for (const [k, s] of Object.entries(c.best_by_stops)) {
      assert.deepEqual(best[k].stop_laps, s.stop_laps, `${c.race_id} ${c.driver} ${k}-stop laps`);
      assert.deepEqual(best[k].compounds, s.compounds, `${c.race_id} ${c.driver} ${k}-stop compounds`);
    }
    const top = bestStrategies(p, st, rules, { maxStops: 2, top: 3 });
    assert.deepEqual(top.map((s) => [s.stop_laps, s.compounds]), c.top3.map((s) => [s.stop_laps, s.compounds]));
    c.strategies.forEach((s, i) => {
      assert.ok(Math.abs(expectedTime(p, st, s) - c.expected[i]) < 1e-6, "expected time");
    });
    for (const run of c.runs) {
      const r = simulate(p, st, c.strategies, { n: run.n, seed: run.seed, scMode: run.mode, scLap: run.sc_lap });
      assert.equal(r.scDraws, run.sc_draws, `${run.mode} safety-car draws`);
      run.times.forEach((row, i) => row.forEach((v, j) => {
        assert.ok(Math.abs(r.times[i][j] - v) < 1e-6, `${c.race_id} ${run.mode} draw ${i} strategy ${j}: ${r.times[i][j]} vs ${v}`);
      }));
    }
  }
});
