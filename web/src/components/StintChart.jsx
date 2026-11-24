import { COMPOUND } from "../data.js";
import { useTooltip } from "./Tooltip.jsx";

const OTHER = { INTERMEDIATE: "Intermediate", WET: "Wet" };

// Every driver's tyre stints, lap by lap. Rows: drivers who went furthest first.
export default function StintChart({ race, highlight, decisionLap, onPick }) {
  const tt = useTooltip();
  if (!race) return null;
  const N = race.total_laps;
  const drivers = Object.entries(race.drivers)
    .sort((a, b) => b[1].last_lap - a[1].last_lap || a[0].localeCompare(b[0]));
  const row = 22, left = 48, right = 12, top = 22, W = 760;
  const H = top + drivers.length * row + 26;
  const x = (lap) => left + ((lap - 1) / N) * (W - left - right);
  const ticks = [1, ...Array.from({ length: Math.floor(N / 10) }, (_, i) => (i + 1) * 10).filter((t) => t < N), N];
  return (
    <figure className="chart">
      <div className="chart-box">
        <svg viewBox={`0 0 ${W} ${H}`} role="img"
          aria-label={`Tyre stints of every driver, ${race.event_name} ${race.season}`}>
          {ticks.map((t) => (
            <g key={t}>
              <line x1={x(t)} x2={x(t)} y1={top - 4} y2={H - 22} className="grid" />
              <text x={x(t)} y={H - 8} className="axis" textAnchor="middle">{t}</text>
            </g>
          ))}
          <text x={left} y={12} className="axis">Lap</text>
          {decisionLap && <line x1={x(decisionLap + 1)} x2={x(decisionLap + 1)} y1={top - 6} y2={H - 22} className="decision" />}
          {drivers.map(([code, d], i) => {
            const y = top + i * row;
            const on = highlight === code;
            return (
              <g key={code} className={`stint-row${on ? " on" : ""}${highlight && !on ? " dim" : ""}`}
                onClick={onPick ? () => onPick(code) : undefined} style={onPick ? { cursor: "pointer" } : undefined}>
                <text x={left - 8} y={y + 15} textAnchor="end" className="row-label">{code}</text>
                {d.stints.map(([comp, a, b], k) => {
                  const c = COMPOUND[comp];
                  const x0 = x(a) + 1, w = Math.max(x(b + 1) - x(a) - 2, 1);
                  const label = c ? c.name : OTHER[comp] || comp || "Unknown";
                  return (
                    <g key={k} onMouseMove={(e) => tt.show(e, `${code}: ${label}, laps ${a}–${b} (${b - a + 1} laps)`)} onMouseLeave={tt.hide}>
                      <rect x={x0} y={y + 3} width={w} height={row - 6} rx={4}
                        fill={c ? c.color : "var(--other)"} />
                      {w > 16 && <text x={x0 + w / 2} y={y + 15} textAnchor="middle" className="bar-label">{c ? c.short : (comp || "?")[0]}</text>}
                    </g>
                  );
                })}
                {["dnf", "dsq", "dns"].includes(d.status) && <text x={x(d.last_lap + 1) + 4} y={y + 15} className="axis">{d.status === "dsq" ? "DSQ" : "out"}</text>}
              </g>
            );
          })}
        </svg>
        {tt.node}
      </div>
      <figcaption>
        <Legend /> Each bar is one set of tyres; letters give the compound. “out” marks a car that retired (official classification); lapped cars end a lap or two early.
        {onPick && " Click a row to pick that driver."}
      </figcaption>
    </figure>
  );
}

export function Legend() {
  return (
    <span className="legend">
      {Object.values(COMPOUND).map((c) => (
        <span key={c.short}><i style={{ background: c.color }} />{c.name}</span>
      ))}
      <span><i style={{ background: "var(--other)" }} />Wet weather tyres</span>
    </span>
  );
}
