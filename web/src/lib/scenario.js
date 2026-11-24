// Simulator configuration <-> URL query string, so a scenario can be shared.
// Only identifiers and choices are stored: no data.
const COMP = { S: "SOFT", M: "MEDIUM", H: "HARD" };
export const SC_MODES = ["none", "random", "at_lap"];
export const CANDIDATES = ["observed", "plan", "best0", "best1", "best2", "best3"];

export function encodeScenario(s) {
  const q = new URLSearchParams();
  if (s.race) q.set("race", s.race);
  if (s.driver) q.set("driver", s.driver);
  if (Number.isInteger(s.lap)) q.set("lap", String(s.lap));
  if (s.sc && s.sc !== "none") q.set("sc", s.sc);
  if (s.sc === "at_lap" && Number.isInteger(s.scLap)) q.set("scLap", String(s.scLap));
  if (s.plan?.length) q.set("plan", s.plan.map((p) => `${p.lap}:${p.comp[0]}`).join(","));
  if (s.a) q.set("a", s.a);
  if (s.b) q.set("b", s.b);
  return q.toString();
}

// Invalid parts are dropped, never guessed.
export function decodeScenario(text) {
  const q = new URLSearchParams(text);
  const int = (k) => (/^\d+$/.test(q.get(k) || "") ? parseInt(q.get(k), 10) : undefined);
  const out = {};
  if (/^\d{4}_\d{2}$/.test(q.get("race") || "")) out.race = q.get("race");
  if (/^[A-Z]{3}$/.test(q.get("driver") || "")) out.driver = q.get("driver");
  if (int("lap") !== undefined) out.lap = int("lap");
  if (SC_MODES.includes(q.get("sc"))) out.sc = q.get("sc");
  if (int("scLap") !== undefined) out.scLap = int("scLap");
  const plan = (q.get("plan") || "").split(",").filter(Boolean).map((x) => {
    const m = /^(\d+):([SMH])$/.exec(x);
    return m ? { lap: parseInt(m[1], 10), comp: COMP[m[2]] } : null;
  });
  if (plan.length && plan.every(Boolean) && plan.length <= 3) out.plan = plan;
  for (const k of ["a", "b"]) if (CANDIDATES.includes(q.get(k))) out[k] = q.get(k);
  return out;
}
