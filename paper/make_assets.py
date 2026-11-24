"""Build every figure and table of the report from the exported result files.

    python paper/make_assets.py        (after python -m webexport and node paper/monza.mjs)

Nothing here is typed by hand: each number is read from web/public/data or from
paper/data/monza.json. Figures are vector PDFs; tables are LaTeX (booktabs).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "web" / "public" / "data"
OUT = Path(__file__).resolve().parent
FIG, TAB = OUT / "figures", OUT / "tables"
FIG.mkdir(exist_ok=True)
TAB.mkdir(exist_ok=True)

serif = "Times New Roman" if any("Times New Roman" in f.name for f in font_manager.fontManager.ttflist) else "Liberation Serif"
plt.rcParams.update({"font.family": serif, "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": "#e6e6e0", "grid.linewidth": .6, "axes.axisbelow": True,
                     "pdf.fonttype": 42, "savefig.bbox": "tight"})
C = {"SOFT": "#d33a2c", "MEDIUM": "#c99700", "HARD": "#2f7fc8", "a": "#b5612a", "b": "#1f82a8", "ink": "#0d0d0d", "grey": "#6b6b66"}
NAME = {"persistence": "Persistence", "compound_drift": "Compound drift", "ridge": "Ridge regression",
        "mixed_effects": "Mixed-effects model", "random_forest": "Random forest", "xgboost": "XGBoost",
        "xgboost_ens5": "XGBoost (5 seeds)", "mlp": "MLP", "lstm": "LSTM", "tcn": "TCN",
        "xgboost_direct": "XGBoost (direct)", "lstm_multi": "LSTM", "mlp_multi": "MLP",
        "trend_extrapolation": "Trend extrapolation"}
FAMILY = {"persistence": "Benchmark", "compound_drift": "Benchmark", "ridge": "Statistical", "mixed_effects": "Statistical",
          "random_forest": "Tree ensemble", "xgboost": "Tree ensemble", "xgboost_ens5": "Tree ensemble",
          "mlp": "Neural network", "lstm": "Neural network", "tcn": "Neural network"}


def load(name):
    return json.loads((DATA / "results" / name).read_text())


def md_table(text: str, heading: str) -> list[dict]:
    """First Markdown table after a heading in a generated report."""
    lines, started = [], False
    for l in text[text.index(heading):].splitlines()[1:]:
        if l.startswith("|"):
            lines.append(l); started = True
        elif started:
            break
    head = [h.strip() for h in lines[0].strip("|").split("|")]
    rows = [dict(zip(head, [c.strip() for c in l.strip("|").split("|")])) for l in lines[2:]]
    return rows


def write(name, s):
    (TAB / name).write_text(s)


def f(x, d=3):
    return f"{x:.{d}f}".replace("-", "$-$")


def comp(s):
    return " vs ".join(NAME.get(p, p) for p in s.split(" vs "))


# ------------------------------------------------------------------ data
cov = load("coverage.json")
seasons = cov["by_season"]
nn = {str(r["season"]): r for r in cov["field_non_null_share"]}
rows = []
for s, v in seasons.items():
    rows.append(f"{s} & {v['races_listed']} & {v['races_in_sample']} & {v['driver_laps']:,} & {v['clean_green_laps']:,} & "
                f"{100 * v['clean_green_share']:.1f} & {100 * nn[s]['lap_time_s']:.1f} \\\\")
tot = {k: sum(v[k] for v in seasons.values()) for k in ("races_listed", "races_in_sample", "driver_laps", "clean_green_laps")}
rows.append(r"\midrule" + f"\nTotal & {tot['races_listed']} & {tot['races_in_sample']} & {tot['driver_laps']:,} & {tot['clean_green_laps']:,} & "
            f"{100 * tot['clean_green_laps'] / tot['driver_laps']:.1f} & \\\\")
write("t_data.tex", "\n".join(rows))

# ------------------------------------------------------------------ Task 1
ft = load("final_test.json")
meta = load("final_test_meta.json")
rep1 = (DATA / "reports" / "final_test.md").read_text()
compute = {r["model"]: float(r["fit_s"]) for r in md_table(rep1, "## S6. Compute")}
rows = []
for r in sorted(ft["summary"], key=lambda r: r["mae"]):
    m = r["model"]
    rows.append(f"{NAME[m]} & {FAMILY[m]} & {f(r['mae'])} & [{f(r['mae_ci_low'])}, {f(r['mae_ci_high'])}] & {f(r['rmse'])} & "
                f"{f(r['bias'])} & {f(100 * r['skill_vs_persistence'], 1)} & {(f'{compute[m]:,.0f}' if compute[m] >= 1 else '$<$1')} \\\\")
write("t_task1.tex", "\n".join(rows))
rows = []
for r in ft["primary"]:
    rows.append(f"{r['#']} & {comp(r['comparison'])} & {f(r['MAE diff (s)'], 4)} & [{f(r['90% low'], 4)}, {f(r['90% high'], 4)}] & "
                f"[{f(r['95% low'], 4)}, {f(r['95% high'], 4)}] & {r['Holm p']:.2f} & {r['label']} \\\\")
write("t_primary1.tex", "\n".join(rows))

fig, ax = plt.subplots(figsize=(6.3, 2.7))
pr = ft["primary"][::-1]
for i, r in enumerate(pr):
    ax.plot([r["95% low"], r["95% high"]], [i, i], color=C["ink"], lw=1.2)
    ax.plot([r["90% low"], r["90% high"]], [i, i], color=C["ink"], lw=4.5, solid_capstyle="round")
    ax.plot(r["MAE diff (s)"], i, "o", ms=6, mfc="white", mec=C["ink"], mew=1.5)
ax.axvspan(-0.01, 0.01, color="#fff3b8", zorder=0, label="Equivalence margin ($\\pm$0.01 s)")
ax.axvline(0, color=C["grey"], lw=.8)
ax.set_yticks(range(len(pr)), [f"{r['#']}  {comp(r['comparison'])}" for r in pr])
ax.set_xlabel("Difference in mean absolute error (s per lap); negative favours the first model")
ax.set_xlim(-0.014, 0.014)
ax.legend(loc="lower right", frameon=False, fontsize=8.5)
fig.savefig(FIG / "f_primary1.pdf")
plt.close(fig)

te = load("test_errors.json")
bins = te["by_tyre_age"]
fig, ax = plt.subplots(figsize=(6.3, 2.8))
xs = range(len(bins))
for m, col, ls in [("persistence", C["grey"], "--"), ("ridge", "#8c8c84", ":"), ("xgboost_ens5", C["a"], "-"), ("lstm", C["b"], "-"), ("tcn", "#5d5aa8", "-.")]:
    ax.plot(xs, [b["mae"][m] for b in bins], ls, color=col, marker="o", ms=3.5, lw=1.6, label=NAME[m])
ax.set_xticks(list(xs), [f"{b['lo'] + 1}–{b['hi']}\n(n={b['n']:,})" for b in bins])
ax.set_xlabel("Tyre age of the predicted lap (laps)")
ax.set_ylabel("Mean absolute error (s)")
ax.legend(frameon=False, fontsize=8.5, ncol=2)
fig.savefig(FIG / "f_tyreage_error.pdf")
plt.close(fig)

# ------------------------------------------------------------------ Task 2
t2 = load("task2_test_meta.json")
rep2 = (DATA / "reports" / "task2_test.md").read_text()
allm = md_table(rep2, "## 10-lap total, all models")
rows = [f"{NAME[r['model']]} & {float(r['MAE of 10-lap total (s)']):.3f} & {f(float(r['bias (s)']))} \\\\" for r in allm]
write("t_task2_models.tex", "\n".join(rows))
rows = []
for r in t2["primary"]:
    rows.append(f"{r['#']} & {comp(r['comparison'])} & {f(r['10-lap MAE diff (s)'], 3)} & [{f(r['90% low'], 3)}, {f(r['90% high'], 3)}] & "
                f"[{f(r['95% low'], 3)}, {f(r['95% high'], 3)}] & {r['Holm p']:.3f} & {r['label']} \\\\")
write("t_primary2.tex", "\n".join(rows))
hz = md_table(rep2, "## Secondary: by horizon")
fig, ax = plt.subplots(figsize=(6.3, 2.8))
h = [int(r["h"]) for r in hz]
for m, col, ls in [("persistence", C["grey"], "--"), ("mlp_multi", "#5d5aa8", "-."), ("lstm_multi", C["b"], "-"), ("xgboost_direct", C["a"], "-")]:
    ax.plot(h, [float(r[m]) for r in hz], ls, color=col, marker="o", ms=3.5, lw=1.6, label=NAME[m])
ax.set_xticks(h)
ax.set_xlabel("Forecast horizon (laps ahead)")
ax.set_ylabel("Mean absolute error (s)")
ax.legend(frameon=False, fontsize=8.5)
fig.savefig(FIG / "f_horizon.pdf")
plt.close(fig)

# ------------------------------------------------------------------ Task 3
t3 = load("task3.json")
rob = t3["robustness"]
order = [("main", "Main: race-lap, driver-race, race-compound FE"), ("naive", "Naive: no race-lap FE"),
         ("R1", "R1: first two laps of each stint dropped"), ("R2", "R2: tyre age $\\leq$ 15 laps"),
         ("R4", "R4: pace outliers removed"), ("R6", "R6: plus race $\\times$ stint-number FE"),
         ("R5: season 2023", "R5: season 2023"), ("R5: season 2024", "R5: season 2024"), ("R5: season 2025", "R5: season 2025")]
rows = []
for key, label in order:
    cells = []
    for c in ("SOFT", "MEDIUM", "HARD"):
        r = next(v for v in rob if v["specification"].startswith(key) and v["compound"] == c)
        cells.append(f"{f(r['s_per_lap'], 3)} [{f(r['ci_low'], 3)}, {f(r['ci_high'], 3)}]")
    rows.append(f"{label} & " + " & ".join(cells) + " \\\\")
    if key == "naive":
        rows.append(r"\midrule")
write("t_task3.tex", "\n".join(rows))
curve = load("tyre_curves.json")
fig, ax = plt.subplots(figsize=(6.3, 3.0))
for c in ("SOFT", "MEDIUM", "HARD"):
    rs = sorted([r for r in curve if r["compound"] == c], key=lambda r: r["tyre_age"])
    a = [r["tyre_age"] for r in rs]
    ax.fill_between(a, [r["ci_low"] for r in rs], [r["ci_high"] for r in rs], color=C[c], alpha=.15, lw=0)
    ax.plot(a, [r["effect_s"] for r in rs], color=C[c], lw=1.8, label=c.title())
ax.axhline(0, color=C["grey"], lw=.8)
ax.set_xlabel("Tyre age (laps); ages above 35 pooled")
ax.set_ylabel("Lap time against age 5 (s)")
ax.legend(frameon=False)
fig.savefig(FIG / "f_tyre_curves.pdf")
plt.close(fig)

# ------------------------------------------------------------------ simulator
bt = load("sim_backtest.json")
ns, rem, pit, cal = bt["next_stint"], bt["remaining"], bt["pit_loss"], bt["calibration"]
rows = [
    f"Next-stint lap time (s per lap) & {ns['laps']:,} laps, {ns['stops']:,} stops & {f(ns['model_mae'])} & {f(ns['model_bias'])} & {f(ns['persistence_mae'])} & {f(ns['persistence_bias'])} \\\\",
    f"Remaining race time (s) & {rem['drivers']} drivers, {rem['races']} races & {f(rem['mae_s'], 1)} & {f(rem['bias_s'], 1)} & -- & -- \\\\",
    f"Pit loss per green-flag stop (s) & {pit['stops']:,} stops & {f(pit['mae_s'], 2)} & {f(pit['bias_s'], 2)} & -- & -- \\\\",
]
write("t_backtest.tex", "\n".join(rows))
fig, ax = plt.subplots(figsize=(6.3, 2.6))
bb = ns["by_laps_after_stop"]
labels = [re.sub(r"\((\d+), (\d+)\]", lambda m: f"{int(m.group(1)) + 1}–{m.group(2)}", b["bin"]) for b in bb]
x = range(len(bb))
ax.bar([i - .2 for i in x], [b["model_bias"] for b in bb], .38, color=C["a"], label="Simulator")
ax.bar([i + .2 for i in x], [b["persistence_bias"] for b in bb], .38, color=C["grey"], label="Persistence")
ax.axhline(0, color=C["ink"], lw=.8)
ax.set_xticks(list(x), labels)
ax.set_xlabel("Laps since the pit stop")
ax.set_ylabel("Bias (s per lap; positive = too slow)")
ax.legend(frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, 1.14))
fig.savefig(FIG / "f_nextstint_bias.pdf")
plt.close(fig)

# ------------------------------------------------------------------ Monza
mz = json.loads((OUT / "data" / "monza.json").read_text())
fig, ax = plt.subplots(figsize=(6.3, 2.5))
drivers = ["LEC", "PIA", "NOR", "SAI", "HAM", "RUS", "VER"]
for i, d in enumerate(drivers[::-1]):
    for comp_, a, b in mz["stints"][d]:
        ax.barh(i, b - a + 1, left=a - .5, height=.62, color=C.get(comp_, "#6f8f7c"), edgecolor="white", lw=1.2)
        ax.text((a + b) / 2, i, comp_[0], ha="center", va="center", fontsize=7.5, color="white" if comp_ != "MEDIUM" else C["ink"], fontweight="bold")
ax.axvline(mz["lap"] + .5, color=C["ink"], ls="--", lw=1)
ax.text(mz["lap"] + 1, len(drivers) - .4, f"decision after lap {mz['lap']}", fontsize=8)
ax.set_yticks(range(len(drivers)), drivers[::-1])
ax.set_xlim(.5, mz["total_laps"] + .5)
ax.set_xlabel("Lap")
ax.grid(axis="y", visible=False)
fig.savefig(FIG / "f_monza_stints.pdf")
plt.close(fig)
fig, ax = plt.subplots(figsize=(6.3, 2.7))
for d, col, lab in [("PIA", C["b"], "Piastri"), ("LEC", C["a"], "Leclerc")]:
    ax.plot(mz[d]["wear"], mz[d]["one_minus_two"], color=col, marker="o", ms=3.5, lw=1.6, label=lab)
ax.axhline(0, color=C["grey"], lw=.8)
ax.axvline(mz["PIA"]["break_even"], color=C["ink"], ls="--", lw=1)
ax.text(mz["PIA"]["break_even"] + .05, max(mz["PIA"]["one_minus_two"]) * .85, f"break-even about ×{mz['PIA']['break_even']:.1f}", fontsize=8.5)
ax.set_xlabel("Multiplier on the model's tyre-age effect at Monza")
ax.set_ylabel("One stop minus two stops (s)")
ax.legend(frameon=False)
fig.savefig(FIG / "f_monza_sensitivity.pdf")
plt.close(fig)
FULLC = {"S": "soft", "M": "medium", "H": "hard"}


def plan_text(desc):
    """'H-S (stops: 35)' -> 'stop on lap 35 for soft'; 'H (stops: no further stops)' -> 'no further stop'."""
    seq, stops = desc.split(" (stops: ")
    stops = stops.rstrip(")")
    if stops.startswith("no further"):
        return "no further stop"
    new = seq.split("-")[1:]
    return "; ".join(f"stop on lap {l} for {FULLC[c]}" for l, c in zip(stops.split(", "), new))


rows = []
for d, nm in [("PIA", "Piastri"), ("LEC", "Leclerc")]:
    r = mz[d]
    rows.append(f"{nm} & {plan_text(r['observed'])} & {plan_text(r['alternative'])} & "
                f"{f(r['mean'], 1)} & [{f(r['p05'], 1)}, {f(r['p95'], 1)}] & {100 * r['pAltFaster']:.1f} & {r['break_even']:.1f} \\\\")
write("t_monza.tex", "\n".join(rows))

print("serif font:", serif)
print("figures:", sorted(p.name for p in FIG.glob("*.pdf")))
print("tables:", sorted(p.name for p in TAB.glob("*.tex")))

# ------------------------------------------------------------------ stops per full-distance finisher (dry races)
import collections  # noqa: E402
cnt, n_races = collections.Counter(), 0
for fp in (DATA / "sim" / "races").glob("*.json"):
    p = json.loads(fp.read_text())
    if not p["simulatable"]:
        continue
    n_races += 1
    for v in p["drivers"].values():
        if v.get("status") == "classified" and v["finished"]:
            cnt[len([l for l, _ in v["stops"] if l < p["total_laps"]])] += 1
tot = sum(cnt.values())
(OUT / "data" / "stop_counts.json").write_text(json.dumps(
    {"dry_races": n_races, "finishers": tot, "share_by_stops": {k: cnt[k] / tot for k in sorted(cnt)}}, indent=1))
print("stops:", n_races, tot, {k: round(100 * cnt[k] / tot, 1) for k in sorted(cnt)})
