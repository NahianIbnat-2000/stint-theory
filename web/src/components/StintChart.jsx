import { forwardRef } from "react";
import { COMPOUND } from "../data.js";
import { useTooltip } from "./Tooltip.jsx";

const OTHER = { INTERMEDIATE: "Intermediate", WET: "Wet" };
export const compoundInfo = (c) => COMPOUND[c] || { color: "var(--other)", short: (c || "?")[0], name: OTHER[c] || c || "Unknown" };

// Every driver's tyre stints, lap by lap. Rows: drivers who went furthest first.
const StintChart = forwardRef(function StintChart({ race, highlight, decisionLap, onPick, compact = false }, ref) {
  const tt = useTooltip();
  if (!race) return null;
  const N = race.total_laps;
  const drivers = Object.entries(race.drivers)
    .sort((a, b) => b[1].last_lap - a[1].last_lap || a[0].localeCompare(b[0]));
  const row = compact ? 15 : 22, left = 44, right = 30, top = 20, W = 760;
  const H = top + drivers.length * row + 24;
  const x = (lap) => left + ((lap - 1) / N) * (W - left - right);
  const ticks = [1, ...Array.from({ length: Math.floor(N / 10) }, (_, i) => (i + 1) * 10).filter((t) => t < N - 3), N];
  return (
    <figure className="chart">
      <div className="chart-box">
        <svg ref={ref} viewBox={`0 0 ${W} ${H}`} role="img"
          aria-label={`Tyre stints of every driver, ${race.event_name} ${race.season}`}>
          {ticks.map((t) => (
            <g key={t}>
              <line x1={x(t)} x2={x(t)} y1={top - 4} y2={H - 20} className="grid" />
              <text x={x(t)} y={H - 6} className="axis" textAnchor="middle">{t}</text>
            </g>
          ))}
          <text x={left} y={11} className="axis-title">Lap</text>
          {decisionLap && <line x1={x(decisionLap + 1)} x2={x(decisionLap + 1)} y1={top - 6} y2={H - 20} className="decision" />}
          {drivers.map(([code, d], i) => {
            const y = top + i * row;
            const on = highlight === code;
            return (
              <g key={code} className={`stint-row${on ? " on" : ""}${highlight && !on ? " dim" : ""}`}
                onClick={onPick ? () => onPick(code) : undefined} style={onPick ? { cursor: "pointer" } : undefined}>
                <text x={left - 7} y={y + row * 0.68} textAnchor="end" className="row-label" style={compact ? { fontSize: 10 } : undefined}>{code}</text>
                {d.stints.map(([comp, a, b], k) => {
                  const c = compoundInfo(comp);
                  const x0 = x(a) + 1, w = Math.max(x(b + 1) - x(a) - 2, 1);
                  return (
                    <g key={k} onMouseMove={(e) => tt.show(e, `${code}: ${c.name}, laps ${a}–${b} (${b - a + 1} laps)`)} onMouseLeave={tt.hide}>
                      <rect x={x0} y={y + 2} width={w} height={row - 4} rx={compact ? 2 : 4} fill={c.color} />
                      {w > 16 && !compact && <text x={x0 + w / 2} y={y + 15} textAnchor="middle" className={`bar-label${comp === "MEDIUM" ? " dark" : ""}`}>{c.short}</text>}
                    </g>
                  );
                })}
                {["dnf", "dsq", "dns"].includes(d.status) && <text x={x(d.last_lap + 1) + 4} y={y + row * 0.68} className="axis">{d.status === "dsq" ? "DSQ" : "out"}</text>}
              </g>
            );
          })}
        </svg>
        {tt.node}
      </div>
      {!compact && (
        <figcaption>
          <Legend /> Each bar is one set of tyres. “out” marks a retirement (official classification); lapped cars end a lap or two early.
          {onPick && " Select a row to pick that driver."}
        </figcaption>
      )}
    </figure>
  );
});
export default StintChart;

export function Legend() {
  return (
    <span className="legend">
      {Object.entries(COMPOUND).map(([k, c]) => (
        <span key={k}><i style={{ background: c.color, color: k === "MEDIUM" ? "var(--graphite)" : "#fff" }}>{c.short}</i>{c.name}</span>
      ))}
      <span><i style={{ background: "var(--other)" }}>W</i>Wet-weather tyres</span>
    </span>
  );
}
