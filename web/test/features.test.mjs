// Tests for the simulator page features, run on the exported races (real data).
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { simulate, summarise, stateAt, expectedTime } from "../src/sim/engine.js";
import { bestByStops } from "../src/sim/strategy.js";
import { encodeScenario, decodeScenario } from "../src/lib/scenario.js";
import { duelStats, histogram } from "../src/lib/stats.js";
import { stopLapCurve, gapGrid, withParams } from "../src/lib/sensitivity.js";
import { explainDuel } from "../src/lib/explain.js";
import { toCSV } from "../src/lib/export.js";
import { candidates, rulesOf } from "../src/lib/candidates.js";
import { ROUTES } from "../src/routes.js";

const DATA = process.env.STINT_WEB_DATA || fileURLToPath(new URL("../public/data", import.meta.url));
const SRC = fileURLToPath(new URL("../src", import.meta.url));
const haveData = existsSync(join(DATA, "sim", "index.json"));
const races = haveData ? JSON.parse(readFileSync(join(DATA, "sim", "index.json"), "utf8")).filter((r) => r.simulatable) : [];
const loadRace = (id) => JSON.parse(readFileSync(join(DATA, "sim", "races", `${id}.json`), "utf8"));

function scenario() {
  const race = loadRace(races.at(-1).race_id);
  const driver = Object.keys(race.drivers).sort().find((d) => race.drivers[d].states.lap.length > 5 && race.drivers[d].finished);
  const s = race.drivers[driver].states;
  const st = stateAt(race, driver, Math.floor(s.lap.length / 3));
  return { race, driver, st };
}

test("scenario links round-trip and drop invalid parts", () => {
  const s = { race: "2025_24", driver: "ALB", lap: 21, sc: "at_lap", scLap: 30, plan: [{ lap: 33, comp: "MEDIUM" }, { lap: 45, comp: "SOFT" }], a: "observed", b: "best2" };
  assert.deepEqual(decodeScenario(encodeScenario(s)), s);
  assert.deepEqual(decodeScenario("race=x&driver=alb&lap=-3&sc=rain&plan=10:Q&a=hack"), {});
  assert.equal(encodeScenario({ race: "2025_01", sc: "none" }), "race=2025_01");
});

test("duel statistics are computed from the same draws as the engine summary", { skip: !haveData }, () => {
  const { race, driver, st } = scenario();
  const c = candidates(race, driver, st);
  const r = simulate(race, st, c, { n: 300, seed: 7 });
  const sum = summarise(r, c);
  const d = duelStats(r.times, 0, c.length - 1);
  assert.ok(Math.abs(d.mean - sum.at(-1).delta) < 1e-9);
  assert.ok(Math.abs(d.meanA - sum[0].mean) < 1e-9);
  assert.ok(d.p05 <= d.median && d.median <= d.p95);
  assert.ok(Math.abs(d.pBFaster - sum.at(-1).pFaster) < 1e-12);
  assert.equal(histogram(d.diffs, 20).reduce((a, b) => a + b.n, 0), 300);
});

test("candidates: best plans match the optimiser, duplicates are flagged", { skip: !haveData }, () => {
  const { race, driver, st } = scenario();
  const c = candidates(race, driver, st);
  const best = bestByStops(race, st, rulesOf(race), 3);
  for (const [k, s] of Object.entries(best)) {
    const got = c.find((x) => x.id === `best${k}`);
    assert.deepEqual([got.stop_laps, got.compounds], [s.stop_laps, s.compounds]);
  }
  for (const x of c) for (const y of x.alsoIs) assert.ok(c.some((z) => z.label === y && z.stop_laps.join() === x.stop_laps.join()));
  const bad = candidates(race, driver, st, [{ lap: st.decision_lap, comp: "SOFT" }]);
  assert.ok(!bad.some((x) => x.id === "plan"), "a plan that breaks the rules is not compared");
});

test("sensitivity runs use the engine: pit-loss shifts move the gap by exactly that much per extra stop", { skip: !haveData }, () => {
  const { race, driver, st } = scenario();
  const c = candidates(race, driver, st);
  const a = c.find((x) => x.stop_laps.length === 0) || c[0];
  const b = c.find((x) => x.stop_laps.length !== a.stop_laps.length);
  if (!b) return;
  const g = gapGrid(race, st, a, b, [-2, 0, 2], [0.8, 1, 1.2]);
  const base = expectedTime(race, st, b) - expectedTime(race, st, a);
  assert.ok(Math.abs(g[1][1] - base) < 1e-9, "centre cell is the fitted model");
  const extra = b.stop_laps.length - a.stop_laps.length;
  assert.ok(Math.abs(g[1][2] - g[1][1] - 2 * extra) < 1e-9);
  assert.equal(withParams(race, {}).pit_loss.mean_s, race.pit_loss.mean_s);
});

test("moving a stop: the curve's best lap is the optimiser's best lap", { skip: !haveData }, () => {
  const { race, st } = scenario();
  const best1 = bestByStops(race, st, rulesOf(race), 1)[1];
  if (!best1) return;
  const curve = stopLapCurve(race, st, best1, rulesOf(race), 0);
  const top = curve.find((r) => r.vsBest === 0);
  assert.equal(top.lap, best1.stop_laps[0]);
  assert.ok(curve.every((r) => r.vsBest >= 0));
});

test("explanations follow the numbers", () => {
  const a = { id: "observed", label: "What the driver did", stop_laps: [30], compounds: ["HARD"] };
  const b = { id: "best0", label: "Best 0-stop", stop_laps: [], compounds: [] };
  const tie = explainDuel({ a, b, stats: { mean: 0.3, p05: -2, p95: 3, pBFaster: 0.45 } });
  assert.match(tie[0], /^No reliable winner/);
  assert.match(tie[1], /differ by 1 stop/);
  const clear = explainDuel({ a, b, stats: { mean: -8, p05: -12, p95: -4, pBFaster: 0.97 } });
  assert.match(clear[0], /^The best 0-stop plan is faster in 97%/);
});

test("CSV export escapes text and keeps numbers", () => {
  const csv = toCSV([{ p: 'H-M (stops: 33, "x")', v: 1.5 }], [{ label: "plan", value: "p" }, { label: "v", value: (r) => r.v.toFixed(2) }]);
  assert.equal(csv, 'plan,v\n"H-M (stops: 33, ""x"")",1.50\n');
});

test("navigation: unique paths, every route has a page and a title", () => {
  const app = readFileSync(join(SRC, "App.jsx"), "utf8");
  assert.equal(new Set(ROUTES.map((r) => r.path)).size, ROUTES.length);
  for (const r of ROUTES) {
    assert.ok(r.title && r.label);
    assert.ok(app.includes(`"${r.path}":`), `no page for ${r.path}`);
  }
});

test("every report and result file the pages read was exported", { skip: !haveData }, () => {
  const man = JSON.parse(readFileSync(join(DATA, "manifest.json"), "utf8"));
  const files = readdirSync(join(SRC, "pages")).map((f) => readFileSync(join(SRC, "pages", f), "utf8")).join("\n");
  for (const m of files.matchAll(/name="([a-z0-9_]+)"/g)) assert.ok(man.reports.includes(m[1]), `report ${m[1]} not exported`);
  const methods = readFileSync(join(SRC, "pages", "Methods.jsx"), "utf8");
  for (const m of methods.matchAll(/\["([a-z0-9_]+)", "/g)) assert.ok(man.reports.includes(m[1]), `doc ${m[1]} not exported`);
  // pages show a "re-export" note when these are absent (added after the first export)
  const OPTIONAL = new Set(["results/test_errors.json", "results/sim_backtest.json"]);
  for (const m of files.matchAll(/useData\("(results\/[a-z0-9_]+\.json)"/g)) if (!OPTIONAL.has(m[1])) assert.ok(existsSync(join(DATA, m[1])), `${m[1]} missing`);
});

