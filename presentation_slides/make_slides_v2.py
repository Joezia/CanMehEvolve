#!/usr/bin/env python3
"""v2 slides: 3-page 16:9 static PDF + PNG previews + overview. White background, one sans-serif font, no footnotes/footers.
Data: presentation_slides/data/*.csv (copied from presentation_materials/tables; computed from raw run files). No experiment is run here.
Page-3 counts are derived from data/correctness_unified.csv (one row per final patch, 'round-2 final' groups).
usage: python3 presentation_slides/make_slides_v2.py   (needs matplotlib, numpy, pdftoppm)"""
import csv, os, math, statistics as st, subprocess
from pathlib import Path
os.environ.setdefault("MPLCONFIGDIR", str(Path.home() / ".mplconfig"))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.transforms import blended_transform_factory

HERE = Path(__file__).resolve().parent; DATA = HERE / "data"
W, H = 13.333, 7.5
INK, INK2, MUTED, GRID, RULE = "#14171a", "#46505a", "#7a838c", "#e6e9ed", "#b9c0c8"
BLUE, ORANGE, GREY = "#2a78d6", "#d9780f", "#8d949c"
plt.rcParams.update({"font.family": "Liberation Sans", "pdf.fonttype": 42, "text.color": INK})
TITLE, BODY, CELL = 34, 22, 20

def new_slide():
    fig = plt.figure(figsize=(W, H), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off")
    return fig, ax

def T(ax, x, y, s, size=BODY, weight="normal", color=INK, ha="left", va="top", **kw):
    return ax.text(x, y, s, fontsize=size, fontweight=weight, color=color, ha=ha, va=va, **kw)

def title(ax, s): T(ax, 0.5, 0.3, s, size=TITLE, weight="bold")

def hline(ax, x0, x1, y, color=RULE, lw=1.2): ax.plot([x0, x1], [y, y], color=color, lw=lw, solid_capstyle="butt")

def read(name): return list(csv.DictReader(open(DATA / name)))

# ------------------------------------------------------------------------------------------------ page 1
def pct(x, up):  # percentage, 2 decimals, rounded outward so the interval is never narrowed
    v = x * 100; f = 100.0
    v = math.ceil(v * f - 1e-9) / f if up else math.floor(v * f + 1e-9) / f
    return "100" if v >= 100 else ("0" if v == 0 else f"{v:.2f}")

def slide1():
    fig, ax = new_slide(); title(ax, "Speedup Judge")
    # left: interface
    T(ax, 0.5, 1.2, "candidateIsFaster(reply, 0.02) \u2192 bool", size=20, weight="bold", family="Liberation Mono", color=BLUE)
    items = [("Input", "Raw timings of candidate and Original SDK (-O2): 10 processes \u00d7 9 repetitions"),
             ("Ratio", "Per process: median candidate / median Original SDK; then median over processes"),
             ("Test", "Exact sign-flip test on the log-ratios"),
             ("Return true", "mean log-ratio < 0, p < 0.01, ratio \u2264 0.98")]
    y = 1.9
    for lab, txt in items:
        T(ax, 0.5, y, lab, size=BODY, weight="bold", color=INK2)
        lines = wrap(fig, ax, txt, BODY, 6.5)
        T(ax, 0.5, y + 0.4, "\n".join(lines), size=BODY, linespacing=1.05)
        y += 0.4 + 0.38 * len(lines) + 0.2
    T(ax, 0.5, y + 0.02, "Return false = not confirmed faster.", size=BODY, color=INK2)
    # right: calibration table
    cal = {r["pair"]: r for r in read("calibration_pairs.csv")}; fpr = [r for r in read("fpr_summary.csv") if r["group"] == "Synthetic null, all"][0]
    rows = [("1.000\u00d7 (Null)", int(fpr["false_accepts"]), int(fpr["valid_measurements"]), float(fpr["cp95_lo"]), float(fpr["cp95_hi"]))]
    for key, lab in (("faster-1-percent", "\u22481.010\u00d7"), ("faster-2-percent", "\u22481.020\u00d7"), ("faster-5-percent", "\u22481.050\u00d7"), ("faster-10-percent", "\u22481.100\u00d7")):
        r = cal[key]; rows.append((lab, int(r["judged_faster"]), int(r["valid_trials"]), float(r["cp95_lo"]), float(r["cp95_hi"])))
    assert [(a, b) for _, a, b, _, _ in rows] == [(0, 500), (1, 100), (42, 100), (99, 100), (100, 100)]
    tx = [7.55, 9.35, 10.85]; x_end = 12.85
    T(ax, tx[0], 1.2, "Known\nspeedup", size=CELL, weight="bold", linespacing=1.1)
    T(ax, tx[1], 1.2, "Accepted /\ntrials", size=CELL, weight="bold", linespacing=1.1)
    T(ax, tx[2], 1.2, "95% CI of\nacceptance rate", size=CELL, weight="bold", linespacing=1.1)
    hline(ax, tx[0], x_end, 1.95, color=INK, lw=1.6)
    pitch = 0.56
    for i, (lab, a, n, lo, hi) in enumerate(rows):
        yy = 2.1 + i * pitch
        T(ax, tx[0], yy, lab, size=CELL); T(ax, tx[1], yy, f"{a}/{n}", size=CELL)
        T(ax, tx[2], yy, f"{pct(lo, False)}\u2013{pct(hi, True)}%", size=CELL)
        if i < len(rows) - 1: hline(ax, tx[0], x_end, yy + pitch - 0.08, color=GRID)
    yb = 2.1 + 5 * pitch - 0.08; hline(ax, tx[0], x_end, yb, color=INK, lw=1.2)
    bias = max(abs(float(cal[k]["abs_bias"])) for k in ("null", "faster-1-percent", "faster-2-percent", "faster-5-percent", "faster-10-percent"))
    first90 = min(float(cal[k]["true_speedup"]) for k in ("faster-1-percent", "faster-2-percent", "faster-5-percent", "faster-10-percent") if float(cal[k]["rate"]) >= 0.9)
    assert abs(bias - 0.00145) < 5e-6 and abs(first90 - 1.05) < 1e-3
    t1 = "\n".join(wrap(fig, ax, "Among tested points, detection reaches at least 90% from \u22481.05\u00d7.", BODY, 5.3))
    t2 = "\n".join(wrap(fig, ax, f"Largest absolute median-ratio deviation: {bias:.5f}.", BODY, 5.3))
    T(ax, tx[0], yb + 0.3, t1, size=BODY, linespacing=1.05)
    T(ax, tx[0], yb + 0.3 + 0.38 * (t1.count("\n") + 1) + 0.25, t2, size=BODY, linespacing=1.05)
    return fig

def wrap(fig, ax, text, size, width_in):
    r = fig.canvas.get_renderer(); out, cur = [], ""
    for w_ in text.split():
        t = (cur + " " + w_).strip(); tt = ax.text(0, 0, t, fontsize=size); bb = tt.get_window_extent(r); tt.remove()
        if bb.width / fig.dpi > width_in and cur: out.append(cur); cur = w_
        else: cur = t
    out.append(cur); return out

# ------------------------------------------------------------------------------------------------ page 2
def slide2():
    runs = read("i3_runs.csv"); ctl = read("controls_summary.csv")
    o3 = st.median([float(r["median_speedup"]) for r in ctl if r["comparison"].startswith("-O3 vs stock")])
    nat = [r for r in ctl if r["comparison"].startswith("-O3 -march=native vs stock") and r["valid_comparison"] == "True"][0]
    h1 = [r for r in ctl if "attempt 1" in r["comparison"]][0]; h2 = [r for r in ctl if "attempt 2" in r["comparison"]][0]
    rowsp = [("C1: -O3", o3, None, None, GREY), ("C1: -O3 -march=native", float(nat["median_speedup"]), None, None, GREY),
             ("C2: Human-guided patch 1", float(h1["median_speedup"]), None, None, GREY), ("C2: Human-guided patch 2", float(h2["median_speedup"]), None, None, GREY)]
    for model in ("Qwen", "DeepSeek"):
        for meth in ("Population search", "Best-of-N"):
            sel = [r for r in runs if r["model"] == model and r["method"] == meth]; assert len(sel) == 5
            v = [float(r["speedup"]) for r in sel]; tok = st.median([float(r["total_tokens"]) for r in sel])
            rowsp.append((f"{model}: {meth}", st.median(v), (min(v), max(v)), tok, BLUE if meth.startswith("Pop") else ORANGE))
    exp = [1.090, 1.108, 1.068, 1.082, 1.0745, 1.0560, 1.1648, 1.0732]
    assert all(abs(r[1] - e) < 6e-4 for r, e in zip(rowsp, exp)), [r[1] for r in rowsp]
    fig, ax = new_slide(); title(ax, "Search Results")
    T(ax, 0.5, 1.0, "Select a function in a parent patch → LLM rewrite → check and time → update population", size=BODY)
    T(ax, 0.5, 1.45, "C3: Best-of-N comparison · C4: 5 seeds, 40 requests per run", size=BODY, weight="bold")
    T(ax, 0.5, 1.85, "Dot = median · line = full range of the five seeds (not a confidence interval)", size=BODY, color=INK2)
    AL, AR, AT, AB = 4.45, 9.75, 2.8, 5.45   # axes box in inches (x left/right, y top/bottom of slide)
    a = fig.add_axes([AL / W, 1 - AB / H, (AR - AL) / W, (AB - AT) / H]); a.set_facecolor("white")
    a.set_xlim(0.99, 1.22); a.set_ylim(len(rowsp) - 0.5, -0.5)
    for sp in ("top", "right", "left"): a.spines[sp].set_visible(False)
    a.spines["bottom"].set_color(RULE)
    a.set_yticks(range(len(rowsp))); a.set_yticklabels([r[0] for r in rowsp], fontsize=CELL, color=INK); a.tick_params(axis="y", length=0, pad=10)
    a.set_xticks([1.00, 1.05, 1.10, 1.15, 1.20]); a.set_xticklabels(["1.00", "1.05", "1.10", "1.15", "1.20"], fontsize=CELL, color=INK2); a.tick_params(axis="x", length=4, color=RULE)
    a.xaxis.grid(True, color=GRID, lw=1); a.set_axisbelow(True)
    a.axvline(1.0, color=INK, lw=1.6, ls=(0, (4, 3)), zorder=2)
    a.axhline(3.5, color=RULE, lw=1)
    a.set_xlabel("Speedup relative to Original SDK (-O2)", fontsize=CELL, color=INK2, labelpad=6)
    T(ax, 12.83, AT - 0.12, "Reported\ntokens/run", size=CELL, weight="bold", ha="right", va="bottom", linespacing=1.1)
    for i, (lab, m, rng, tok, col) in enumerate(rowsp):
        if rng: a.plot(rng, [i, i], color=col, lw=5, solid_capstyle="round", alpha=0.55, zorder=3)
        a.scatter([m], [i], s=130, color=col, edgecolor="white", linewidth=1.2, zorder=5)
        xr = (rng[1] if rng else m) + 0.004
        a.text(xr, i, f"{m:.3f}", fontsize=CELL, va="center", ha="left", color=INK, zorder=6)
    for i, r in enumerate(rowsp):
        if r[3]:
            yfig = 1 - (AT + (AB - AT) * (i + 0.5) / len(rowsp)) / H
            fig.text(12.83 / W, yfig, f"{r[3]/1000:.1f}k", fontsize=CELL, ha="right", va="center")
        else:
            yfig = 1 - (AT + (AB - AT) * (i + 0.5) / len(rowsp)) / H
            fig.text(12.83 / W, yfig, "—", fontsize=CELL, ha="right", va="center", color=MUTED)
    T(ax, 0.5, 6.4, "DeepSeek showed a clear observed\nsearch advantage; Qwen did not show\na clear benefit in this sample.", size=BODY, linespacing=1.05)
    T(ax, 7.2, 6.4, "Equal request budgets did not\nimply equal token costs.", size=BODY, linespacing=1.05)
    return fig

# ------------------------------------------------------------------------------------------------ page 3
def slide3():
    rows = [r for r in read("correctness_unified.csv") if r["group"].startswith("round-2 final")]; assert len(rows) == 20
    legal = sum(r["legal_encoder_files_identical"] != r["legal_encoder_files_compared"] for r in rows)
    mut = sum(int(r["crash_patch_only"]) > 0 for r in rows)
    san = sum(int(r["asan_errors"]) > 0 or int(r["ubsan_messages_not_in_stock"]) > 0 for r in rows)
    tsan = sum(int(r["tsan_race_locations"]) > 0 for r in rows)
    race_only = sum(int(r["tsan_race_locations"]) > 0 and int(r["crash_patch_only"]) == 0 and not (int(r["asan_errors"]) > 0 or int(r["ubsan_messages_not_in_stock"]) > 0)
                    and r["legal_encoder_files_identical"] == r["legal_encoder_files_compared"] for r in rows)
    assert (legal, mut, san, tsan, race_only) == (3, 1, 1, 15, 12), (legal, mut, san, tsan, race_only)
    assert {r["asan_ubsan_subset_files"] for r in rows} == {"126"} and {r["tsan_subset_files"] for r in rows} == {"24"}
    assert all(r["original4_identical"] == "4" for r in rows)
    fig, ax = new_slide(); title(ax, "Additional Correctness Tests")
    T(ax, 0.5, 1.2, "All 20 final patches passed the supplied correctness checks.", size=24, weight="bold")
    cx = [0.5, 3.95, 7.0, 9.2]; xe = 12.83
    heads = ["Additional test", "Test coverage", "Patches with\nnew findings", "Observed problem"]
    for x, h_ in zip(cx, heads): T(ax, x, 1.95, h_, size=CELL, weight="bold", linespacing=1.1)
    hline(ax, 0.5, xe, 2.75, color=INK, lw=1.6)
    data = [("Valid-input differential test", "55 additional SDK-encoded files", f"{legal}/20", "Different decoded output"),
            ("Mutated-input differential test", "400 mutated files", f"{mut}/20", "More crashes than the Original SDK"),
            ("ASan / UBSan", "Up to 126 files, single thread", f"{san}/20", "New memory or undefined-behavior reports"),
            ("TSan", "4 threads, up to 24 files", f"{tsan}/20", "Data-race reports")]
    rh = 0.82
    for i, (a_, b_, c_, d_) in enumerate(data):
        y = 2.95 + i * rh
        wa = "\n".join(wrap(fig, ax, a_, CELL, 3.2)); wb = "\n".join(wrap(fig, ax, b_, CELL, 2.9)); wd = "\n".join(wrap(fig, ax, d_, CELL, 3.6))
        T(ax, cx[0], y, wa, size=CELL, linespacing=1.12); T(ax, cx[1], y, wb, size=CELL, linespacing=1.12)
        T(ax, cx[2], y, c_, size=CELL, weight="bold"); T(ax, cx[3], y, wd, size=CELL, linespacing=1.12)
        hline(ax, 0.5, xe, y + rh - 0.1, color=GRID if i < len(data) - 1 else INK, lw=1.2 if i < len(data) - 1 else 1.6)
    T(ax, 0.5, 6.35, "A patch can have findings in more than one test.", size=BODY, color=INK2)
    T(ax, 0.5, 6.8, "The supplied checks did not cover all failures found by the broader tests.", size=24, weight="bold")
    return fig

def main():
    figs = [slide1(), slide2(), slide3()]
    pdf = HERE / "CanMehEvolve_ZhouZiang_v2.pdf"
    with PdfPages(pdf) as pp:
        for f in figs: pp.savefig(f, facecolor="white")
    subprocess.run(["pdftoppm", "-r", "150", "-png", str(pdf), str(HERE / "_pg")], check=True)
    for i in range(1, 4): (HERE / f"_pg-{i}.png").replace(HERE / f"slide{i}_v2.png")
    fig = plt.figure(figsize=(13.333, 2.8), facecolor="#dddddd")
    for i in range(3):
        a = fig.add_axes([0.01 + i * 0.33, 0.04, 0.32, 0.92]); a.imshow(mpimg.imread(HERE / f"slide{i+1}_v2.png")); a.axis("off")
    fig.savefig(HERE / "overview_thumbnails_v2.png", dpi=110, facecolor="#dddddd")
    print("wrote", pdf)

if __name__ == "__main__":
    main()
