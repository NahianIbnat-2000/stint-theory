import { useState } from "react";
import { COMPOUND } from "../data.js";
import { fmt, signed } from "../format.js";

// Lap time at each tyre age relative to age 5, by compound, with 95% bands.
export default function TyreCurves({ curve, svgRef, visible = null }) {
  const [hover, setHover] = useState(null);
  const W = 760, H = 430, left = 56, right = 80, top = 16, bottom = 110;
  const ages = [...new Set(curve.map((r) => r.tyre_age))].sort((a, b) => a - b);
  const lo = Math.min(...curve.map((r) => r.ci_low)), hi = Math.max(...curve.map((r) => r.ci_high));
  const x = (a) => left + ((a - ages[0]) / (ages.at(-1) - ages[0])) * (W - left - right);
  const y = (v) => top + ((hi - v) / (hi - lo)) * (H - top - bottom);
  const yt = ticks(lo, hi);
  const series = Object.keys(COMPOUND).map((c) => ({ c, rows: curve.filter((r) => r.compound === c).sort((a, b) => a.tyre_age - b.tyre_age) }))
    .filter((s) => s.rows.length && (!visible || visible.includes(s.c)));
  // end labels: keep at least 15 px apart so they never overlap
  const labelY = (() => {
    const ys = series.map((s, i) => ({ i, y: y(s.rows.at(-1).effect_s) + 4 })).sort((a, b) => a.y - b.y);
    for (let k = 1; k < ys.length; k++) ys[k].y = Math.max(ys[k].y, ys[k - 1].y + 15);
    const out = []; ys.forEach((v) => { out[v.i] = v.y; }); return out;
  })();
  const move = (e) => {
    const r = e.currentTarget.getBoundingClientRect();
    const px = ((e.clientX - r.left) / r.width) * W;
    const a = ages.reduce((best, v) => (Math.abs(x(v) - px) < Math.abs(x(best) - px) ? v : best), ages[0]);
    setHover(a);
  };
  return (
    <figure className="chart">
      <div className="chart-box">
        <svg ref={svgRef} viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Lap time by tyre age and compound" onMouseMove={move} onMouseLeave={() => setHover(null)}>
          {yt.map((t) => (
            <g key={t}>
              <line x1={left} x2={W - right} y1={y(t)} y2={y(t)} className={t === 0 ? "zero" : "grid"} />
              <text x={left - 8} y={y(t) + 4} textAnchor="end" className="axis">{signed(t, 1)}</text>
            </g>
          ))}
          {ages.filter((a) => a % 5 === 0 || a === 1).map((a) => (
            <text key={a} x={x(a)} y={H - 88} textAnchor="middle" className="axis">{a}</text>
          ))}
          {/* sample size: laps behind each point, per compound (small multiples of bars) */}
          {(() => {
            const maxN = Math.max(...series.flatMap((s) => s.rows.map((r) => r.laps)), 1);
            const bh = 52 / Math.max(series.length, 1);
            return series.map(({ c, rows }, si) => (
              <g key={c}>
                {rows.map((r) => <rect key={r.tyre_age} x={x(r.tyre_age) - (x(2) - x(1)) / 2 + 1} width={Math.max(x(2) - x(1) - 2, 2)} rx={1}
                  y={H - 70 + si * bh + (bh - 2) * (1 - r.laps / maxN)} height={Math.max((bh - 2) * (r.laps / maxN), 0.5)}
                  fill={COMPOUND[c].color} opacity=".75" />)}
                <text x={W - right + 8} y={H - 70 + si * bh + bh / 2 + 3} className="axis" style={{ fontSize: 10 }}>{COMPOUND[c].short} laps</text>
              </g>
            ));
          })()}
          <text x={(left + W - right) / 2} y={H - 2} textAnchor="middle" className="axis-title">Tyre age (laps); ages above {ages.at(-1)} pooled. Bars: number of laps behind each point</text>
          <text x={left - 44} y={top + 2} className="axis">s</text>
          {series.map(({ c, rows }, si) => (
            <g key={c}>
              <path className="ci-band" fill={COMPOUND[c].color}
                d={`M${rows.map((r) => `${x(r.tyre_age)},${y(r.ci_high)}`).join("L")}L${[...rows].reverse().map((r) => `${x(r.tyre_age)},${y(r.ci_low)}`).join("L")}Z`} />
              <path className="line" stroke={COMPOUND[c].color} d={`M${rows.map((r) => `${x(r.tyre_age)},${y(r.effect_s)}`).join("L")}`} />
              <text x={x(rows.at(-1).tyre_age) + 8} y={labelY[si]} className="direct-label">{COMPOUND[c].name}</text>
            </g>
          ))}
          {hover !== null && (
            <g>
              <line x1={x(hover)} x2={x(hover)} y1={top} y2={H - bottom} className="crosshair" />
              {series.map(({ c, rows }) => {
                const r = rows.find((v) => v.tyre_age === hover);
                return r ? <circle key={c} cx={x(hover)} cy={y(r.effect_s)} r={4.5} fill={COMPOUND[c].color} className="ring" /> : null;
              })}
            </g>
          )}
        </svg>
        {hover !== null && (
          <div className="tooltip" style={{ left: `${(x(hover) / W) * 100}%`, top: 8 }}>
            <b>Tyre age {hover}</b>
            {series.map(({ c, rows }) => {
              const r = rows.find((v) => v.tyre_age === hover);
              return r && <div key={c}>{COMPOUND[c].name}: {signed(r.effect_s, 3)} s [{fmt(r.ci_low, 2)}, {fmt(r.ci_high, 2)}], {r.laps} laps</div>;
            })}
          </div>
        )}
      </div>
      <figcaption>Lap time compared with the same compound at tyre age 5, after removing fuel and track (race-lap effects), the driver’s pace in that race and the compound’s pace at that race. Shaded: 95% interval.</figcaption>
    </figure>
  );
}

function ticks(lo, hi) {
  const span = hi - lo, raw = span / 5, mag = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => span / s <= 6);
  const out = [];
  for (let t = Math.ceil(lo / step) * step; t <= hi + 1e-12; t += step) out.push(Math.abs(t) < 1e-9 ? 0 : +t.toFixed(6));
  return out;
}
