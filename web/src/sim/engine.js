// Port of simulation/engine.py. Every random draw is taken in the same order as in
// Python, so the same seed gives the same numbers (checked by web/test/parity.test.mjs).
import { Mulberry32 } from "./rng.js";
import { SLICKS } from "./constraints.js";

export const DISCLAIMER =
  "Strategy outcomes are model-based counterfactual estimates, not observations of what would necessarily have happened.";
const FULL = { S: "SOFT", M: "MEDIUM", H: "HARD" };

export class Pace {
  constructor(p, coef = null) {
    this.c = coef || p.pace.coef;
    this.cap = p.pace.age_cap;
    this.scale = p.circuit.scale;
    this.tail = p.pace.tail_slope || {};
  }
  kappa(comp) { return this.c[`k_${comp}`] ?? 0; }
  g(comp, age) {
    const b1 = this.c[`age_${comp}`], b2 = this.c[`age2_${comp}`];
    let cap = this.cap;
    if (b2 < 0) cap = Math.min(cap, Math.max(-b1 / (2 * b2), 0));
    const a = Math.min(age, cap);
    const val = b1 * a + b2 * (a * a);
    let slopeCap = b1 + 2 * b2 * cap;
    if (comp in this.tail) slopeCap = Math.max(slopeCap, this.tail[comp]);
    return this.scale * (val + Math.max(age - cap, 0) * slopeCap);
  }
  lapMean(mu, lap, comp, age) {
    return mu + this.c.lap_number * lap + this.kappa(comp) + this.g(comp, age);
  }
}

export function stateAt(p, driver, i) {
  const s = p.drivers[driver].states;
  return {
    race_id: p.race_id, driver, decision_lap: s.lap[i], total_laps: p.total_laps,
    current_compound: s.comp[i], current_age: s.age[i], stops_so_far: s.stops[i],
    compounds_used: [...s.used[i]].map((c) => FULL[c]), mu: s.mu[i], mu_se: s.mu_se[i], n_pace_laps: s.n[i],
  };
}

export function observedStrategy(p, driver, lap) {
  const d = p.drivers[driver];
  if (!d.finished) return null;
  const stops = [], comps = [];
  for (const [ln, nxt] of d.stops) {
    if (ln > lap && ln < p.total_laps) {
      if (!SLICKS.includes(nxt)) return null;
      stops.push(ln); comps.push(nxt);
    }
  }
  return { stop_laps: stops, compounds: comps, label: "observed" };
}

export function describe(s, current) {
  const seq = [current[0], ...s.compounds.map((c) => c[0])].join("-");
  return `${seq} (stops: ${s.stop_laps.length ? s.stop_laps.join(", ") : "no further stops"})`;
}

export function lapPlan(st, s) {
  const L = st.decision_lap, N = st.total_laps;
  let comp = st.current_compound, age0 = st.current_age, start = L;
  const stops = new Map(s.stop_laps.map((l, i) => [l, s.compounds[i]]));
  const out = [];
  for (let j = L + 1; j <= N; j++) {
    const age = age0 + (j - start);
    const stop = stops.has(j);
    out.push([j, comp, age, stop]);
    if (stop) { comp = stops.get(j); age0 = 0; start = j; }
  }
  return out;
}

export function expectedTime(p, st, s, pace = null) {
  pace = pace || new Pace(p);
  let total = 0;
  for (const [j, c, a] of lapPlan(st, s)) total += pace.lapMean(st.mu, j, c, a);
  return total + s.stop_laps.length * p.pit_loss.mean_s;
}

export function cholesky(A) {
  const n = A.length, L = A.map(() => new Array(n).fill(0));
  for (let j = 0; j < n; j++) {
    let s = A[j][j];
    for (let k = 0; k < j; k++) s -= L[j][k] * L[j][k];
    L[j][j] = Math.sqrt(s);
    for (let i = j + 1; i < n; i++) {
      let t = A[i][j];
      for (let k = 0; k < j; k++) t -= L[i][k] * L[j][k];
      L[i][j] = t / L[j][j];
    }
  }
  return L;
}

export function simulate(p, st, strategies, { n = 1000, seed = 2026, scMode = "none", scLap = null } = {}) {
  const rng = new Mulberry32(seed);
  const names = p.pace.names;
  const b = names.map((k) => p.pace.coef[k]);
  const V = p.pace.vcov.map((row, i) => row.map((v, j) => v + (i === j ? 1e-12 : 0)));
  const Lc = cholesky(V);
  const L = st.decision_lap, N = st.total_laps, nLaps = N - L;
  const { phi, sigma_innov: sig, sigma_marginal: sig0 } = p.ar1;
  const pl = p.pit_loss, sc = p.safety_car;
  let pmf = Object.entries(sc.duration_pmf).map(([k, v]) => [parseInt(k, 10), v]).sort((a, b) => a[0] - b[0]);
  if (!pmf.length) pmf = [[4, 1.0]];
  const plans = strategies.map((s) => lapPlan(st, s));
  const T = Array.from({ length: n }, () => new Array(strategies.length).fill(0));
  let scDraws = 0;
  for (let i = 0; i < n; i++) {
    const z0 = rng.normals(b.length);
    const coef = {};
    names.forEach((k, r) => { let v = 0; for (let c = 0; c < b.length; c++) v += Lc[r][c] * z0[c]; coef[k] = b[r] + v; });
    const pace = new Pace(p, coef);
    const mu = st.mu + st.mu_se * rng.normal();
    const z = rng.normals(nLaps);
    const e = new Array(nLaps);
    e[0] = sig0 * z[0];
    for (let k = 1; k < nLaps; k++) e[k] = phi * e[k - 1] + sig * z[k];
    const shocks = rng.normals(8);
    const uSc = rng.uniforms(nLaps);
    const uLen = rng.uniform();
    let start = null;
    if (scMode === "random") {
      const h = uSc.findIndex((u) => u < sc.hazard_per_lap);
      start = h >= 0 ? L + 1 + h : null;
    } else if (scMode === "at_lap") start = scLap;
    const scLaps = new Set();
    if (start !== null) {
      let acc = 0, length = pmf[pmf.length - 1][0];
      for (const [k, w] of pmf) { acc += w; if (uLen <= acc) { length = k; break; } }
      for (let j = start; j < Math.min(start + length, N + 1); j++) scLaps.add(j);
      scDraws++;
    }
    plans.forEach((plan, col) => {
      let t = 0, nStop = 0;
      plan.forEach(([j, c, a, stop], k) => {
        let lapT = pace.lapMean(mu, j, c, a) + e[k];
        if (scLaps.has(j)) lapT *= sc.lap_time_factor;
        t += lapT;
        if (stop) {
          let loss = pl.mean_s + pl.sd_s * shocks[Math.min(nStop, 7)];
          if (scLaps.has(j)) loss *= pl.neutralised_factor;
          t += Math.max(loss, 0.5 * pl.mean_s);
          nStop++;
        }
      });
      T[i][col] = t;
    });
  }
  return { times: T, scDraws, n, seed, scMode };
}

const pct = (arr, q) => {
  const s = [...arr].sort((a, b) => a - b), pos = (s.length - 1) * q / 100;
  const lo = Math.floor(pos), hi = Math.ceil(pos);
  return s[lo] + (s[hi] - s[lo]) * (pos - lo);
};

export function summarise(res, strategies, ref = 0) {
  const T = res.times;
  return strategies.map((s, j) => {
    const col = T.map((r) => r[j]), d = T.map((r) => r[j] - r[ref]);
    return {
      strategy: s, mean: col.reduce((a, b) => a + b, 0) / col.length,
      p05: pct(col, 5), p95: pct(col, 95),
      delta: d.reduce((a, b) => a + b, 0) / d.length, d05: pct(d, 5), d95: pct(d, 95),
      pFaster: j === ref ? null : d.filter((x) => x < 0).length / d.length,
    };
  });
}
