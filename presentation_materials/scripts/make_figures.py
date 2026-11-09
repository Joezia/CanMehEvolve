#!/usr/bin/env python3
"""Static figures (PNG + vector PDF) from the CSV tables in presentation_materials/tables. Palette: validated reference palette of the dataviz skill
(categorical slots 1-3 only: blue = population search, orange = greedy chain, aqua = best-of-N; status colours for correctness with a symbol and a label)."""
import sys, os, re; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
os.environ.setdefault("MPLCONFIGDIR", str(__import__("pathlib").Path.home() / ".mplconfig"))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from pm_lib import *
from runsets import CONFIGS, CFG

SURF, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
ALGO_COL = {"population": BLUE, "greedy": ORANGE, "best-of-N": AQUA}
GOOD, WARN, SERIOUS, CRIT, NA = "#0ca30c", "#fab219", "#ec835a", "#d03b3b", "#898781"
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF, "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "text.color": INK, "font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": False, "grid.color": GRID,
                     "pdf.fonttype": 42, "axes.titlesize": 10, "axes.titleweight": "bold", "axes.titlelocation": "left"})
FIG = PM / "figures"; FD = PM / "figure_data"; FIG.mkdir(exist_ok=True); FD.mkdir(exist_ok=True)

def save(fig, name):
    fig.savefig(FIG / f"{name}.png", dpi=200, bbox_inches="tight"); fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight"); plt.close(fig)

R = list(csv.DictReader(open(PM / "tables/runs_all.csv")))
CORR = {r["object"]: r for r in csv.DictReader(open(PM / "tables/correctness_unified.csv"))}
def fnum(x):
    try: return float(x)
    except Exception: return None

def status_of(obj):
    r = CORR.get(obj)
    if not r or r.get("tested") != "yes": return "not tested", NA, "?"
    f = r.get("findings", "")
    leg = "legal encoder file" in f or "original file" in f
    if leg or "digest mismatch" in f or "crashes where" in f or "ASan error" in f: return "wrong output / crash / memory error", CRIT, "x"
    if "output differs" in f: return "differs only on hostile mutant files", SERIOUS, "D"
    if "TSan" in f: return "race reported by TSan, no wrong output seen", WARN, "!"
    return "no finding in the tested conditions", GOOD, "o"

def obj_of_run(r):
    cfg, s = r["config"], r["seed"]
    if cfg.endswith("I3"): return "r2-" + {"qwen_pop": "qwen-population", "qwen_bon": "qwen-bestofn", "ds_pop": "ds-population", "ds_bon": "ds-bestofn"}[cfg[:-3]] + f"-s{s}"
    if cfg == "ds_bon_I2": return f"final-bestofn-seed{s}"
    if cfg == "ds_greedy_I2": return None if s == "3" else f"final-greedy-seed{s}"      # seed 3's 40-request final differs from the tested 38-request state
    return None
MARK = {"x": "X", "D": "D", "!": "^", "o": "o", "?": "s"}

# ---------------------------------------------------------------- Fig 1: seed-level result, per model, with correctness status
rows = []
order = {"Qwen3-coder-next": ["qwen_pop_I1", "qwen_bon_I1", "qwen_pop_I3", "qwen_bon_I3"], "DeepSeek-v4.1-flash": ["ds_greedy_I2", "ds_bon_I2", "ds_pop_I3", "ds_bon_I3"]}

C = {r["comparison"] + "|" + r["batch"]: r for r in csv.DictReader(open(PM / "tables/controls_summary.csv"))}
def csp(key): return float([v for k, v in C.items() if k.startswith(key)][0]["median_speedup"])
refs = [(float([v for k, v in C.items() if k.startswith("-O3 vs stock -O2")][0]["median_speedup"]), "-O3"),
        (csp("-O3 -march=native vs stock"), "-O3 -march=native"), (csp("human patch attempt 1"), "human 1"), (csp("human patch attempt 2"), "human 2")]
fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6), sharex=True)
ylabs = []
for ax, (model, cids) in zip(axes, order.items()):
    for yi, cid in enumerate(cids[::-1]):
        label, algo, impl = CFG[cid][1], CFG[cid][2], CFG[cid][4]
        rr = sorted([r for r in R if r["config"] == cid], key=lambda r: int(r["seed"]))
        v = [float(r["remeasure_speedup_median3"]) for r in rr]
        ax.plot([min(v), max(v)], [yi, yi], color=ALGO_COL[algo], lw=2.2, solid_capstyle="round", alpha=.55, zorder=1)
        ax.plot([median(v)] * 2, [yi - .27, yi + .27], color=INK, lw=2, zorder=3)
        for k, r in enumerate(rr):
            st, col, sym = status_of(obj_of_run(r)) if obj_of_run(r) else ("not tested", NA, "?")
            ax.scatter(float(r["remeasure_speedup_median3"]), yi + (k - 2) * 0.11, s=46, marker=MARK[sym], color=ALGO_COL[algo], edgecolor=col, linewidth=2.0 if sym != "?" else 1.2, zorder=4)
            rows.append({"model": model, "config": cid, "seed": r["seed"], "remeasured_speedup": r["remeasure_speedup_median3"], "correctness_status": st})
        ylabs.append(f"{CFG[cid][2]}  (code {CFG[cid][4]})\nmedian {median(v):.3f}  [{min(v):.3f}, {max(v):.3f}]")
    ax.set_yticks(range(4)); ax.set_yticklabels(ylabs, fontsize=8); ylabs = []
    ax.set_title(model); ax.set_xlim(1.0, 1.24)
    ax.xaxis.grid(True); ax.set_axisbelow(True)
    for x, lab in refs:
        ax.axvline(x, color=MUTED, lw=.9, ls=(0, (3, 3)), zorder=0); ax.text(x + .001, -.55, lab, rotation=90, va="bottom", ha="left", fontsize=6.5, color=MUTED)
    ax.set_ylim(-.6, 3.7)
handles = [Line2D([], [], marker="s", color=NA, mfc=SURF, mec=NA, ls="", label="correctness: final patch not tested"), Line2D([], [], marker="o", color=GOOD, mfc=SURF, mec=GOOD, mew=2, ls="", label="no finding in tested conditions"),
           Line2D([], [], marker="^", color=WARN, mfc=SURF, mec=WARN, mew=2, ls="", label="TSan race, no wrong output seen"), Line2D([], [], marker="D", color=SERIOUS, mfc=SURF, mec=SERIOUS, mew=2, ls="", label="differs on hostile mutant files only"),
           Line2D([], [], marker="X", color=CRIT, mfc=SURF, mec=CRIT, mew=2, ls="", label="wrong output / crash / memory error")]
fig.supxlabel("independent re-measurement of the fixed final patch: speedup vs stock -O2 (median of 3 measurements)", fontsize=9, color=INK2, y=0.03)
fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=8, bbox_to_anchor=(.5, -.14))
fig.suptitle("Seed-level results (one dot = one independent search); black tick = median, line = range; dashed = compiler and human controls (single node, 5 measurements each)", x=.01, ha="left", fontsize=9.5, fontweight="bold", y=1.0)
save(fig, "fig1_seed_results_with_correctness"); write_csv(FD / "fig1_seed_results.csv", rows)

# ---------------------------------------------------------------- Fig 2: calibration detection
cal = list(csv.DictReader(open(PM / "tables/calibration_pairs.csv")))
fig, ax = plt.subplots(figsize=(6.4, 3.8))
pts = [r for r in cal if r["pair"] in ("slower-10-percent", "null", "faster-1-percent", "faster-2-percent", "faster-5-percent", "faster-10-percent")]
x = [float(r["true_reduction_pct"]) for r in pts]; y = [100 * float(r["rate"]) for r in pts]
lo = [100 * float(r["cp95_lo"]) for r in pts]; hi = [100 * float(r["cp95_hi"]) for r in pts]
ax.axvspan(-1, 2, color=GRID, alpha=.5, lw=0); ax.text(0.5, 108, "below the 2% gate", ha="center", fontsize=8, color=MUTED)
ax.errorbar(x, y, yerr=[[a - b for a, b in zip(y, lo)], [b - a for a, b in zip(y, hi)]], fmt="o", color=BLUE, ecolor=BLUE, capsize=3, lw=1.5, ms=6)
ax.axhline(90, color=MUTED, lw=.8, ls=(0, (3, 3))); ax.text(-9.9, 91.5, "90% detection", fontsize=7.5, color=MUTED)
for r, a, b in zip(pts, x, y):
    ax.annotate(f"{r['judged_faster']}/{r['valid_trials']}", (a, b), textcoords="offset points", xytext=(6, -12 if b > 50 else 8), fontsize=7.5, color=INK2)
ax.set_xlabel("true time reduction built into the pair (%)  [negative = slower]"); ax.set_ylabel("judged faster in a single measurement (%)")
ax.set_title("Detection rate with exact 95% intervals (100 trials per point)"); ax.set_ylim(-5, 112); ax.set_xlim(-11.5, 10.5); ax.yaxis.grid(True); ax.set_axisbelow(True)
save(fig, "fig2_calibration_detection"); write_csv(FD / "fig2_calibration.csv", [{"pair": r["pair"], "true_reduction_pct": r["true_reduction_pct"], "k": r["judged_faster"], "n": r["valid_trials"], "cp_lo": r["cp95_lo"], "cp_hi": r["cp95_hi"]} for r in pts])

# ---------------------------------------------------------------- Fig 3: false-accept upper bounds
fp = list(csv.DictReader(open(PM / "tables/fpr_summary.csv")))
sel = [r for r in fp if r["group"] in ("Synthetic null, calibration batches (xcnc2, 2 batches)", "Synthetic null, extra batches, xcnc", "Synthetic null, extra batches, xcnd", "Synthetic null, all", "SDK inert, batch group A, xcnc", "SDK inert, batch group A, xcnd",
                                         "SDK inert, batch group B, xcnc", "SDK inert, batch group B, xcnd", "SDK inert, all batches, xcnc", "SDK inert, all batches, xcnd", "SDK inert, all batches, both classes")]
fig, ax = plt.subplots(figsize=(7.6, 4.3))
for i, r in enumerate(sel[::-1]):
    col = BLUE if r["family"].startswith("synthetic") else ORANGE
    ax.plot([0, 100 * float(r["cp95_hi"])], [i, i], color=col, lw=2.4, solid_capstyle="round"); ax.scatter([0], [i], color=col, s=30, zorder=3)
    ax.text(100 * float(r["cp95_hi"]) + .06, i, f"0/{r['valid_measurements']}  upper {100*float(r['cp95_hi']):.2f}%", va="center", fontsize=8, color=INK2)
ax.axvline(1.0, color=MUTED, lw=.9, ls=(0, (3, 3))); ax.text(1.02, len(sel) - .45, "1%", fontsize=8, color=MUTED)
ax.set_yticks(range(len(sel))); ax.set_yticklabels([r["group"] for r in sel[::-1]], fontsize=8); ax.set_xlim(0, 4.6); ax.set_xlabel("95% upper confidence bound of the false-accept rate (%) when 0 false accepts were observed")
ax.set_title("False accepts: 0 in every group; the bound depends on how many valid measurements"); ax.xaxis.grid(True); ax.set_axisbelow(True)
ax.legend(handles=[Line2D([], [], color=BLUE, lw=2.4, label="synthetic null pair"), Line2D([], [], color=ORANGE, lw=2.4, label="real SDK, inert patch")], frameon=False, loc="lower right", fontsize=8)
save(fig, "fig3_false_accept_bounds"); write_csv(FD / "fig3_fpr.csv", [{k: r[k] for k in ("group", "valid_measurements", "false_accepts", "cp95_lo", "cp95_hi")} for r in sel])

# ---------------------------------------------------------------- Fig 4: cost vs result
fig, ax = plt.subplots(figsize=(7.6, 4.6))
MK = {"I1": "s", "I2": "^", "I3": "o"}
pts4 = []
for r in R:
    tok = float(r["total_tokens"]); sp = float(r["remeasure_speedup_median3"]); a = CFG[r["config"]][2]
    mdl = "Qwen" if r["config"].startswith("qwen") else "DeepSeek"
    ax.scatter(tok, sp, s=36, marker=MK[r["impl"]], facecolor=ALGO_COL[a] if mdl == "DeepSeek" else SURF, edgecolor=ALGO_COL[a], linewidth=1.6, zorder=3)
    pts4.append({"run": r["run"], "total_tokens": tok, "remeasured_speedup": sp})
ax.set_xscale("log"); ax.set_xticks([2e4, 3e4, 5e4, 1e5, 2e5, 3e5, 6e5]); ax.set_xticklabels(["20k", "30k", "50k", "100k", "200k", "300k", "600k"]); ax.minorticks_off()
ax.set_xlabel("total tokens (prompt + completion; reasoning tokens are part of completion), log scale"); ax.set_ylabel("independent re-measured speedup")
ax.set_title("Cost against result, every seed of every configuration"); ax.yaxis.grid(True); ax.set_axisbelow(True)
h = [Line2D([], [], marker="o", color=BLUE, ls="", label="population search"), Line2D([], [], marker="o", color=ORANGE, ls="", label="greedy chain"), Line2D([], [], marker="o", color=AQUA, ls="", label="best-of-N"),
     Line2D([], [], marker="o", color=INK2, mfc=INK2, ls="", label="filled = DeepSeek"), Line2D([], [], marker="o", color=INK2, mfc=SURF, ls="", label="hollow = Qwen"),
     Line2D([], [], marker="s", color=INK2, mfc=SURF, ls="", label="code I1"), Line2D([], [], marker="^", color=INK2, mfc=SURF, ls="", label="code I2"), Line2D([], [], marker="o", color=INK2, mfc=SURF, ls="", label="code I3")]
ax.legend(handles=h, frameon=False, fontsize=7.5, ncol=2, loc="center right")
save(fig, "fig4_cost_vs_result"); write_csv(FD / "fig4_cost.csv", pts4)

# ---------------------------------------------------------------- Fig 5: representative chain
ch = list(csv.DictReader(open(PM / "tables/chain_steps_ds_greedy_s3.csv")))
fig, ax = plt.subplots(figsize=(8.4, 4.4))
xs = [int(c["step"]) for c in ch]; ys = [float(c["cumulative_speedup_at_search_time"]) for c in ch]
ax.step([0] + xs, [1.0] + ys, where="post", color=ORANGE, lw=2)
for c in ch:
    tm = c.get("corr_tsan_digest_mismatches", ""); tl = c.get("corr_tsan_locations", "")
    col, mk = (GOOD, "o") if tl == "0" else ((CRIT, "X") if tm not in ("", "-", "None", "0") else ((WARN, "^") if tl not in ("", "None") else (NA, "s")))
    ax.scatter(int(c["step"]), float(c["cumulative_speedup_at_search_time"]), s=60, marker=mk, color=SURF, edgecolor=col, linewidth=2.2, zorder=4)
    ax.annotate(c["function"].replace("::", "::\n", 1) if len(c["function"]) > 18 else c["function"], (int(c["step"]), float(c["cumulative_speedup_at_search_time"])), textcoords="offset points", xytext=(0, -24 if int(c["step"]) % 2 == 0 else 11), fontsize=6.3, color=INK2, ha="center")
ax.axhline(1.1758, color=MUTED, lw=.9, ls=(0, (3, 3))); ax.text(.1, 1.1775, "independent re-measurement of the 40-request final patch: 1.1758", fontsize=7.5, color=MUTED)
ax.set_ylim(.975, 1.195); ax.set_xlabel("accepted step (rank-rule record updates)"); ax.set_ylabel("cumulative speedup at search time"); ax.set_xticks(xs); ax.yaxis.grid(True); ax.set_axisbelow(True)
ax.set_title("DeepSeek greedy chain, seed 3: search-time record after each accepted step\n(only the final patch was re-measured independently)", fontsize=9.5)
h = [Line2D([], [], marker="o", color=GOOD, mfc=SURF, mew=2, ls="", label="TSan clean at this step"), Line2D([], [], marker="X", color=CRIT, mfc=SURF, mew=2, ls="", label="TSan race + wrong output under 4 threads"),
     Line2D([], [], marker="^", color=WARN, mfc=SURF, mew=2, ls="", label="TSan race, run did not finish"), Line2D([], [], marker="s", color=NA, mfc=SURF, mew=2, ls="", label="not tested")]
ax.legend(handles=h, frameon=False, fontsize=7.5, loc="lower right")
save(fig, "fig5_chain_seed3"); write_csv(FD / "fig5_chain.csv", ch)

# ---------------------------------------------------------------- Fig 6: stacking
cur = list(csv.DictReader(open(PM / "figure_data/stack_curve.csv"))); sb = list(csv.DictReader(open(PM / "tables/stacking_by_seed.csv")))
fig, ax = plt.subplots(figsize=(7.4, 4.4))
for s in range(1, 6):
    p = [(int(c["K"]), float(c["speedup"])) for c in cur if int(c["seed"]) == s]
    ax.plot([a for a, _ in p], [b for _, b in p], color=MUTED, lw=1, alpha=.8)
    bk = [r for r in sb if int(r["seed"]) == s][0]
    ax.scatter(int(bk["bestK_posthoc"]), float(bk["bestK_speedup_posthoc"]), marker="*", s=90, color=AQUA, edgecolor=INK, linewidth=.6, zorder=4)
med = {}
for c in cur: med.setdefault(int(c["K"]), []).append(float(c["speedup"]))
ks = sorted(k for k in med if len(med[k]) >= 3)
ax.plot(ks, [median(med[k]) for k in ks], color=AQUA, lw=2.6, label="median over seeds (K with >= 3 seeds)")
ax.axhline(median([float(r["best_of_N_final_remeasured"]) for r in sb]), color=AQUA, lw=1, ls=(0, (3, 3))); ax.text(11.1, 1.0745, "best-of-N final (median)", fontsize=7.5, color=INK2, ha="right")
ax.axhline(median([float(r["greedy_final_remeasured_40req"]) for r in sb]), color=ORANGE, lw=1, ls=(0, (3, 3))); ax.text(11.1, 1.1775, "greedy final (median)", fontsize=7.5, color=INK2, ha="right")
ax.set_xlabel("K = number of best-of-N candidates (one per function) stacked, best search-time ratio first"); ax.set_ylabel("speedup, median of 3 independent measurements"); ax.set_xticks(range(1, 13)); ax.yaxis.grid(True); ax.set_axisbelow(True)
ax.set_title("Stacking the best-of-N runs' own candidates (no new model call); star = best K per seed, chosen after the fact")
ax.legend(frameon=False, fontsize=8, loc="lower right")
save(fig, "fig6_stacking"); write_csv(FD / "fig6_stacking.csv", cur)

# ---------------------------------------------------------------- Fig 7: correctness matrix
cu = list(csv.DictReader(open(PM / "tables/correctness_unified.csv")))
objs = [r for r in cu if r["tested"] in ("yes",) ]
CONC = {r["object"]: r for r in csv.DictReader(open(PM / "tables/concurrency_patterns_by_patch.csv"))}
def conc_of(r):
    n = r["object"]; n = re.sub(r"s3-step\d+-gen(\d+)", r"s3-gen\1", n)
    return CONC.get(n)
cols = [("legal files differ", lambda r: ("n/a", NA) if r["corpus"].startswith("A") else (("yes", CRIT) if (fnum(r.get("legal_encoder_files_compared")) or 0) != (fnum(r.get("legal_encoder_files_identical")) or 0) else ("ok", GOOD))),
        ("4 originals differ", lambda r: ("yes", CRIT) if r.get("original4_compared") != r.get("original4_identical") else ("ok", GOOD)),
        ("mutants differ", lambda r: ("yes", SERIOUS) if r.get("mutants_compared") != r.get("mutants_identical") else ("ok", GOOD)),
        ("crash only in patch", lambda r: ("yes", CRIT) if (fnum(r.get("crash_patch_only")) or 0) > 0 else ("ok", GOOD)),
        ("ASan / UBSan new", lambda r: ("yes", CRIT) if (fnum(r.get("asan_errors")) or 0) > 0 or (fnum(r.get("ubsan_messages_not_in_stock")) or 0) > 0 else ("ok", GOOD)),
        ("code reading: unsynchronised shared state", lambda r: ("n/a", NA) if conc_of(r) is None else (("yes", WARN) if conc_of(r)["reading_says_unsafe"] == "True" else ("ok", GOOD))),
        ("TSan race", lambda r: ("yes", WARN) if (fnum(r.get("tsan_race_locations")) or 0) > 0 else ("ok", GOOD)),
        ("wrong output, 4 threads", lambda r: ("yes", CRIT) if (fnum(r.get("tsan_digest_mismatches")) or 0) > 0 else (("n/a", NA) if not str(r.get("tsan_digest_mismatches", "")).isdigit() else ("ok", GOOD)))]
fig, ax = plt.subplots(figsize=(8.6, 0.17 * len(objs) + 1.8))
for i, r in enumerate(objs):
    for j, (nm, fn) in enumerate(cols):
        t, c = fn(r); ax.add_patch(plt.Rectangle((j, -i - 1), .92, .84, color=c, alpha=.9 if t != "n/a" else .35, lw=0))
        ax.text(j + .46, -i - .58, {"yes": "!", "ok": "", "n/a": "-"}[t], ha="center", va="center", fontsize=6.5, color=INK if c == WARN else "white")
    ax.text(-.15, -i - .58, r["object"], ha="right", va="center", fontsize=6.5, color=INK2)
for j, (nm, _) in enumerate(cols): ax.text(j + .46, .2, nm, rotation=60, ha="left", va="bottom", fontsize=7.5, color=INK2)
ax.set_xlim(0, len(cols)); ax.set_ylim(-len(objs) - .3, 0); ax.axis("off")
fig.suptitle("Extended correctness, every tested object (green = no finding, grey = not applicable / not read; the code-reading column covers the 4 DeepSeek-final/chain families, rounds I2/I3 finals and the human patches)", x=.02, ha="left", y=1.005, fontsize=8, fontweight="bold")
save(fig, "fig7_correctness_matrix"); write_csv(FD / "fig7_correctness.csv", [{"object": r["object"], "findings": r["findings"]} for r in objs])

# ---------------------------------------------------------------- Fig 8: null search vs real steps
ns = list(csv.DictReader(open(PM / "figure_data/null_search_steps.csv"))); gr = list(csv.DictReader(open(PM / "tables/greedy_real_update_steps.csv")))
fig, ax = plt.subplots(figsize=(7.4, 3.0))
nv = [float(r["step_pct"]) for r in ns if r["updated"] == "True"]; gv = [float(r["step_pct"]) for r in gr]
rng = np.random.default_rng(1)
ax.scatter(nv, 1 + rng.uniform(-.12, .12, len(nv)), s=26, color=MUTED, label=f"no-op candidates, rank rule: {len(nv)} updates in 8 runs"); ax.scatter(gv, 0 + rng.uniform(-.12, .12, len(gv)), s=26, color=ORANGE, label=f"real DeepSeek greedy chains: {len(gv)} updates in 5 runs")
ax.axvline(max(nv), color=MUTED, lw=.9, ls=(0, (3, 3))); ax.text(max(nv) * 1.05, 1.42, f"largest noise-only step {max(nv):.3f}%", fontsize=7.5, color=MUTED)
ax.set_xscale("log"); ax.set_yticks([0, 1]); ax.set_yticklabels(["real chains", "no-op (noise only)"]); ax.set_xlabel("size of one record update: 100 x (1 - R_new / R_previous), %  (log scale)"); ax.set_ylim(-.5, 1.7)
ax.set_title("Updates produced by noise alone versus updates of real chains"); ax.xaxis.grid(True); ax.set_axisbelow(True); ax.legend(frameon=False, fontsize=7.5, loc="lower right")
save(fig, "fig8_null_search_steps"); write_csv(FD / "fig8_steps.csv", [{"kind": "null", "step_pct": v} for v in nv] + [{"kind": "real", "step_pct": v} for v in gv])

# ---------------------------------------------------------------- Fig 9: request funnel
fn = list(csv.DictReader(open(PM / "tables/request_funnel.csv"))) if (PM / "tables/request_funnel.csv").exists() else []
if fn:
    cats = [("http_or_no_code_or_truncated", "no usable reply (HTTP error, no code, truncated)", MUTED), ("unchanged", "replacement equals current text", AXIS), ("compile_fail", "compile or link failure", SERIOUS),
            ("check_fail", "failed the provided checks", CRIT), ("measured_not_confirmed", "measured, not confirmed faster than stock", BLUE),
            ("confirmed_inherited_or_not_better_than_parent", "confirmed vs stock but no better than its parent (mostly inherited gain)", "#6aa84f"), ("new_step_accepted", "new step accepted (better than its parent) / best-of-N: independent attempt confirmed", GOOD)]
    fig, ax = plt.subplots(figsize=(9.0, 4.4))
    for yi, r in enumerate(fn[::-1]):
        left = 0
        for key, lab, col in cats:
            v = float(r[key]); ax.barh(yi, v, left=left, color=col, edgecolor=SURF, linewidth=1.5, height=.62)
            if v >= 2: ax.text(left + v / 2, yi, f"{v:.0f}", ha="center", va="center", fontsize=7, color="white" if col not in (AXIS, WARN) else INK)
            left += v
    ax.set_yticks(range(len(fn))); ax.set_yticklabels([r["label"] for r in fn[::-1]], fontsize=8); ax.set_xlabel("what the 40 model requests (rows) turned into; median over 5 seeds per category"); ax.set_xlim(0, 44)
    ax.set_title("40 requests are not 40 optimisation attempts"); ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=c) for _, _, c in cats], labels=[l for _, l, _ in cats], frameon=False, fontsize=7.5, ncol=3, loc="upper center", bbox_to_anchor=(.45, -.14))
    save(fig, "fig9_request_funnel"); write_csv(FD / "fig9_funnel.csv", fn)
# ---------------------------------------------------------------- Fig 10: selection probabilities
rs = list(csv.DictReader(open(PM / "figure_data/region_expected_vs_observed.csv"))) if (PM / "figure_data/region_expected_vs_observed.csv").exists() else []
if rs:
    fig, ax = plt.subplots(figsize=(7.4, 3.9)); n = len(rs); w = .38
    ax.bar([i - w / 2 for i in range(n)], [float(r["expected_pct"]) for r in rs], w, color=BLUE, label="expected from the profile (0.9 x sample share + uniform part)")
    ax.bar([i + w / 2 for i in range(n)], [float(r["observed_pct"]) for r in rs], w, color=ORANGE, label="observed share of independent draws (10 runs pooled)")
    ax.set_xticks(range(n)); ax.set_xticklabels([r["function"].replace("::", "::\n") for r in rs], fontsize=7.5); ax.set_ylabel("% of independent draws")
    ax.set_title("Function selection: profile weight versus draws actually made (DeepSeek, code I3: population and best-of-N runs pooled)"); ax.legend(frameon=False, fontsize=7.5); ax.yaxis.grid(True); ax.set_axisbelow(True)
    save(fig, "fig10_function_selection"); write_csv(FD / "fig10_selection.csv", rs)
print("figures:", sorted(p.name for p in FIG.glob("*.png")))
