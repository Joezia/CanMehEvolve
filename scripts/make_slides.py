#!/usr/bin/env python3
"""Build talk/talk.pptx (5 slides, speaker notes included) from the frozen exports.
Needs python-pptx (not part of the project build): PYTHONPATH=$HOME/.pylib-deliver python3 scripts/make_slides.py
"""
import json, statistics as st
from pathlib import Path
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parent.parent
D = json.load(open(ROOT / "runs/phase1-final/phase1_final.json"))
runs = [r for r in D["runs"] if r["experiment"] == "deepseek"]
cb = D["common_budget_34"]
S = D["stats"]
BLUE, ORANGE, INK, MUTED, LIGHT = RGBColor(0x00, 0x72, 0xB2), RGBColor(0xD5, 0x5E, 0x00), RGBColor(0x22, 0x22, 0x22), RGBColor(0x66, 0x66, 0x66), RGBColor(0xF2, 0xF4, 0xF7)

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
blank = prs.slide_layouts[6]


def text(slide, x, y, w, h, paras, size=20, bold=False, color=INK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    for i, p in enumerate(paras if isinstance(paras, list) else [paras]):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        if isinstance(p, tuple):
            p, kw = p
        else:
            kw = {}
        run = para.add_run()
        run.text = p
        run.font.size = Pt(kw.get("size", size))
        run.font.bold = kw.get("bold", bold)
        run.font.color.rgb = kw.get("color", color)
        run.font.name = "Calibri"
        para.alignment = align
        para.space_after = Pt(kw.get("after", 6))
    return tb


def title(slide, t, sub=None):
    text(slide, 0.6, 0.35, 12.1, 0.9, t, size=32, bold=True)
    if sub:
        text(slide, 0.6, 1.15, 12.1, 0.5, sub, size=16, color=MUTED)


def box(slide, x, y, w, h, label, fill, fg=RGBColor(255, 255, 255), size=15, bold=True):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    s.line.fill.background()
    tf = s.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = label
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = fg
    r.font.name = "Calibri"
    return s


def arrow(slide, x1, y1, x2, y2):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = MUTED
    c.line.width = Pt(2)
    ln = c.line._get_or_add_ln()
    from lxml import etree
    tail = etree.SubElement(ln, "{http://schemas.openxmlformats.org/drawingml/2006/main}tailEnd")
    tail.set("type", "triangle")


def notes(slide, t):
    slide.notes_slide.notes_text_frame.text = t


def med(vals):
    return st.median(vals)


g = [r for r in runs if r["arm"] == "greedy"]
b = [r for r in runs if r["arm"] == "bestofn"]
g34 = [c for c in cb if c["arm"] == "greedy"]
b34 = [c for c in cb if c["arm"] == "bestofn"]
gs = [r["best_confirmed_speedup"] for r in g]
bs = [r["best_confirmed_speedup"] for r in b]
ctl = {c["control"]: c for c in D["controls"]}
O3 = ctl["C1 -O3 vs -O2 (batch 1071478)"]["median_speedup"]
O3N = ctl["C1 -O3 -march=native vs -O2 (rerun 1071478)"]["median_speedup"]

# 1 ----------------------------------------------------------------------------------------------------------------------------
s = prs.slides.add_slide(blank)
title(s, "Does an LLM search make the Garmin FIT decoder faster?", "…and is it more than repeated sampling?   CS6219 project · FIT SDK 21.201.0 · one model, five seeds")
text(s, 0.6, 1.9, 6.2, 4.6, [("Question", {"bold": True, "size": 22, "color": BLUE}),
                              "Does LLM-guided patch search speed up full file decode, and does keeping the best patch beat sampling the model N times with no memory?",
                              ("What we measure", {"bold": True, "size": 22, "color": BLUE}),
                              "Full decode of four FIT files, about 358 ms in the stock -O2 build. Every candidate is a diff; ratio = candidate / stock.",
                              ], size=19)
text(s, 7.2, 1.9, 5.5, 4.6, [("Two arms, same model and budget", {"bold": True, "size": 22, "color": BLUE}),
                              ("Greedy: one chain, each call edits the current best patch", {"color": BLUE, "bold": True}),
                              ("Best-of-N: every call starts from stock, no memory", {"color": ORANGE, "bold": True}),
                              ("References", {"bold": True, "size": 22, "color": BLUE}),
                              "C1 compiler flags (-O3, -O3 -march=native) · C2 two human patches · inert patch",
                              "40 HTTP requests per run · 5 seeds per arm · all results reported",
                              ], size=19)
notes(s, "(About 45 s.) Papers say an LLM in a search loop finds faster systems code. The missing control is the same number of model calls with no feedback and no selection. "
         "We test that on one real library: the Garmin FIT SDK decoder, measured as a full decode of four files. Every candidate is a unified diff against stock, so a result is a patch someone can review. "
         "We compare a greedy chain, which keeps and builds on its best patch, with best-of-N, which starts from stock every time. Same model, same prompt, same budget of 40 requests, five seeds each. "
         "Compiler flags and two human patches are the non-LLM references. I report every seed.")

# 2 ----------------------------------------------------------------------------------------------------------------------------
s = prs.slides.add_slide(blank)
title(s, "One call, two ways to use it", "Same sampling of functions, same prompt, same measurement; only the starting text differs")
box(s, 0.6, 1.9, 2.4, 1.0, "pick a function\n(perf-weighted 90%, uniform 10%)", MUTED, size=14)
box(s, 3.4, 1.9, 2.4, 1.0, "show model its text\n+ stock decode time", MUTED, size=14)
box(s, 6.2, 1.9, 2.4, 1.0, "model returns\na faster body", MUTED, size=14)
box(s, 9.0, 1.9, 3.7, 1.0, "splice → compile → output checksum\n→ measure (10 processes × 9)", MUTED, size=14)
for x in (3.0, 5.8, 8.6):
    arrow(s, x, 2.4, x + 0.4, 2.4)
box(s, 0.6, 3.5, 5.9, 1.3, "GREEDY: text comes from the current best patch.\nAccept if the rank value R beats the record; the chain continues from it.", BLUE, size=15)
box(s, 6.8, 3.5, 5.9, 1.3, "BEST-OF-N: text is always stock.\nNo score, patch or error is ever shown; keep the best by the same R.", ORANGE, size=15)
text(s, 0.6, 5.1, 12.1, 1.9, ["Rank value: measure once; if below the record and stable, measure again; R = max of the two; update only if R < record.",
                              "This is an ordering heuristic, not a significance test. The fixed final patch is then re-measured 3 more times under the frozen rule.",
                              "Budget: 40 HTTP requests (truncated replies and 502s count). A reply cut at 32,768 tokens is never a candidate."], size=16, color=INK)
notes(s, "(About 60 s.) Each call: pick one function, weighting by perf samples from a 20-second profile with ten percent uniform draws. Show the model that function's text and the stock decode time. "
         "It returns a replacement body. We splice it in, compile, check the decoded output checksum, and time it against stock: ten fresh processes, nine repetitions each. "
         "The only difference between the arms is the text shown. Greedy shows the function as it is under the current best patch, so earlier edits are inherited. "
         "Best-of-N always shows stock and never sees scores or errors. Both rank candidates the same way: measure, re-measure if it might beat the record, take the worse of the two. "
         "That orders candidates; it is not a significance test. The final patch is re-measured three more times independently. Every request counts against the budget of 40, including truncated replies and server errors.")

# 3 ----------------------------------------------------------------------------------------------------------------------------
s = prs.slides.add_slide(blank)
title(s, "Can we trust a timing? Phase 0 calibration", "Synthetic pairs with a known true ratio, 100 trials each; one measurement = 10 processes × 9 repetitions")
rows = [["true change", "judged faster", "95% CI"], ["0% (null)", "0 / 100", "[0.0, 3.6]%"], ["1.0% faster", "1 / 100", "[0.03, 5.4]%"],
        ["1.965% faster", "42 / 100", "[32.2, 52.3]%"], ["4.8% faster", "99 / 100", "[94.6, 100]%"], ["9.1% faster", "100 / 100", "[96.4, 100]%"], ["10% slower", "0 / 100", "[0.0, 3.6]%"]]
tbl = s.shapes.add_table(len(rows), 3, Inches(0.6), Inches(1.9), Inches(6.4), Inches(3.6)).table
for i, r in enumerate(rows):
    for j, v in enumerate(r):
        c = tbl.cell(i, j)
        c.text = v
        for p in c.text_frame.paragraphs:
            for run in p.runs:
                run.font.size = Pt(16)
                run.font.bold = i == 0
                run.font.name = "Calibri"
text(s, 7.4, 1.9, 5.4, 4.8, [("Frozen rule", {"bold": True, "size": 20, "color": BLUE}),
                              "faster = mean log ratio < 0, sign-flip p < 0.01, ratio ≤ 0.98",
                              ("What it shows", {"bold": True, "size": 20, "color": BLUE}),
                              "Weakest effect found in ≥ 90% of trials: about 5%. The 2% gate sits just above a 1.965% change, hence 42%.",
                              ("What it does not show", {"bold": True, "size": 20, "color": BLUE}),
                              "0/100 bounds false accepts at about 3.6%; α = 1% is a threshold, not an observed rate. The SDK showed signs of correlated repetitions the loop does not have.",
                              ], size=16)
notes(s, "(About 60 s.) Before trusting any speedup we calibrated the instrument on pairs where we know the true ratio. One measurement runs the stock and candidate in the same process, alternating order, ten processes by nine repetitions. "
         "The rule says faster if the ratio is below 0.98 and an exact sign-flip test gives p under one percent. The rule and thresholds were fixed before any calibration data. "
         "On 100 null trials nothing was accepted, but that only bounds the false-accept rate by about 3.6 percent. Changes of about 5 percent were found 99 times in 100; the 2 percent pair, whose true change is 1.965 percent and so sits just under the gate, was accepted 42 times. "
         "So the instrument is reliable near 5 percent and above, and that does not carry over unconditionally to every SDK patch: six SDK measurements of an inert patch showed positive autocorrelation.")

# 4 ----------------------------------------------------------------------------------------------------------------------------
s = prs.slides.add_slide(blank)
title(s, "Results: five seeds, nothing dropped")
s.shapes.add_picture(str(ROOT / "report/main_figure.png"), Inches(1.15), Inches(1.15), width=Inches(11.0))
text(s, 0.6, 5.85, 12.1, 1.5, [
    "Full runs, median [range]:  greedy %.3f [%.3f, %.3f]  ·  best-of-N %.3f [%.3f, %.3f]  ·  -O3 %.3f  ·  -O3 -march=native %.3f" % (
        med(gs), min(gs), max(gs), med(bs), min(bs), max(bs), O3, O3N),
    "Greedy higher in 5/5 seeds; permutation p = %.3f, Mann–Whitney p = %.3f (5 seeds: coarse). Greedy used more tokens, but gains more per token (4/5 seeds)." % (
        S["DeepSeek|full|best_confirmed_speedup"]["perm_median_p"], S["DeepSeek|full|best_confirmed_speedup"]["mw_exact_p"]),
    "Panel B is post hoc (first 34 requests; greedy seeds 3–5 stopped at 38/34/34 at the deadline). Same direction."], size=14)
notes(s, "(About 80 s.) Here are all ten runs. Each marker is a seed; the speedup is the median of three independent re-measurements of that run's fixed final patch, and every one passed the rule. "
         "Greedy has a median of 1.169, range 1.157 to 1.216. Best-of-N has 1.073, range 1.067 to 1.074. Greedy is higher in all five paired seeds. "
         "The primary permutation test on the median difference gives p about 0.048 and the Mann-Whitney test 0.008; with five seeds I treat these as coarse. "
         "For reference, -O3 gives 1.09 and -O3 with march native 1.11, measured in a separate batch: every greedy seed beats both, and best-of-N is below -O3. "
         "Panel B is post hoc: three greedy runs stopped at the deadline after 38, 34 and 34 requests, so we also compare each run's best patch within the first 34 requests, re-measured. Same picture. "
         "Panel C is the course metric, speedup minus one per token: greedy spends more tokens but its median is still higher, 3.6 versus 2.2 times ten to the minus seven.")

# 5 ----------------------------------------------------------------------------------------------------------------------------
s = prs.slides.add_slide(blank)
title(s, "What we can and cannot claim")
text(s, 0.6, 1.4, 6.0, 5.6, [("Supported", {"bold": True, "size": 24, "color": BLUE}),
                              "Both arms beat stock; every fixed patch passed the frozen rule 3/3.",
                              "Greedy beat best-of-N in all 5 seeds, in both budget views.",
                              "All best-of-N winners are one function (Profile::GetMesg → table lookup); greedy chains kept it and stacked 4–10 more accepted edits.",
                              "Only greedy exceeded -O3 -march=native."], size=19)
text(s, 6.9, 1.4, 6.0, 5.6, [("Limits", {"bold": True, "size": 24, "color": ORANGE}),
                              "5 seeds, 1 model, 1 library; the arms differ in several ways, so no single cause (selection, feedback, inheritance) is isolated.",
                              "Greedy used 38 / 34 / 34 requests in 3 runs (job time limit); the 34-request view is post hoc.",
                              "Many accepted steps are < 0.3%: noise. Only final patches were independently re-measured.",
                              "Correctness = output checksum only; some edits use unsynchronised static caches. Not upstream-ready.",
                              "Two node families; calibration is synthetic and only reliable near 5%."], size=19)
notes(s, "(About 55 s.) What the data support: both arms beat stock, and greedy beat best-of-N in all five seeds, in the full runs and in the 34-request view. "
         "Every best-of-N winner is the same one-function change, a lookup table in Profile GetMesg; the greedy chains kept it and added four to ten more accepted edits, and only greedy went past -O3 with march native. "
         "What we cannot say: five seeds and one model do not isolate selection, feedback or inheritance, since the arms differ in several ways and we ran no ablation. "
         "Three greedy runs did not reach 40 requests because of the three-hour job limit, and the 34-request analysis was added after seeing results. "
         "Many accepted steps are under 0.3 percent, which is noise; only the final patches were re-measured independently. "
         "Correctness checking is only the output checksum, and some edits use unsynchronised static caches, so none is upstream-ready without review. Thank you; questions.")

out = ROOT / "talk/talk.pptx"
out.parent.mkdir(parents=True, exist_ok=True)
prs.save(str(out))
print(out)
