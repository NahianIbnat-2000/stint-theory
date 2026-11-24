// Port of simulation/constraints.py check().
export const SLICKS = ["SOFT", "MEDIUM", "HARD"];
export const MIN_STINT = 3;

export function check(s, st, rules) {
  const errs = [];
  const N = st.total_laps, L = st.decision_lap;
  const stops = [...s.stop_laps], comps = [...s.compounds];
  if (stops.length !== comps.length) errs.push("each stop needs a compound");
  if (comps.some((c) => !SLICKS.includes(c))) errs.push("only dry compounds (soft, medium, hard) are simulated");
  const sorted = [...stops].sort((a, b) => a - b);
  if (stops.some((v, i) => v !== sorted[i]) || new Set(stops).size !== stops.length)
    errs.push("stop laps must be increasing");
  if (stops.length && (stops[0] <= L || stops[stops.length - 1] >= N))
    errs.push(`stops must be between lap ${L + 1} and lap ${N - 1}`);
  const b = [L, ...stops, N];
  for (let i = 1; i < b.length - 1; i++) {
    if (b[i + 1] - b[i] < MIN_STINT) { errs.push(`stints after a stop must be at least ${MIN_STINT} laps`); break; }
  }
  const used = new Set([...st.compounds_used, st.current_compound, ...comps].filter((c) => SLICKS.includes(c)));
  if (used.size < 2) errs.push("a dry race requires at least two different compounds");
  if (st.stops_so_far + stops.length < (rules.min_stops || 0))
    errs.push(`this race requires at least ${rules.min_stops} pit stops`);
  const cap = rules.max_set_life;
  if (cap !== null && cap !== undefined) {
    const firstEnd = stops.length ? stops[0] : N;
    if (st.current_age + (firstEnd - L) > cap) errs.push(`current set would exceed ${cap} laps of life`);
    const ends = [...stops.slice(1), N];
    for (let i = 0; i < stops.length; i++) {
      if (ends[i] - stops[i] > cap) { errs.push(`a new set would exceed ${cap} laps of life`); break; }
    }
  }
  return errs;
}
