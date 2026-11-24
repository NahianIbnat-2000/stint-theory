import { useTooltip } from "./Tooltip.jsx";
import { fmt } from "../format.js";

// A few series over ordered bins, each line labelled at its end.
// bins: [{label, n}], series: [{key, label, color, values: []}]
export default function BinLines({ bins, series, axisLabel, svgRef }) {
  const tt = useTooltip();
  const W = 820, H = 280, left = 56, right = 140, top = 16, bottom = 58;
  const all = series.flatMap((s) => s.values);
  const lo = Math.min(...all) * 0.97, hi = Math.max(...all) * 1.03;
  const x = (i) => left + (i / Math.max(bins.length - 1, 1)) * (W - left - right);
  const y = (v) => top + ((hi - v) / (hi - lo)) * (H - top - bottom);
  const ends = series.map((s, i) => ({ i, y: y(s.values.at(-1)) + 4 })).sort((a, b) => a.y - b.y);
  for (let k = 1; k < ends.length; k++) ends[k].y = Math.max(ends[k].y, ends[k - 1].y + 15);
  const labelY = []; ends.forEach((e) => { labelY[e.i] = e.y; });
  const yt = Array.from({ length: 5 }, (_, i) => lo + ((hi - lo) * i) / 4);
  return (
    <figure className="chart">
      <div className="chart-box">
        <svg ref={svgRef} viewBox={`0 0 ${W} ${H}`} role="img" aria-label={axisLabel}>
          {yt.map((t, i) => <g key={i}><line x1={left} x2={W - right} y1={y(t)} y2={y(t)} className="grid" />
            <text x={left - 8} y={y(t) + 4} textAnchor="end" className="axis">{fmt(t, 2)}</text></g>)}
          {bins.map((b, i) => <g key={b.label}><text x={x(i)} y={H - 38} textAnchor="middle" className="axis">{b.label}</text>
            <text x={x(i)} y={H - 24} textAnchor="middle" className="axis" style={{ fontSize: 10 }}>n={b.n.toLocaleString()}</text></g>)}
          {series.map((s, si) => (
            <g key={s.key}>
              <path className="line" stroke={s.color} d={`M${s.values.map((v, i) => `${x(i)},${y(v)}`).join("L")}`} strokeDasharray={s.dash} />
              {s.values.map((v, i) => <circle key={i} cx={x(i)} cy={y(v)} r={4} fill={s.color} className="ring"
                onMouseMove={(e) => tt.show(e, `${s.label}, ${bins[i].label}: ${fmt(v, 3)} s (${bins[i].n} laps)`)} onMouseLeave={tt.hide} />)}
              <text x={W - right + 8} y={labelY[si]} className="direct-label">{s.label}</text>
            </g>
          ))}
          <text x={left} y={H - 4} className="axis-title">{axisLabel}</text>
        </svg>
        {tt.node}
      </div>
    </figure>
  );
}
