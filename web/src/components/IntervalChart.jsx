import { fmt, signed } from "../format.js";
import { useTooltip } from "./Tooltip.jsx";
import { useWidth } from "./useWidth.js";

// Paired differences with 90% and 95% intervals against an equivalence margin.
// rows: [{label, point, lo95, hi95, lo90, hi90, verdict}]
export default function IntervalChart({ rows, margin, unit = "s", note, svgRef }) {
  const tt = useTooltip();
  const [ref, width] = useWidth();
  const narrow = width > 0 && width < 620;
  // narrow screens: labels sit above each interval instead of to the left
  // left margin sized to the longest label so nothing is clipped
  const longest = Math.max(...rows.map((r) => r.label.length));
  const W = narrow ? 420 : 820, left = narrow ? 14 : Math.min(380, 24 + longest * 7.4), right = narrow ? 14 : 24, row = narrow ? 64 : 48, top = 30;
  const H = top + rows.length * row + 30;
  const ext = Math.max(margin * 1.6, ...rows.flatMap((r) => [Math.abs(r.lo95), Math.abs(r.hi95)])) * 1.1;
  const x = (v) => left + ((v + ext) / (2 * ext)) * (W - left - right);
  const ticks = niceTicks(-ext, ext);
  return (
    <figure className="chart">
      <div className="chart-box" ref={ref}>
        <svg ref={svgRef} viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Differences in error between models with intervals">
          <rect x={x(-margin)} y={top - 10} width={x(margin) - x(-margin)} height={H - top - 20} className="band" />
          <text x={x(0)} y={top - 16} textAnchor="middle" className="axis">
            ±{margin} {unit}: too small to matter
          </text>
          {ticks.map((t) => (
            <g key={t}>
              <line x1={x(t)} x2={x(t)} y1={top - 10} y2={H - 30} className={t === 0 ? "zero" : "grid"} />
              <text x={x(t)} y={H - 12} textAnchor="middle" className="axis">{signed(t, decimals(ticks))}</text>
            </g>
          ))}
          {rows.map((r, i) => {
            const y = top + i * row + (narrow ? row - 16 : row / 2);
            return (
              <g key={r.label} onMouseMove={(e) => tt.show(e, (
                <><b>{r.label}</b><br />difference {signed(r.point, 4)} {unit}<br />
                  95% interval [{fmt(r.lo95, 4)}, {fmt(r.hi95, 4)}]<br />90% interval [{fmt(r.lo90, 4)}, {fmt(r.hi90, 4)}]<br />{r.verdict}</>
              ))} onMouseLeave={tt.hide}>
                <rect x={0} y={y - row / 2} width={W} height={row} fill="transparent" />
                {narrow ? (
                  <text x={left} y={y - 14} className="row-label">{r.label}<tspan className="row-sub" dx={8}>{r.verdict}</tspan></text>
                ) : (
                  <>
                    <text x={left - 14} y={y - 3} textAnchor="end" className="row-label">{r.label}</text>
                    <text x={left - 14} y={y + 13} textAnchor="end" className="row-sub">{r.verdict}</text>
                  </>
                )}
                <line x1={x(r.lo95)} x2={x(r.hi95)} y1={y} y2={y} className="ci95" />
                <line x1={x(r.lo90)} x2={x(r.hi90)} y1={y} y2={y} className="ci90" />
                <circle cx={x(r.point)} cy={y} r={5} className="point" />
              </g>
            );
          })}
        </svg>
        {tt.node}
      </div>
      <figcaption>
        Left of zero: the first model in the comparison has the smaller error. Thin line: 95% interval; thick line: 90%
        interval (race-clustered bootstrap). {note}
      </figcaption>
    </figure>
  );
}

function niceTicks(lo, hi) {
  const span = hi - lo, raw = span / 6, mag = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 5, 10].map((m) => m * mag).find((s) => span / s <= 7);
  const out = [];
  for (let t = Math.ceil(lo / step) * step; t <= hi + 1e-12; t += step) out.push(Math.abs(t) < step / 1e6 ? 0 : t);
  return out;
}
const decimals = (t) => Math.max(0, ...t.map((v) => (String(+v.toPrecision(6)).split(".")[1] || "").length));
