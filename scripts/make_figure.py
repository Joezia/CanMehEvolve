#!/usr/bin/env python3
"""Main figure: per-seed results of the DeepSeek greedy vs best-of-N experiment, with medians and full ranges.

Reads only runs/phase1-final/phase1_final.json (itself built from raw run files by scripts/phase1_final.py) and the C1 control
rows in the same file.  Writes report/main_figure.{pdf,png}.
Panels: (A) full runs as executed, (B) post-hoc common budget (first 34 HTTP requests), (C) course token-efficiency metric
for both budget bases.  Every plotted point has 3 independent re-measurements of its fixed patch that passed the frozen rule.
Run:  MPLCONFIGDIR=$HOME/.mplconfig python3 scripts/make_figure.py
"""
import json, statistics as st
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
D = json.load(open(ROOT / "runs/phase1-final/phase1_final.json"))
OUT = ROOT / "report"
OUT.mkdir(parents=True, exist_ok=True)

runs = [r for r in D["runs"] if r["experiment"] == "deepseek"]
cb = D["common_budget_34"]
ctl = {c["control"]: c for c in D["controls"]}
O3 = ctl["C1 -O3 vs -O2 (batch 1071478)"]["median_speedup"]
O3N = ctl["C1 -O3 -march=native vs -O2 (rerun 1071478)"]["median_speedup"]

COL = {"greedy": "#0072B2", "bestofn": "#D55E00"}      # blue / vermillion (Okabe-Ito), also told apart by marker and label
MK = {"greedy": "o", "bestofn": "s"}
NAME = {"greedy": "greedy", "bestofn": "best-of-N"}
INK, MUTED, GRID = "#222222", "#666666", "#e3e3e3"
plt.rcParams.update({"font.size": 8.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
                     "axes.spines.top": False, "axes.spines.right": False, "font.family": "DejaVu Sans"})


def series(rows, key, arm):
    return sorted(((r["seed"], r[key], r)) for r in rows if r["arm"] == arm)


def draw(ax, rows, key, x0, arm, filled=True, annotate=None, scale=1.0):
    pts = series(rows, key, arm)
    vals = [v * scale for _, v, _ in pts]
    med = st.median(vals)
    ax.plot([x0, x0], [min(vals), max(vals)], color=COL[arm], lw=1.0, zorder=1)
    ax.plot([x0 - 0.30, x0 + 0.30], [med, med], color=COL[arm], lw=2.2, zorder=2, solid_capstyle="butt")
    for seed, v, r in pts:
        dx = (seed - 3) * 0.12                      # same horizontal slot per seed in every group: left -> right = s1..s5
        ax.scatter([x0 + dx], [v * scale], s=26, marker=MK[arm], facecolor=COL[arm] if filled else "white",
                   edgecolor=COL[arm], linewidths=1.1, zorder=3)
        if annotate and annotate(r):
            ax.annotate(annotate(r), (x0 + dx, v * scale), xytext=(0, 5), textcoords="offset points",
                        ha="center", va="bottom", fontsize=6.2, color=INK)
    return med


fig, axes = plt.subplots(1, 3, figsize=(6.7, 2.75), gridspec_kw={"width_ratios": [1, 1, 1.3], "wspace": 0.32})
a, b, c = axes

# (A) full runs
for ax, rows, title in ((a, runs, "A. Full runs"), (b, cb, "B. First 34 requests")):
    ax.set_title(title, loc="left", fontsize=9, fontweight="bold", color=INK)
    ax.grid(axis="y", color=GRID, lw=0.6, zorder=0)
    ax.axhline(1.0, color=MUTED, lw=0.8, zorder=1)
    ax.axhline(O3, color=MUTED, lw=0.8, ls="--", zorder=1)
    ax.axhline(O3N, color=MUTED, lw=0.8, ls=":", zorder=1)
    ax.set_xlim(-0.65, 1.75)
    ax.set_xticks([0, 1])
    ax.set_xticklabels([NAME["greedy"], NAME["bestofn"]])
    ax.set_ylim(0.99, 1.24)
ann = lambda r: ("%d req." % r["http_attempts"]) if r["http_attempts"] < 40 else ""
draw(a, runs, "best_confirmed_speedup", 0, "greedy")
draw(a, runs, "best_confirmed_speedup", 1, "bestofn")
draw(b, cb, "best_confirmed_speedup", 0, "greedy")
draw(b, cb, "best_confirmed_speedup", 1, "bestofn")
a.set_ylabel("speedup (stock = 1)")
b.set_yticklabels([])
a.text(1.72, 1.0015, "stock", ha="right", va="bottom", fontsize=7, color=MUTED)
a.text(1.72, O3 + 0.0015, "-O3", ha="right", va="bottom", fontsize=7, color=MUTED)
a.text(1.72, O3N + 0.0015, "-O3 native", ha="right", va="bottom", fontsize=7, color=MUTED)

# (C) course metric, both bases
c.set_title("C. (speedup − 1) / token", loc="left", fontsize=9, fontweight="bold", color=INK)
c.grid(axis="y", color=GRID, lw=0.6, zorder=0)
scale = 1e7
m = {}
m["gf"] = draw(c, runs, "course_metric", 0, "greedy", True, scale=scale)
m["bf"] = draw(c, runs, "course_metric", 1, "bestofn", True, scale=scale)
m["g34"] = draw(c, cb, "course_metric_budget", 2.6, "greedy", False, scale=scale)
m["b34"] = draw(c, cb, "course_metric_budget", 3.6, "bestofn", False, scale=scale)
c.set_xlim(-0.65, 4.25)
c.set_xticks([0, 1, 2.6, 3.6])
c.set_xticklabels(["greedy\nfull", "best-\nof-N\nfull", "greedy\n34 req.", "best-\nof-N\n34 req."], fontsize=7.5)
c.set_ylim(0, 5.6)
c.set_ylabel(r"$10^{-7}$ per token")
c.axvline(1.8, color=GRID, lw=0.8)

fig.subplots_adjust(left=0.085, right=0.995, top=0.9, bottom=0.17)
for ext in ("pdf", "png"):
    fig.savefig(OUT / ("main_figure." + ext), dpi=300)
print("medians:", {k: round(v, 4) for k, v in m.items()})
