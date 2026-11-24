// The plans the simulator compares: what happened, the user's plan (if allowed),
// and the model's best plan for each number of further stops.
import { observedStrategy } from "../sim/engine.js";
import { bestByStops } from "../sim/strategy.js";
import { check } from "../sim/constraints.js";

export const N_DRAWS = 1000;
export const SEED = 2026;
export const LABEL = { observed: "What the driver did", plan: "Your plan", best0: "Best 0-stop", best1: "Best 1-stop", best2: "Best 2-stop", best3: "Best 3-stop" };

export function rulesOf(race) {
  return { min_stops: race.rules.min_stops, max_set_life: race.rules.max_set_life };
}

export function candidates(race, driver, st, plan = []) {
  const rules = rulesOf(race);
  const out = [];
  const obs = observedStrategy(race, driver, st.decision_lap);
  if (obs) out.push({ id: "observed", ...obs });
  if (plan.length) {
    const s = { stop_laps: plan.map((p) => p.lap), compounds: plan.map((p) => p.comp) };
    if (!check(s, st, rules).length) out.push({ id: "plan", ...s });
  }
  Object.entries(bestByStops(race, st, rules, 3)).forEach(([n, s]) => out.push({ id: `best${n}`, stop_laps: s.stop_laps, compounds: s.compounds }));
  return out.map((c) => {
    const same = out.filter((o) => o.stop_laps.join() === c.stop_laps.join() && o.compounds.join() === c.compounds.join());
    return { ...c, label: LABEL[c.id], alsoIs: same.filter((o) => o.id !== c.id).map((o) => LABEL[o.id]) };
  });
}
