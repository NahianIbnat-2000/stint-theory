import { useTooltip } from "./Tooltip.jsx";
import { useWidth } from "./useWidth.js";
import { fmt } from "../format.js";

// Point estimates with 95% intervals, one row each. rows: {label, sub, value, lo, hi, color, mark}
export default function DotCI({ rows, axisLabel, digits = 3, zero = true, svgRef, ariaLabel }) {
  const tt = useTooltip();
  const [ref, width] = useWidth();
  const narrow = width > 0 && width < 620;
  const longest = Math.max(...rows.map((r) => (r.label || "").length + (r.sub ? r.sub.length * 0.85 + 1 : 0)), 4);
  const W = narrow ? 420 : 820, left = narrow ? 14 : Math.min(420, 34 + longest * 7.4), right = 24, row = narrow ? 40 : 26, top = 10;
  const H = top + rows.length * row + 36;
  const vals = rows.flatMap((r) => [r.lo ?? r.value, r.hi ?? r.value]).concat(zero ? [0] : []);
  let lo = Math.min(...vals), hi = Math.max(...vals);
  const pad = (hi - lo) * 0.06 || 0.01; lo -= pad; hi += pad;
  const x = (v) => left + ((v - lo) / (hi - lo)) * (W - left - right);
  const ticks = Array.from({ length: 5 }, (_, i) => lo + ((hi - lo) * i) / 4);
  return (
    <figure className="chart">
      <div className="chart-box" ref={ref}>
        <svg ref={svgRef} viewBox={`0 0 ${W} ${H}`} role="img" aria-label={ariaLabel || axisLabel}>
          {ticks.map((t, i) => <g key={i}><line x1={x(t)} x2={x(t)} y1={top - 4} y2={H - 30} className="grid" />
            <text x={x(t)} y={H - 14} textAnchor="middle" className="axis">{fmt(t, digits)}</text></g>)}
          {zero && lo < 0 && hi > 0 && <line x1={x(0)} x2={x(0)} y1={top - 4} y2={H - 30} className="zero" />}
          {rows.map((r, i) => {
            const y = top + i * row + (narrow ? row - 10 : row / 2);
            return (
              <g key={i} onMouseMove={(e) => tt.show(e, <><b>{r.label}</b>{r.sub ? ` (${r.sub})` : ""}<br />{fmt(r.value, digits + 1)}{r.lo != null ? ` [${fmt(r.lo, digits + 1)}, ${fmt(r.hi, digits + 1)}]` : ""}{r.n ? <><br />{r.n}</> : null}</>)} onMouseLeave={tt.hide}>
                <rect x={0} y={y - row / 2} width={W} height={row} fill="transparent" />
                <text x={narrow ? left : left - 10} y={narrow ? y - 10 : y + 4} textAnchor={narrow ? "start" : "end"} className="row-label" style={{ fontWeight: r.strong ? 700 : 500 }}>
                  {r.label}{r.sub && <tspan className="row-sub" dx="6">{r.sub}</tspan>}
                </text>
                {r.lo != null && <line x1={x(r.lo)} x2={x(r.hi)} y1={y} y2={y} stroke={r.color || "var(--graphite)"} strokeWidth="2" />}
                <circle cx={x(r.value)} cy={y} r={r.mark ? 7 : 5} fill={r.color || "var(--panel)"} stroke={r.color ? "var(--panel)" : "var(--graphite)"} strokeWidth="2" />
                {r.mark && <text x={x(r.value)} y={y + 3.5} textAnchor="middle" className={`bar-label${r.mark === "M" ? " dark" : ""}`} style={{ fontSize: 9 }}>{r.mark}</text>}
              </g>
            );
          })}
          <text x={left} y={H - 1} className="axis-title">{axisLabel}</text>
        </svg>
        {tt.node}
      </div>
    </figure>
  );
}
