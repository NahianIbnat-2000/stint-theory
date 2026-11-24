// Port of simulation/strategy.py: exact dynamic programme over stop laps and compounds.
import { Pace } from "./engine.js";
import { MIN_STINT, SLICKS, check } from "./constraints.js";

export function bestStrategies(p, st, rules, { maxStops = 3, top = 5, exact = false } = {}) {
  const pace = new Pace(p);
  const L = st.decision_lap, N = st.total_laps, loss = p.pit_loss.mean_s;
  const cap = rules.max_set_life ?? null;
  const maxAge = st.current_age + N + 1;
  const prefix = {};
  for (const c of SLICKS) {
    const a = [0];
    let acc = 0;
    for (let k = 1; k <= maxAge; k++) { acc += pace.g(c, k); a.push(acc); }
    prefix[c] = a;
  }
  const cost = (comp, age0, a, b) => {
    const n = b - a;
    return pace.kappa(comp) * n + prefix[comp][age0 + n] - prefix[comp][age0];
  };
  const memo = new Map();
  const go = (start, comp, age0, used, left, made) => {
    const key = `${start}|${comp}|${age0}|${used.join(",")}|${left}|${made}`;
    if (memo.has(key)) return memo.get(key);
    const best = [];
    if ((cap === null || age0 + (N - start) <= cap) && used.filter((c) => SLICKS.includes(c)).length >= 2
        && st.stops_so_far + made >= (rules.min_stops || 0) && !(exact && left)) {
      best.push([cost(comp, age0, start, N), []]);
    }
    if (left) {
      const first = start + (start > L ? MIN_STINT : 1);
      for (let stop = first; stop <= N - MIN_STINT; stop++) {
        if (cap !== null && age0 + (stop - start) > cap) break;
        const here = cost(comp, age0, start, stop) + loss;
        for (const nc of SLICKS) {
          const u = [...new Set([...used, nc])].sort();
          for (const [c, path] of go(stop, nc, 0, u, left - 1, made + 1).slice(0, top)) {
            best.push([here + c, [[stop, nc], ...path]]);
          }
        }
      }
    }
    best.sort((a, b) => a[0] - b[0]);
    const out = best.slice(0, top);
    memo.set(key, out);
    return out;
  };
  const used0 = [...new Set([...st.compounds_used, st.current_compound])].sort();
  const out = [];
  for (const [c, path] of go(L, st.current_compound, st.current_age, used0, maxStops, 0)) {
    const s = { stop_laps: path.map((x) => x[0]), compounds: path.map((x) => x[1]), cost: c };
    if (!check(s, st, rules).length) out.push(s);
  }
  return out;
}

export function bestByStops(p, st, rules, maxStops = 3) {
  const res = {};
  for (let k = 0; k <= maxStops; k++) {
    const c = bestStrategies(p, st, rules, { maxStops: k, top: 1, exact: true });
    if (c.length) res[k] = c[0];
  }
  return res;
}
