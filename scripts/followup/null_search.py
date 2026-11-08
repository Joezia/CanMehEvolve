#!/usr/bin/env python3
"""Follow-up 3: "null search" -- the greedy rank rule applied to candidates that cannot change the code.

Phase 0 calibrated the FINAL decision rule, not the greedy ranking heuristic (measure once; if r1 < record and stable measure again;
R = max(r1, r2); update when R < record, no 2% gate, no significance).  With candidates whose true ratio is exactly 1.000 any update is noise.
This script runs that loop with the model replaced by a no-op edit (a comment inserted before the closing brace of a randomly drawn function), so
the compiled code is unchanged.  It reports how often the loop "accepts" and how far the record drifts below 1.0 from noise alone, which is what
the early small steps of a real greedy chain should be compared with.

It reuses the project's own pieces: `CanMehHarness show/splice/measure-patch --no-decision` and `CanMehSearch --rule-eval` (the frozen analysis);
only the loop bookkeeping is re-implemented, following src/Search.cpp (the rank branch).  No model is called.
usage: null_search.py --work W --out OUT --seed S [--steps 40] [--deadline 9000]
"""
import argparse, json, random, subprocess, sys, time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--seed", type=int, required=True)
ap.add_argument("--steps", type=int, default=40)
ap.add_argument("--deadline", type=float, default=9000.0)
ap.add_argument("--harness", default="build/CanMehHarness")
ap.add_argument("--search", default="build/CanMehSearch")
ap.add_argument("--max-lines", type=int, default=250)
a = ap.parse_args()
OUT = Path(a.out)
for d in ("patches", "measurements"):
    (OUT / d).mkdir(parents=True, exist_ok=True)
t0 = time.time()
rng = random.Random(a.seed)


def harness(*args, timeout=1800):
    r = subprocess.run([a.harness, *args], capture_output=True, text=True, timeout=timeout)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"ok": False, "stage": "unparsable", "error": (r.stderr or r.stdout)[:300]}


def analyse(raw_path):
    r = subprocess.run([a.search, "--rule-eval", str(raw_path)], capture_output=True, text=True)
    line = [l for l in r.stdout.splitlines() if l.strip().startswith("{")]
    return json.loads(line[0]) if line else {"valid": False, "error": r.stderr[:200]}


def measure(patch, tag):
    m = harness("measure-patch", "--work", a.work, "--no-decision", "--patch", str(patch), timeout=1800)
    raw = OUT / "measurements" / (tag + ".json")
    raw.write_text(json.dumps(m))
    if not m.get("ok"):
        return None, m
    an = analyse(raw)
    return (an if an.get("valid") else None), m


regions = harness("regions", "--work", a.work, "--max-lines", str(a.max_lines))["regions"]
log = open(OUT / "steps.jsonl", "a")
record, parent, updates, measured, attempts = 1.0, None, 0, 0, 0
measurements_all = []
while measured < a.steps and attempts < 3 * a.steps and time.time() - t0 < a.deadline:
    attempts += 1
    reg = rng.choice(regions)
    step = measured + 1
    rec = {"attempt": attempts, "step": step, "region": reg["id"], "label": reg["label"], "record_before": record, "t": round(time.time() - t0, 1)}
    sa = ["show", "--work", a.work, "--region", str(reg["id"]), "--max-lines", str(a.max_lines)] + (["--patch", str(parent)] if parent else [])
    shown = harness(*sa, timeout=300)
    if not shown.get("ok"):
        rec.update(stage="show", error=str(shown.get("error"))[:200]); log.write(json.dumps(rec) + "\n"); log.flush(); continue
    text = shown["text"]
    k = text.rfind("}")
    if k < 0:
        rec.update(stage="no-brace"); log.write(json.dumps(rec) + "\n"); log.flush(); continue
    new = text[:k] + "// noop-%d-%d\n" % (a.seed, attempts) + text[k:]
    repl = OUT / "patches" / ("a%03d.cpp" % attempts)
    repl.write_text(new)
    patch = OUT / "patches" / ("a%03d.patch" % attempts)
    spl = harness("splice", "--work", a.work, "--region", str(reg["id"]), "--max-lines", str(a.max_lines), "--replacement", str(repl), "--out", str(patch),
                  *(["--patch", str(parent)] if parent else []), timeout=300)
    if not spl.get("ok") or not patch.exists():
        rec.update(stage="splice", error=str(spl.get("error"))[:200]); log.write(json.dumps(rec) + "\n"); log.flush(); continue
    a1, m1 = measure(patch, "a%03d.m1" % attempts)
    if a1 is None:
        rec.update(stage=str(m1.get("stage", "measure")), error=str(m1.get("error"))[:200]); log.write(json.dumps(rec) + "\n"); log.flush(); continue
    measured += 1
    possibly = (not a1["unstable"]) and a1["ratio"] < record
    a2 = None
    if possibly:
        a2, _ = measure(patch, "a%03d.m2" % attempts)
    second_ok = possibly and a2 is not None
    R, updated, reason = a1["ratio"], False, ""
    if not possibly:
        reason = "first_measurement_unstable" if a1["unstable"] else "first_ratio_not_below_record"
    elif not second_ok:
        reason = "second_measurement_failed"
    elif a2["unstable"]:
        reason = "second_measurement_unstable"
    else:
        R = max(a1["ratio"], a2["ratio"])
        if R < record:
            updated, reason = True, "R_below_record"
        else:
            reason = "R_not_below_record"
    rec.update(stage="measured", measured_index=measured, ratio_1=a1["ratio"], p_1=a1["p_value"], faster_1=a1["faster"], unstable_1=a1["unstable"],
               ratio_2=(a2["ratio"] if a2 else None), p_2=(a2["p_value"] if a2 else None), faster_2=(a2["faster"] if a2 else None), unstable_2=(a2["unstable"] if a2 else None),
               R=R, updated=updated, reason=reason)
    measurements_all += [a1] + ([a2] if a2 else [])
    if updated:
        updates += 1
        record, parent = R, patch
        rec["record_after"] = record
    log.write(json.dumps(rec) + "\n"); log.flush()
    print("[step %d] region %s ratio=%.5f%s record=%.5f updates=%d" % (measured, reg["label"], a1["ratio"], " r2=%.5f" % a2["ratio"] if a2 else "", record, updates), flush=True)

summary = {"seed": a.seed, "steps_measured": measured, "attempts": attempts, "updates": updates, "final_record": record, "final_record_speedup": 1.0 / record,
           "measurements": len(measurements_all), "rule_faster_count": sum(1 for x in measurements_all if x["faster"]), "elapsed_s": round(time.time() - t0, 1),
           "ended_because": "steps" if measured >= a.steps else ("deadline" if time.time() - t0 >= a.deadline else "attempt cap")}
(OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary))
