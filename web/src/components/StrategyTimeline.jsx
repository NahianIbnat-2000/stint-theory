import { useState } from "react";
import { lapPlan, Pace } from "../sim/engine.js";
import { compoundInfo, Legend } from "./StintChart.jsx";
import { useTooltip } from "./Tooltip.jsx";
import { fmt } from "../format.js";

// Runs of identical compound/stint from a per-lap list [{lap, comp, stint}]
function runs(laps) {
  const out = [];
  for (const l of laps) {
    const last = out.at(-1);
    if (last && last.comp === l.comp && last.stint === l.stint && last.to === l.lap - 1) last.to = l.lap;
    else out.push({ comp: l.comp, stint: l.stint, from: l.lap, to: l.lap, age0: l.age });
  }
  return out;
}

function actualLaps(d) {
  const out = [];
  d.stints.forEach(([comp, a, b], i) => { for (let l = a; l <= b; l++) out.push({ lap: l, comp, stint: i }); });
  return out;
}

function plannedLaps(st, s, actual) {
  const before = actual.filter((l) => l.lap <= st.decision_lap);
  let stint = (before.at(-1)?.stint ?? 0);
  const after = lapPlan(st, s).map(([lap, comp, age, stop]) => {
    const row = { lap, comp, stint, age };
    if (stop) stint += 1;
    return row;
  });
  return [...before, ...after];
}

// Whole race for one driver: what happened, and plans A and B from the decision lap,
// with the simulator's expected lap time for each plan underneath.
export default function StrategyTimeline({ race, driver, st, plans, svgRef, showPace = true }) {
  const tt = useTooltip();
  const [hoverLap, setHoverLap] = useState(null);
  const d = race.drivers[driver];
  const N = race.total_laps, L = st.decision_lap;
  const actual = actualLaps(d);
  const rowsDef = [{ label: "Actual race", short: "Actual", laps: actual, color: "var(--graphite)" },
    ...plans.map((p) => ({ label: p.label, short: p.key, laps: plannedLaps(st, p, actual), plan: p, color: p.color }))];
  const W = showPace ? 820 : 520, left = showPace ? 92 : 58, right = showPace ? 40 : 14, rowH = 30, top = 22;
  const paceTop = top + rowsDef.length * rowH + 34, paceH = showPace ? 170 : 0;
  const H = showPace ? paceTop + paceH + 34 : top + rowsDef.length * rowH + 30;
  const x = (lap) => left + ((lap - 1) / N) * (W - left - right);
  const ticks = [1, ...Array.from({ length: Math.floor(N / 10) }, (_, i) => (i + 1) * 10).filter((t) => t < N - 3), N];
  const actualComp = new Map(actual.map((l) => [l.lap, l.comp]));

  // expected lap time per plan (no pit loss on the lap itself; stop laps marked)
  const pace = new Pace(race);
  const series = plans.map((p) => ({
    p, pts: lapPlan(st, p).map(([lap, comp, age, stop]) => ({ lap, t: pace.lapMean(st.mu, lap, comp, age), comp, age, stop })),
  }));
  const allT = series.flatMap((s) => s.pts.map((q) => q.t));
  const lo = Math.min(...allT), hi = Math.max(...allT), pad = (hi - lo) * 0.08 || 0.5;
  const y = (t) => paceTop + paceH - ((t - (lo - pad)) / (hi - lo + 2 * pad)) * paceH;
  const yTicks = niceTicks(lo - pad, hi + pad);

  return (
    <figure className="chart">
      <div className="chart-box">
        <svg ref={svgRef} viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`Strategy timeline for ${driver}: actual race and the compared plans, with expected lap times`}
          onMouseLeave={() => setHoverLap(null)}>
          {ticks.map((t) => <g key={t}><line x1={x(t)} x2={x(t)} y1={top - 4} y2={showPace ? paceTop + paceH : H - 20} className="grid" />
            <text x={x(t)} y={H - (showPace ? 18 : 6)} textAnchor="middle" className="axis">{t}</text></g>)}
          {showPace && <text x={(left + W - right) / 2} y={H - 3} textAnchor="middle" className="axis-title">Lap</text>}
          <rect x={left} y={top - 6} width={x(L + 1) - left} height={rowsDef.length * rowH + 4} fill="var(--canvas)" opacity=".65" />
          <line x1={x(L + 1)} x2={x(L + 1)} y1={top - 8} y2={showPace ? paceTop + paceH : H - 20} className="decision" />
          {showPace && <text x={x(L + 1) + 4} y={top - 10} className="axis">decision after lap {L}</text>}
          {rowsDef.map((r, i) => {
            const yy = top + i * rowH;
            return (
              <g key={r.label}>
                <text x={left - 8} y={yy + 19} textAnchor="end" className="row-label">{r.short}</text>
                {i > 0 && <rect x={6} y={yy + 6} width={10} height={14} rx={2} fill={r.color} />}
                {runs(r.laps).map((s, k) => {
                  const c = compoundInfo(s.comp);
                  const x0 = x(s.from) + 1, w = Math.max(x(s.to + 1) - x(s.from) - 2, 1);
                  const changed = i > 0 && s.from > L && Array.from({ length: s.to - s.from + 1 }, (_, j) => s.from + j)
                    .some((lap) => actualComp.get(lap) !== s.comp);
                  const msg = i === 0
                    ? `Actual: ${c.name}, laps ${s.from}–${s.to} (${s.to - s.from + 1} laps)`
                    : s.from > L
                      ? `${r.label}: ${c.name} from lap ${s.from} to ${s.to} (${s.to - s.from + 1} laps)${s.from > L + 1 ? `, after a stop at the end of lap ${s.from - 1}` : ""}.${changed ? " Differs from what happened." : ""}`
                      : `${r.label}: laps already run (same as the actual race)`;
                  return (
                    <g key={k} onMouseMove={(e) => tt.show(e, msg)} onMouseLeave={tt.hide}>
                      <rect className="seg" x={x0} y={yy + 4} width={w} height={rowH - 8} rx={4} fill={c.color} opacity={i > 0 && s.to <= L ? 0.35 : 1} />
                      {changed && <rect x={x0 - 1} y={yy + 3} width={w + 2} height={rowH - 6} rx={5} className="changed" />}
                      {w > 16 && <text x={x0 + w / 2} y={yy + 19} textAnchor="middle" className={`bar-label${s.comp === "MEDIUM" ? " dark" : ""}`}>{c.short}</text>}
                    </g>
                  );
                })}
              </g>
            );
          })}
          {showPace && <>{/* expected pace */}
          <text x={left} y={paceTop - 10} className="axis-title">Expected lap time (s), from the simulator, no safety car</text>
          {yTicks.map((t) => <g key={t}><line x1={left} x2={W - right} y1={y(t)} y2={y(t)} className="grid" />
            <text x={left - 8} y={y(t) + 4} textAnchor="end" className="axis">{t.toFixed(1)}</text></g>)}
          {series.map(({ p, pts }) => (
            <g key={p.key}>
              <path className="line" stroke={p.color} d={`M${pts.map((q) => `${x(q.lap + 0.5)},${y(q.t)}`).join("L")}`} />
              {pts.filter((q) => q.stop).map((q) => <path key={q.lap} d={`M${x(q.lap + 0.5)},${y(q.t) - 9}l-5,-8h10z`} fill={p.color} />)}
              <text x={x(pts.at(-1).lap + 0.5) + 6} y={y(pts.at(-1).t) + 4} className="direct-label" fill={p.color}>{p.key}</text>
            </g>
          ))}
          <rect x={x(L + 1)} y={paceTop} width={W - right - x(L + 1)} height={paceH} className="hit"
            onMouseMove={(e) => {
              const b = e.currentTarget.ownerSVGElement.getBoundingClientRect();
              const lap = Math.round(((e.clientX - b.left) / b.width * W - left) / (W - left - right) * N + 0.5);
              setHoverLap(Math.min(N, Math.max(L + 1, lap)));
            }} />
          {hoverLap && <line x1={x(hoverLap + 0.5)} x2={x(hoverLap + 0.5)} y1={paceTop} y2={paceTop + paceH} className="crosshair" />}</>}
        </svg>
        {hoverLap && (
          <div className="tooltip" style={{ left: `${Math.min(70, (x(hoverLap) / W) * 100)}%`, top: `${(paceTop / H) * 100}%` }}>
            <b>Lap {hoverLap}</b>
            {series.map(({ p, pts }) => {
              const q = pts.find((v) => v.lap === hoverLap);
              return q && <div key={p.key}>{p.key}: {fmt(q.t, 2)} s on {compoundInfo(q.comp).name.toLowerCase()}, age {q.age}{q.stop ? ", pits at the end of this lap" : ""}</div>;
            })}
          </div>
        )}
        {tt.node}
      </div>
      {showPace && <figcaption>
        <Legend /> Shaded laps were already run at the decision. A dashed black outline marks stints that differ from what happened.
        Triangles mark planned stops. The pace lines are expected values; pit-lane time is added once per stop in the totals, not drawn here.
      </figcaption>}
    </figure>
  );
}

function niceTicks(lo, hi) {
  const span = hi - lo, raw = span / 4, mag = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => span / s <= 5);
  const out = [];
  for (let t = Math.ceil(lo / step) * step; t <= hi + 1e-9; t += step) out.push(+t.toFixed(6));
  return out;
}
