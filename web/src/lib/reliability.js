import { fmt, signed } from "../format.js";

const pct = (x, d = 1) => (x == null ? "–" : `${fmt(100 * x, d)}%`);

// Plain reading of the calibration numbers, from fixed rules.
export function calibrationReading(c, bias) {
  const miss = c.below90 + c.above90;
  const lo = Math.min(c.below90, c.above90), hi = Math.max(c.below90, c.above90);
  const side = c.below90 > c.above90 ? "faster" : "slower";
  if (miss <= 0.13) return "The ranges contain the actual time about as often as they claim to.";
  const parts = [`The 90% range missed ${pct(miss)} of the time, against 10% expected.`];
  if (hi > 2 * lo) {
    parts.push(`The misses are lopsided: drivers were mostly ${side} than the whole range (${pct(hi)} against ${pct(lo)} on the other side). That points to the centre of the range being off${bias != null ? `, matching the ${signed(bias, 1)} s bias above` : ""}, not to the range being too narrow.`);
  } else {
    parts.push("The misses fall on both sides about equally, so the ranges are too narrow.");
  }
  parts.push("Read the ranges as the spread the model knows about when comparing plans, not as a forecast interval for a finishing time.");
  return parts.join(" ");
}
