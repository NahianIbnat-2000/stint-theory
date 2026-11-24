// Plain-language reading of a duel, built from fixed rules (no generated text).
import { fmt } from "../format.js";

export const PRACTICAL_S = 1.0;      // gaps below this are treated as no difference
// "Best 1-stop" -> "the best 1-stop plan"; "What the driver did" -> "what the driver did"
export const phrase = (s) => (s.id === "observed" ? "what the driver did" : s.id === "plan" ? "your plan" : `the ${s.label.toLowerCase()} plan`);
const cap = (t) => t.charAt(0).toUpperCase() + t.slice(1);

export function explainDuel({ a, b, stats }) {
  const out = [];
  const nA = a.stop_laps.length, nB = b.stop_laps.length;
  const gap = Math.abs(stats.mean);
  const faster = stats.mean < 0 ? b : a, slower = stats.mean < 0 ? a : b;
  const spans0 = stats.p05 < 0 && stats.p95 > 0;
  if (gap < PRACTICAL_S && spans0) {
    out.push(`No reliable winner: the expected gap is ${fmt(gap, 1)} s and the 90% range runs from ${fmt(stats.p05, 1)} to ${fmt(stats.p95, 1)} s, so either plan can come out ahead.`);
  } else if (spans0) {
    out.push(`${cap(phrase(faster))} is expected to be ${fmt(gap, 1)} s faster than ${phrase(slower)}, but the 90% range (${fmt(stats.p05, 1)} to ${fmt(stats.p95, 1)} s) includes zero: it is faster in ${fmt(100 * (stats.mean < 0 ? stats.pBFaster : 1 - stats.pBFaster), 0)}% of simulated races.`);
  } else {
    out.push(`${cap(phrase(faster))} is faster in ${fmt(100 * (stats.mean < 0 ? stats.pBFaster : 1 - stats.pBFaster), 0)}% of simulated races, by ${fmt(gap, 1)} s on average (90% range ${fmt(stats.p05, 1)} to ${fmt(stats.p95, 1)} s).`);
  }
  if (nA !== nB) {
    out.push(`The plans differ by ${Math.abs(nA - nB)} stop${Math.abs(nA - nB) > 1 ? "s" : ""}. The backtest found fresh tyres modelled about 0.4 s/lap too slow for the first laps of a stint, so each extra stop is likely overcharged by roughly 1–2 s. Read a gap of that size in favour of fewer stops as a tie.`);
  }
  out.push("Track position is not modelled. A plan that is faster against the clock can still lose places in traffic, and that matters most where overtaking is hard (Monaco, Singapore, Hungary).");
  out.push("The range covers uncertainty the model knows about: its parameters, the driver’s pace, lap-to-lap noise, pit-stop times and safety cars. It does not cover the model being wrong in a systematic way; the backtest measures that separately.");
  return out;
}
