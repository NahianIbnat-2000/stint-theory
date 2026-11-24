import { useTooltip } from "./Tooltip.jsx";
import { histogram } from "../lib/stats.js";
import { fmt, signed } from "../format.js";

// Distribution of B - A over the simulated races (same draws for both plans).
export function DuelHistogram({ stats, a, b, svgRef }) {
  const tt = useTooltip();
  const bins = histogram(stats.diffs, 32);
  const W = 760, H = 230, left = 44, right = 16, top = 26, bottom = 40;
  const lo = Math.min(bins[0].x0, 0), hi = Math.max(bins.at(-1).x1, 0);
  const x = (v) => left + ((v - lo) / (hi - lo)) * (W - left - right);
  const maxN = Math.max(...bins.map((v) => v.n));
  const y = (n) => top + (1 - n / maxN) * (H - top - bottom);
  return (
    <figure className="chart">
      <div className="chart-box">
        <svg ref={svgRef} viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`Distribution of the time gap between ${b.label} and ${a.label}`}>
          <rect x={x(stats.p05)} y={top - 14} width={Math.max(x(stats.p95) - x(stats.p05), 1)} height={H - top - bottom + 14} className="band" />
          <text x={x(stats.p05) + 3} y={top - 4} className="axis">90% of races</text>
          {bins.map((v, i) => {
            const fill = v.x1 <= 0 ? "var(--series-b)" : v.x0 >= 0 ? "var(--series-a)" : "var(--text-2)";
            return (
              <rect key={i} x={x(v.x0) + 1} y={y(v.n)} width={Math.max(x(v.x1) - x(v.x0) - 2, 1)} height={H - bottom - y(v.n)} rx={2} fill={fill}
                onMouseMove={(e) => tt.show(e, `${v.n} of ${stats.n} races: ${b.key} − ${a.key} between ${signed(v.x0, 1)} and ${signed(v.x1, 1)} s`)} onMouseLeave={tt.hide} />
            );
          })}
          <line x1={x(0)} x2={x(0)} y1={top - 6} y2={H - bottom} className="zero" />
          <line x1={x(stats.mean)} x2={x(stats.mean)} y1={top - 6} y2={H - bottom} stroke="var(--red)" strokeWidth="2" />
          <text x={x(stats.mean) + 4} y={top + 4} className="axis" style={{ fill: "var(--red)" }}>mean {signed(stats.mean, 1)}</text>
          {[lo, hi, 0].map((t, i) => <text key={i} x={x(t)} y={H - 22} textAnchor="middle" className="axis">{signed(t, 1)}</text>)}
          <text x={left} y={H - 4} className="axis-title">← {b.key} faster · seconds ({b.key} minus {a.key}) · {a.key} faster →</text>
        </svg>
        {tt.node}
      </div>
    </figure>
  );
}

// Expected remaining time when one stop moves, relative to its best lap.
export function StopLapCurve({ curve, current, color, label, svgRef }) {
  const tt = useTooltip();
  if (curve.length < 2) return <p className="muted">This plan has no stop that can move within the rules.</p>;
  const W = 760, H = 220, left = 50, right = 20, top = 16, bottom = 40;
  const lx = curve.map((r) => r.lap), vy = curve.map((r) => r.vsBest);
  const x = (l) => left + ((l - lx[0]) / Math.max(lx.at(-1) - lx[0], 1)) * (W - left - right);
  const top_ = Math.max(...vy) || 1;
  const y = (v) => top + (v / top_) * (H - top - bottom);
  const best = curve.find((r) => r.vsBest === 0);
  return (
    <figure className="chart">
      <div className="chart-box">
        <svg ref={svgRef} viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`Expected time cost of moving the stop of ${label}`}>
          {[0, top_ / 2, top_].map((t) => <g key={t}><line x1={left} x2={W - right} y1={y(t)} y2={y(t)} className="grid" />
            <text x={left - 6} y={y(t) + 4} textAnchor="end" className="axis">+{fmt(t, 1)}</text></g>)}
          <path className="line" stroke={color} d={`M${curve.map((r) => `${x(r.lap)},${y(r.vsBest)}`).join("L")}`} />
          {curve.map((r) => <circle key={r.lap} cx={x(r.lap)} cy={y(r.vsBest)} r={r.lap === current ? 6 : 3} fill={r.lap === current ? "var(--red)" : color}
            onMouseMove={(e) => tt.show(e, `Stop on lap ${r.lap}: +${fmt(r.vsBest, 2)} s against the best lap for this stop`)} onMouseLeave={tt.hide} />)}
          {best && <text x={x(best.lap)} y={y(0) + 18} textAnchor="middle" className="axis">best: lap {best.lap}</text>}
          {lx.filter((l, i) => i === 0 || i === lx.length - 1 || l % 5 === 0).map((l) => <text key={l} x={x(l)} y={H - 20} textAnchor="middle" className="axis">{l}</text>)}
          <text x={(left + W - right) / 2} y={H - 3} textAnchor="middle" className="axis-title">Lap of the stop (red dot: the plan as chosen)</text>
        </svg>
        {tt.node}
      </div>
    </figure>
  );
}

// Expected gap B - A under shifted pit loss (columns) and tyre-wear multipliers (rows).
export function GapHeatmap({ grid, pitDeltas, wearMults, a, b }) {
  const maxAbs = Math.max(...grid.flat().map(Math.abs)) || 1;
  const bg = (v) => {
    const t = Math.min(Math.abs(v) / maxAbs, 1);
    const pole = v < 0 ? "var(--div-neg)" : "var(--div-pos)";
    return `color-mix(in srgb, ${pole} ${Math.round(t * 85)}%, var(--div-mid))`;
  };
  return (
    <div className="table-wrap">
      <table className="heat">
        <caption className="sr-only">Expected gap {b.key} minus {a.key} in seconds</caption>
        <thead>
          <tr><th>Tyre wear ×</th>{pitDeltas.map((d) => <th key={d} className="num">pit loss {d === 0 ? "as fitted" : `${d > 0 ? "+" : ""}${d} s`}</th>)}</tr>
        </thead>
        <tbody>
          {grid.map((row, i) => (
            <tr key={wearMults[i]}>
              <th>{wearMults[i] === 1 ? "as fitted" : `× ${wearMults[i]}`}</th>
              {row.map((v, j) => (
                <td key={j} className={wearMults[i] === 1 && pitDeltas[j] === 0 ? "base" : undefined}
                  style={{ background: bg(v), color: Math.abs(v) / maxAbs > 0.6 ? "#fff" : "var(--text)" }}
                  title={`${b.key} − ${a.key} = ${signed(v, 1)} s`}>{signed(v, 1)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
