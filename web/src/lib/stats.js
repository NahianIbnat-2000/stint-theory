// Summaries of simulated outcomes. Every number comes from the draws of the engine.
export function quantile(arr, q) {
  const s = [...arr].sort((a, b) => a - b), pos = (s.length - 1) * q;
  const lo = Math.floor(pos), hi = Math.ceil(pos);
  return s[lo] + (s[hi] - s[lo]) * (pos - lo);
}
const mean = (a) => a.reduce((x, y) => x + y, 0) / a.length;

// B minus A, draw by draw (common random numbers). Negative = B faster.
export function duelStats(times, ia, ib) {
  const d = times.map((r) => r[ib] - r[ia]);
  return {
    n: d.length, diffs: d, mean: mean(d), median: quantile(d, 0.5),
    p05: quantile(d, 0.05), p95: quantile(d, 0.95),
    pBFaster: d.filter((x) => x < 0).length / d.length,
    meanA: mean(times.map((r) => r[ia])), meanB: mean(times.map((r) => r[ib])),
  };
}

export function histogram(values, nBins = 30) {
  const lo = Math.min(...values), hi = Math.max(...values);
  const w = hi > lo ? (hi - lo) / nBins : 1;
  const bins = Array.from({ length: nBins }, (_, i) => ({ x0: lo + i * w, x1: lo + (i + 1) * w, n: 0 }));
  for (const v of values) bins[Math.min(nBins - 1, Math.floor((v - lo) / w))].n++;
  return bins;
}
