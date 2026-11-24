// Sensitivity runs. Each value is the simulator's own expected remaining race time
// (engine.expectedTime: no safety car, noise has mean zero) under changed inputs.
import { expectedTime } from "../sim/engine.js";
import { check } from "../sim/constraints.js";

export function withParams(p, { pitDelta = 0, wearMult = 1 } = {}) {
  return {
    ...p,
    pit_loss: { ...p.pit_loss, mean_s: p.pit_loss.mean_s + pitDelta },
    circuit: { ...p.circuit, scale: p.circuit.scale * wearMult },
  };
}

// Move one stop of a strategy across every allowed lap, others fixed.
export function stopLapCurve(p, st, s, rules, stopIndex = 0) {
  const out = [];
  for (let lap = st.decision_lap + 1; lap < st.total_laps; lap++) {
    const laps = [...s.stop_laps];
    laps[stopIndex] = lap;
    const cand = { stop_laps: laps, compounds: s.compounds };
    if (check(cand, st, rules).length) continue;
    out.push({ lap, expected: expectedTime(p, st, cand) });
  }
  const best = Math.min(...out.map((r) => r.expected));
  return out.map((r) => ({ ...r, vsBest: r.expected - best }));
}

// Expected gap B - A over a grid of pit-loss shifts (s) and tyre-wear multipliers.
export function gapGrid(p, st, a, b, pitDeltas, wearMults) {
  return wearMults.map((w) => pitDeltas.map((d) => {
    const q = withParams(p, { pitDelta: d, wearMult: w });
    return expectedTime(q, st, b) - expectedTime(q, st, a);
  }));
}
