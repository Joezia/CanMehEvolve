#!/usr/bin/env python3
"""Builds the 3-slide static PDF (16:9) plus PNG previews and a thumbnail overview. Data: presentation_slides/data/*.csv (copied from presentation_materials/tables).
usage: python3 presentation_slides/make_slides.py   (needs matplotlib, numpy)"""
import csv, os, statistics as st
from pathlib import Path
os.environ.setdefault("MPLCONFIGDIR", str(Path.home() / ".mplconfig"))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch
import numpy as np

HERE = Path(__file__).resolve().parent; DATA = HERE / "data"; OUT = HERE
W, H = 13.333, 7.5
INK, INK2, MUTED, GRID, LINE = "#14171a", "#46505a", "#7a838c", "#e3e6ea", "#c9ced4"
BLUE, AQUA, RED, AMBER, GREY = "#2a78d6", "#1baf7a", "#d03b3b", "#f0a500", "#9aa1a9"
plt.rcParams.update({"font.family": "Liberation Sans", "pdf.fonttype": 42, "ps.fonttype": 42, "text.color": INK})
FOOT = "Zhou Ziang (A0359536N)  |  NUS CS6219  |  CanMehEvolve"

def new_slide():
    fig = plt.figure(figsize=(W, H), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off")
    return fig, ax

def T(ax, x, y, s, size=22, weight="normal", color=INK, ha="left", va="top", **kw):
    return ax.text(x, y, s, fontsize=size, fontweight=weight, color=color, ha=ha, va=va, **kw)

def box(ax, x, y, w, h, fc="white", ec=LINE, lw=1.6, r=0.12):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw))

def footer(ax, n, note=None):
    ax.plot([0.5, W - 0.5], [7.12, 7.12], color=GRID, lw=1)
    T(ax, 0.5, 7.4, FOOT, size=11, color=MUTED, va="bottom"); T(ax, W - 0.5, 7.4, f"{n} / 3", size=11, color=MUTED, ha="right", va="bottom")

def title(ax, s):
    T(ax, 0.5, 0.28, s, size=37, weight="bold", family="Liberation Sans Narrow")

# ---------------------------------------------------------------------------------------------------------------- slide 1
def slide1():
    fig, ax = new_slide(); title(ax, "How do we decide whether a patch is faster?")
    T(ax, 0.5, 1.08, "Rule for one full measurement vs stock", size=20, color=INK2)
    steps = [("1", "Measure", "10 processes, 9 repetitions each"), ("2", "Per process", "median candidate time / median stock time"),
             ("3", "Test", "exact sign-flip test on the 10 ratios"), ("4", "Judge", "faster only if all three hold")]
    x0, y0, bw, bh, gap = 0.5, 1.7, 6.9, 0.88, 0.26
    for i, (n, a_, b_) in enumerate(steps):
        y = y0 + i * (bh + gap); h = bh if i < 3 else 1.5
        box(ax, x0, y, bw, h, fc="#f4f7fb" if i < 3 else "#eaf2fc", ec=BLUE if i == 3 else LINE, lw=2.2 if i == 3 else 1.6)
        ax.add_patch(plt.Circle((x0 + 0.5, y + 0.44), 0.27, fc=BLUE, ec="none")); T(ax, x0 + 0.5, y + 0.45, n, size=20, weight="bold", color="white", ha="center", va="center")
        T(ax, x0 + 1.0, y + 0.1, a_, size=22, weight="bold", color=BLUE)
        T(ax, x0 + 1.0, y + 0.45, b_, size=21)
        if i < 3: ax.add_patch(FancyArrowPatch((x0 + 0.5, y + h + 0.02), (x0 + 0.5, y + h + gap - 0.02), arrowstyle="-|>", mutation_scale=20, color=MUTED, lw=2))
    yy = y0 + 3 * (bh + gap) + 0.88
    for k, (lab, w_) in enumerate([("direction: faster", 2.1), ("p < 0.01", 1.4), ("reduction \u2265 2%", 2.0)]):
        xx = x0 + 1.0 + sum([2.1, 1.4, 2.0][:k]) + 0.15 * k
        box(ax, xx, yy, w_, 0.42, fc="white", ec=BLUE, lw=1.8, r=0.08); T(ax, xx + w_ / 2, yy + 0.22, lab, size=19, weight="bold", ha="center", va="center")
    cx, cw = 7.9, 4.95
    T(ax, cx, 1.08, "Checked against known cases", size=20, color=INK2)
    cards = [("99/100", "Known true time reduction\n\u2248 4.8%: judged faster", BLUE), ("0/500", "Synthetic null, no change:\nfalse accepts, 95% CP\nupper bound 0.735%", AQUA),
             ("0/804", "Real SDK, no substantive\nchange: false accepts,\n95% CP upper bound 0.458%", AQUA)]
    for i, (big, small, col) in enumerate(cards):
        y = 1.7 + i * 1.32
        box(ax, cx, y, cw, 1.2, fc="white", ec=col, lw=2.2)
        T(ax, cx + 0.15, y + 0.6, big, size=34, weight="bold", color=col, va="center")
        T(ax, cx + 2.0, y + 0.6, small, size=15, va="center", color=INK, linespacing=1.25)
    T(ax, cx, 5.62, "Per single full measurement, in the conditions\ntested; not the false-positive rate of a whole\nsearch. 0 observed does not mean a true\nrate of zero.", size=15.5, color=INK2, linespacing=1.3)
    T(ax, 0.5, 6.78, "Garmin FIT SDK 21.201.0   |   full decode of 4 FIT files   |   stock and candidates built with -O2", size=13, color=MUTED)
    footer(ax, 1); return fig

# ---------------------------------------------------------------------------------------------------------------- slide 2
def chips(fig, ax, y, labels, size=16, h=0.46, x0=0.5, xmax=W - 0.5, gap=0.42, pad=0.28):
    r = fig.canvas.get_renderer(); inv = ax.transData.inverted(); ws = []
    for l in labels:
        t = ax.text(0, 0, l, fontsize=size, fontweight="bold"); bb = t.get_window_extent(r); t.remove()
        ws.append(abs(inv.transform((bb.x1, 0))[0] - inv.transform((bb.x0, 0))[0]) + 2 * pad)
    tot = sum(ws) + gap * (len(labels) - 1); sc = min(1.0, (xmax - x0) / tot); x = x0
    for i, (l, w_) in enumerate(zip(labels, ws)):
        w_ *= sc; box(ax, x, y, w_, h, fc="#eaf2fc", ec=BLUE, lw=1.6, r=0.08); T(ax, x + w_ / 2, y + h / 2 + 0.01, l, size=size, weight="bold", ha="center", va="center")
        if i < len(labels) - 1: ax.add_patch(FancyArrowPatch((x + w_ + 0.04, y + h / 2), (x + w_ + gap * sc - 0.04, y + h / 2), arrowstyle="-|>", mutation_scale=16, color=MUTED, lw=1.8))
        x += w_ + gap * sc

def slide2():
    rows = list(csv.DictReader(open(DATA / "i3_runs.csv")))
    ctl = list(csv.DictReader(open(DATA / "controls_summary.csv")))
    o3 = [r for r in ctl if r["comparison"].startswith("-O3 vs stock")]; nat = [r for r in ctl if r["comparison"].startswith("-O3 -march=native vs stock") and r["valid_comparison"] == "True"][0]
    h1 = [r for r in ctl if "attempt 1" in r["comparison"]][0]; h2 = [r for r in ctl if "attempt 2" in r["comparison"]][0]
    o3v = st.median([float(r["median_speedup"]) for r in o3])
    fig, ax = new_slide(); title(ax, "Does search beat independent sampling\u2014and at what cost?")
    T(ax, 0.5, 1.02, "Population (6): pick parent + function  \u2192  LLM rewrite  \u2192  compile + checks  \u2192  timing  \u2192  keep, feed back failures", size=17, color=INK2)
    T(ax, 0.5, 1.5, "C3  matched best-of-N, 40 requests/run      C4  5 seeds/configuration      dot = median of 3 re-measurements", size=16, color=INK2)
    cols = {"Population search": BLUE, "Best-of-N": AQUA}
    med = {}
    AX0, AX1 = 2.35, 4.5
    for model, px in [("Qwen", 0.5), ("DeepSeek", 6.85)]:
        a = fig.add_axes([(px + 0.95) / W, 1 - AX1 / H, 4.6 / W, (AX1 - AX0) / H]); a.set_facecolor("white")
        a.set_xlim(-0.6, 1.6); a.set_ylim(1.0, 1.24)
        for sp in ("top", "right"): a.spines[sp].set_visible(False)
        for sp in ("left", "bottom"): a.spines[sp].set_color(LINE)
        a.yaxis.grid(True, color=GRID, lw=1); a.set_axisbelow(True)
        a.set_yticks([1.00, 1.05, 1.10, 1.15, 1.20]); a.set_yticklabels(["1.00", "1.05", "1.10", "1.15", "1.20"], fontsize=18, color=INK2); a.tick_params(axis="y", length=0)
        a.set_xticks([])
        a.text(0, 1.04, model, transform=a.transAxes, fontsize=22, fontweight="bold", ha="left", va="bottom")
        for gi, meth in enumerate(("Population search", "Best-of-N")):
            sel = sorted([r for r in rows if r["model"] == model and r["method"] == meth], key=lambda r: int(r["seed"]))
            v = [float(r["speedup"]) for r in sel]; m = st.median(v); tok = st.median([float(r["total_tokens"]) for r in sel]); med[(model, meth)] = (m, min(v), max(v), tok)
            a.plot([gi, gi], [min(v), max(v)], color=cols[meth], lw=3.5, alpha=.5, solid_capstyle="round", zorder=1)
            a.plot([gi - .25, gi + .25], [m, m], color=INK, lw=3.2, zorder=3)
            for x, r in zip(np.array([-0.18, -0.09, 0.0, 0.09, 0.18]) + gi, sel):
                p3 = r["passes"] != "3/3"
                a.scatter(x, float(r["speedup"]), s=100, color="white" if p3 else cols[meth], edgecolor=cols[meth], linewidth=2.4, zorder=4)
                if p3: a.text(x + 0.06, float(r["speedup"]), "\u2020", fontsize=18, color=INK, va="center")
            a.text(gi + 0.3, m, f"{m:.3f}", ha="left", va="center", fontsize=18, fontweight="bold", color=INK, bbox=dict(fc="white", ec="none", pad=1.5), zorder=5)
        for gi, meth in enumerate(("Population search", "Best-of-N")):
            m, lo, hi, tok = med[(model, meth)]
            xx = px + 0.95 + 4.6 * (gi + 0.6) / 2.2
            T(ax, xx, AX1 + 0.08, meth, size=18, weight="bold", color=cols[meth], ha="center")
            T(ax, xx, AX1 + 0.4, f"{tok:,.0f} tokens", size=18, color=INK2, ha="center")
        pm, bm = med[(model, "Population search")][3], med[(model, "Best-of-N")][3]
        T(ax, px + 0.95 + 4.6, AX0 - 0.1, f"search: +{round(100 * (pm / bm - 1))}% tokens", size=18, weight="bold", ha="right", va="bottom", color=INK)
    T(ax, 0.55, (AX0 + AX1) / 2, "speedup vs stock", size=17, color=INK2, rotation=90, va="center", ha="center")
    # reference strip: C1 | C2
    box(ax, 0.5, 5.28, 7.6, 0.78, fc="#f4f7fb", ec=LINE, r=0.1); box(ax, 8.3, 5.28, 4.53, 0.78, fc="#f4f7fb", ec=LINE, r=0.1)
    T(ax, 0.68, 5.31, "C1  compiler flags, speedup vs stock", size=15.5, color=INK2); T(ax, 0.68, 5.64, f"-O2 1.000\u00d7     -O3 {o3v:.3f}\u00d7     -O3 -march=native {float(nat['median_speedup']):.3f}\u00d7", size=18, weight="bold")
    T(ax, 8.48, 5.31, "C2  human-guided, AI-assisted patches", size=15.5, color=INK2); T(ax, 8.48, 5.64, f"{float(h1['median_speedup']):.3f}\u00d7  /  {float(h2['median_speedup']):.3f}\u00d7", size=18, weight="bold")
    # conclusions
    T(ax, 0.5, 6.15, "DeepSeek: all five search results exceeded all five best-of-N results;\nQwen showed no clear advantage in this sample.", size=19, weight="bold", linespacing=1.2)
    T(ax, 9.75, 6.15, "Requests were matched;\ntoken costs were not.", size=19, weight="bold", linespacing=1.2, color=INK)
    T(ax, 0.5, 6.84, "\u2020 Qwen best-of-N seed 4: re-measurement passed the rule 2/3.  Tokens = reported usage per run (median); requests without usage (DeepSeek HTTP 502) are not counted.\nC1/C2: separate single-node batches, 5 measurements each. C2 patches: GetMesg lookup table; GetMesg + GetFieldIndex lookup tables; no formal timing record.", size=10.5, color=MUTED, va="top", linespacing=1.25)
    ax.text(0.5, 7.4, FOOT, fontsize=11, color=MUTED, ha="left", va="bottom"); ax.text(W - 0.5, 7.4, "2 / 3", fontsize=11, color=MUTED, ha="right", va="bottom")
    return fig

# ---------------------------------------------------------------------------------------------------------------- slide 3
def slide3():
    rows = list(csv.DictReader(open(DATA / "i3_runs.csv")))
    n_race = sum(r["class_"] == "race only" for r in rows); n_bad = sum(r["class_"] == "differs/crash/memory" for r in rows); n_none = sum(r["class_"] == "none detected" for r in rows)
    n_legal = sum(r["legal55"] != "55/55" for r in rows); assert (n_race, n_bad, n_none, n_legal) == (12, 4, 4, 3)
    case = [r for r in rows if r["model"] == "Qwen" and r["method"] == "Population search" and r["seed"] == "3"][0]
    fig, ax = new_slide(); title(ax, "Passing the benchmark did not guarantee equivalent behavior")
    box(ax, 0.5, 1.15, 5.5, 1.95, fc="#f4f7fb", ec=LINE)
    T(ax, 0.7, 1.27, "Supplied checks \u2014\nbefore timing every candidate", size=19, weight="bold", color=INK2, linespacing=1.15)
    T(ax, 0.75, 1.98, "\u2022 4 fixed FIT files, single thread\n\u2022 decode checksum + profile digest\n\u2022 candidate must not start threads", size=19, linespacing=1.38)
    ax.add_patch(FancyArrowPatch((3.25, 3.12), (3.25, 3.3), arrowstyle="-|>", mutation_scale=22, color=BLUE, lw=2.2))
    box(ax, 0.5, 3.32, 5.5, 2.78, fc="#eaf2fc", ec=BLUE, lw=2.2)
    T(ax, 0.7, 3.45, "Expanded validation", size=22, weight="bold", color=BLUE)
    T(ax, 0.75, 3.95, "\u2022 55 extra valid FIT files\n    (written by the SDK encoder)\n\u2022 400 mutated inputs\n\u2022 ASan/UBSan: memory errors,\n    undefined behavior\n\u2022 TSan: 4 threads, 24 files", size=19, linespacing=1.32)
    rx = 6.4
    T(ax, rx, 1.1, "Final patches of the 20 runs", size=19, color=INK2)
    heads = [("20/20", "passed the supplied checks", INK2), ("16/20", "had findings in the expanded\ndynamic checks", AMBER), ("3/20", "differed on additional\nvalid FIT files", RED)]
    for i, (big, small, col) in enumerate(heads):
        y = 1.55 + i * 0.7
        T(ax, rx, y + 0.3, big, size=34, weight="bold", color=col, va="center"); T(ax, rx + 1.85, y + 0.3, small, size=19, va="center", linespacing=1.1)
    sx, sy, sq, g = rx, 3.66, 0.24, 0.045; i = 0
    for key, col, n in (("race", AMBER, n_race), ("bad", RED, n_bad), ("none", GREY, n_none)):
        for _ in range(n):
            ax.add_patch(Rectangle((sx + i * (sq + g), sy), sq, sq * 1.45, fc=col, ec="white", lw=1)); i += 1
        i += 0.9
    leg = [(AMBER, "12  data-race report only (no wrong output seen)"), (RED, "4  also output difference, crash or memory error"), (GREY, "4  no new finding detected (not proof of safety)")]
    for k, (col, lab) in enumerate(leg):
        yy = 4.15 + k * 0.34
        ax.add_patch(Rectangle((rx, yy + 0.04), 0.22, 0.22, fc=col, ec="none")); T(ax, rx + 0.35, yy, lab, size=16.5, va="top")
    box(ax, rx, 5.3, 6.45, 0.98, fc="#fdecec", ec=RED, lw=2.4)
    T(ax, rx + 0.2, 5.36, "Qwen population search, seed 3", size=19, weight="bold", color=RED)
    T(ax, rx + 0.2, 5.63, f"Original benchmark files:  {case['original4']} matched", size=19)
    T(ax, rx + 0.2, 5.93, "Additional valid files:", size=19); T(ax, rx + 2.85, 5.87, "45/55 differed", size=23, weight="bold", color=RED)
    T(ax, 0.5, 6.42, "Broader correctness validation is needed before treating benchmark\nspeedups as reliable optimizations.", size=21, weight="bold", linespacing=1.12)
    footer(ax, 3); return fig

def main():
    figs = [slide1(), slide2(), slide3()]
    pdf = OUT / "CanMehEvolve_ZhouZiang.pdf"
    with PdfPages(pdf) as pp:
        for f in figs: pp.savefig(f, facecolor="white")
    import subprocess
    subprocess.run(["pdftoppm", "-r", "150", "-png", str(pdf), str(OUT / "_pg")], check=True)
    for i in range(1, 4): (OUT / f"_pg-{i}.png").replace(OUT / f"slide{i}.png")
    # overview of the three pages
    import matplotlib.image as mpimg
    fig = plt.figure(figsize=(13.333, 2.6 * 1.0 + 0.2), facecolor="#dddddd")
    for i in range(3):
        a = fig.add_axes([0.01 + i * 0.33, 0.04, 0.32, 0.92]); a.imshow(mpimg.imread(OUT / f"slide{i+1}.png")); a.axis("off")
    fig.savefig(OUT / "overview_thumbnails.png", dpi=110, facecolor="#dddddd")
    print("wrote", pdf)

if __name__ == "__main__":
    main()
