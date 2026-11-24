import { useTooltip } from "./Tooltip.jsx";
import { useWidth } from "./useWidth.js";
import { fmt, signed } from "../format.js";
import { name, familyOf } from "../models.js";

// Ranked dots with 95% intervals where they exist. rows: {model, value, lo, hi}
export default function ModelRanking({ rows, metric, selected, onSelect, svgRef }) {
  const tt = useTooltip();
  const [ref, width] = useWidth();
  const narrow = width > 0 && width < 620;
  const lower = metric.lowerIsBetter !== false;
  const sorted = [...rows].sort((a, b) => (metric.key === "bias" ? Math.abs(a.value) - Math.abs(b.value) : lower ? a.value - b.value : b.value - a.value));
  const longest = Math.max(...rows.map((r) => `${name(r.model)}  ${familyOf(r.model)}`.length + 4));
  const W = narrow ? 420 : 820, left = narrow ? 14 : Math.min(440, 30 + longest * 7.3), right = 30, row = narrow ? 46 : 34, top = 18;
  const H = top + sorted.length * row + 34;
  const vals = sorted.flatMap((r) => [r.value, r.lo ?? r.value, r.hi ?? r.value]);
  let lo = Math.min(...vals), hi = Math.max(...vals);
  if (metric.key === "bias") { const m = Math.max(Math.abs(lo), Math.abs(hi)); lo = -m; hi = m; }
  const pad = (hi - lo) * 0.06 || 0.01;
  lo -= pad; hi += pad;
  const x = (v) => left + ((v - lo) / (hi - lo)) * (W - left - right);
  const ticks = Array.from({ length: 5 }, (_, i) => lo + ((hi - lo) * i) / 4);
  return (
    <figure className="chart">
      <div className="chart-box" ref={ref}>
        <svg ref={svgRef} viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`Models ranked by ${metric.label}`}>
          {ticks.map((t, i) => <g key={i}><line x1={x(t)} x2={x(t)} y1={top - 6} y2={H - 28} className="grid" />
            <text x={x(t)} y={H - 12} textAnchor="middle" className="axis">{fmt(t, metric.digits ?? 3)}</text></g>)}
          {metric.key === "bias" && <line x1={x(0)} x2={x(0)} y1={top - 6} y2={H - 28} className="zero" />}
          {sorted.map((r, i) => {
            const y = top + i * row + (narrow ? row - 12 : row / 2);
            const on = selected === r.model;
            return (
              <g key={r.model} style={{ cursor: "pointer" }} onClick={() => onSelect?.(r.model)}
                onMouseMove={(e) => tt.show(e, <><b>{name(r.model)}</b> ({familyOf(r.model).toLowerCase()})<br />{metric.label}: {fmt(r.value, 4)} s{r.lo != null ? <><br />95% interval [{fmt(r.lo, 4)}, {fmt(r.hi, 4)}]</> : null}</>)}
                onMouseLeave={tt.hide}>
                <rect x={0} y={y - row / 2} width={W} height={row} fill={on ? "var(--canvas)" : "transparent"} />
                <text x={narrow ? left : left - 12} y={narrow ? y - 12 : y + 4} textAnchor={narrow ? "start" : "end"} className="row-label" style={on ? { fill: "var(--red)" } : undefined}>
                  {i + 1}. {name(r.model)}<tspan className="row-sub" dx="6">{familyOf(r.model)}</tspan>
                </text>
                {r.lo != null && <line x1={x(r.lo)} x2={x(r.hi)} y1={y} y2={y} className="ci95" />}
                <circle cx={x(r.value)} cy={y} r={on ? 6.5 : 5} className="point" style={on ? { stroke: "var(--red)" } : undefined} />
              </g>
            );
          })}
          <text x={left} y={H - 1} className="axis-title">{metric.label} (s){lower && metric.key !== "bias" ? ", lower is better" : metric.key === "bias" ? ", closer to 0 is better" : ""}</text>
        </svg>
        {tt.node}
      </div>
    </figure>
  );
}

export { signed };
