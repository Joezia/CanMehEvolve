#!/usr/bin/env python3
"""Unified extended-correctness table. Two test generations are reported side by side (they are different test scales, not different stories):
  corpus A (earlier objects): 4 standard files + 400 mutants (CRC fixed; NOT legal files); ASan/UBSan on 71 files; TSan 4 threads on 12 files.
  corpus B (current objects): corpus A + 55 legal files written by the SDK encoder; differential on all 459; ASan/UBSan on 126; TSan 4 threads on 24; per-file handling (plain build) on 459.
Everything is recomputed from the raw outputs (raw.jsonl per file, *.err of the sanitizer runs); nothing is run here. Objects that were never tested are listed as 'not tested'."""
import sys, re, collections; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from pm_lib import *

F = ROOT / "runs/followup"; C2 = ROOT / "runs/round2/correctness"
idxB = {r["id"]: r["kind"] for r in jload(C2 / "DIFF0-1096972/index.json")}
idxA = {r["id"]: r["kind"] for r in jload(F / "correctness-sanitize-1088521/corpus_index.json")} if jload(F / "correctness-sanitize-1088521/corpus_index.json") else {}
same_prefix = all(idxA.get(i) == idxB.get(i) for i in range(404)) if idxA else None

def read_raw(rawp, idx):
    rows = jl(rawp)
    done = {r["i"]: r for r in rows if "ref" in r}; crash = {r["i"]: r for r in rows if "crash" in r}
    def cnt(kinds_valid):
        comp = [i for i in done if (idx[i] == "valid") == kinds_valid]
        ident = [i for i in comp if done[i]["ref"] == done[i]["cand"]]
        return len(comp), len(ident)
    orig = [i for i in done if idx[i] == "original"]
    leg = [i for i in done if idx[i] == "valid"]
    mut = [i for i in done if idx[i] not in ("original", "valid")]
    f = lambda L: (len(L), sum(1 for i in L if done[i]["ref"] == done[i]["cand"]))
    both = sum(1 for c in crash.values() if c["crash"] == "both"); co = sum(1 for c in crash.values() if c["crash"] == "cand_only"); so = sum(1 for c in crash.values() if c["crash"] == "stock_only")
    return {"orig": f(orig), "legal": f(leg), "mut": f(mut), "crash_both": both, "crash_patch_only": co, "crash_stock_only": so,
            "legal_crash": sum(1 for i, c in crash.items() if idx[i] in ("valid", "original"))}

def norm(txt):
    return {m.group(1) + " " + re.sub(r"-?\d+", "N", m.group(2)) for m in re.finditer(r"(src/[\w./]+):\d+:\d+: runtime error: (.*)", txt)}
def races(txt):
    return sorted(set(re.findall(r"SUMMARY: ThreadSanitizer: .*? (?:\S*/)?(src/[\w./]+:\d+)", txt)))

def err(dirs, name, cfg):
    for d in dirs:
        p = d / f"{name}-{cfg}.err"
        if p.exists(): return p.read_text(errors="replace")
    return None

sanA = [F / "correctness-sanitize-1088521", F / "correctness-sanitize-human-1091677"]
sanB = sorted(C2.glob("SAN-*"))[::-1]
sumA, sumB = {}, {}
for d in sanA: sumA.update(jload(d / "summary.json", {}) or {})
for d in sorted(C2.glob("SAN-*")): sumB.update(jload(d / "summary.json", {}) or {})
stock_ub = norm(err(sanA, "stock", "asan") or "")
rows = []

def sanitizer_cols(summary, dirs, name, scale):
    a, t = summary.get(name + "|asan"), summary.get(name + "|tsan")
    d = {}
    if a is not None:
        txt = err(dirs, name, "asan") or ""
        newub = norm(txt) - stock_ub
        d.update({"asan_ubsan_subset_files": scale[0], "asan_run_completed": a.get("files", 0) > 0 and a.get("returncode") == 0, "asan_errors": a.get("asan_errors"),
                  "ubsan_messages_not_in_stock": len(newub), "stock_own_ubsan_message_still_present": bool(stock_ub <= norm(txt)) if a.get("files", 0) else "unknown (run aborted)",
                  "asan_digest_differences": a.get("digest_differences_vs_stock") if a.get("files", 0) else "not compared (run aborted)"})
    if t is not None:
        txt = err(dirs, name, "tsan") or ""
        mm = re.search(r"digest_mismatches (\d+)", t.get("output", "") or "")
        d.update({"tsan_subset_files": scale[1], "tsan_threads": 4, "tsan_race_locations": len(races(txt)), "tsan_returncode": t.get("returncode"),
                  "tsan_digest_mismatches": int(mm.group(1)) if mm else "no digest line (run did not finish)", "tsan_comparisons": scale[1] * 4 if mm else ""})
    return d

# --- corpus A objects
diffA = {}
for f in sorted(F.glob("correctness-diff-*/summary.json")):
    diffA.update(jload(f, {}))
rawA = {}
for p in sorted(F.glob("correctness-diff-*/*/raw.jsonl")):
    rawA[p.parent.name] = p
groupA = lambda n: ("human patch (C2)" if n.startswith("human") else "DeepSeek best-of-N final (rank rule)" if "bestofn" in n else "DeepSeek greedy final" if n.startswith("final-greedy") else "greedy chain step (seed 3)")
for n in sorted(diffA):
    r = read_raw(rawA[n], idxB) if n in rawA else None
    row = {"object": n, "group": groupA(n), "corpus": "A (4 originals + 400 mutants)", "tested": "yes"}
    if r:
        row.update({"original4_compared": r["orig"][0], "original4_identical": r["orig"][1], "legal_encoder_files_compared": "n/a (not in corpus A)", "mutants_compared": r["mut"][0], "mutants_identical": r["mut"][1],
                    "crash_both_same_input": r["crash_both"], "crash_patch_only": r["crash_patch_only"], "crash_stock_only": r["crash_stock_only"]})
    row.update(sanitizer_cols(sumA, sanA, n, (71, 12)))
    rows.append(row)
# --- corpus B objects
diffB = {}
for f in sorted(C2.glob("DIFF*/summary.json")):
    diffB.update(jload(f, {}))
rawB = {p.parent.name: p for p in sorted(C2.glob("DIFF*/*/raw.jsonl"))}
plainstock = None
def plain_load(name):
    for d in sorted(C2.glob("SAN-*"))[::-1]:
        p = d / f"{name}-plain.out"
        if p.exists():
            o = {}
            for l in open(p, errors="replace"):
                m = re.search(r"/(\d{4})/x\.fit (\d) (\d+) ?(.*)", l)
                if m: o[int(m.group(1))] = (m.group(2), m.group(3), re.sub(r"\d+", "N", m.group(4)))
            return o
    return {}
plainstock = plain_load("stock")
for n in sorted(diffB):
    r = read_raw(rawB[n], idxB)
    grp = "round-2 final: " + ("DeepSeek" if "-ds-" in n else "Qwen") + (" population" if "population" in n else " best-of-N") if n.startswith("r2-") else "stack of best-of-N candidates (" + ("post-hoc best K" if "bestK" in n else "fixed K") + ")"
    pc = plain_load(n)
    pdiff = [k for k in plainstock if pc.get(k) != plainstock[k]] if pc and plainstock else None
    row = {"object": n, "group": grp, "corpus": "B (+55 legal encoder files)", "tested": "yes", "original4_compared": r["orig"][0], "original4_identical": r["orig"][1],
           "legal_encoder_files_compared": r["legal"][0], "legal_encoder_files_identical": r["legal"][1], "mutants_compared": r["mut"][0], "mutants_identical": r["mut"][1],
           "crash_both_same_input": r["crash_both"], "crash_patch_only": r["crash_patch_only"], "crash_stock_only": r["crash_stock_only"],
           "plain_per_file_handling_differs": len(pdiff) if pdiff is not None else "", "plain_newly_killed_by_signal": sum(1 for k in pdiff if pc[k][0] == "3" and plainstock[k][0] != "3") if pdiff is not None else ""}
    row.update(sanitizer_cols(sumB, sanB, n, (126, 24)))
    rows.append(row)
# --- baseline and untested objects
sa, ta = sumA.get("stock|asan"), sumA.get("stock|tsan")
rows.append({"object": "stock (SDK 21.201.0)", "group": "baseline", "corpus": "A and B", "tested": "reference", "asan_errors": sa.get("asan_errors") if sa else "", "ubsan_messages_not_in_stock": 0,
             "asan_ubsan_subset_files": "71 (A) / 126 (B)", "tsan_race_locations": len(races(err(sanA, "stock", "tsan") or "")), "tsan_returncode": ta.get("returncode") if ta else "",
             "note": "stock has %d own UBSan message(s): %s" % (len(stock_ub), "; ".join(sorted(stock_ub)))})
for s in range(1, 6):
    for arm in ("search", "bestofn"):
        rows.append({"object": f"qwen3-coder-next {arm} seed {s} final patch (original implementation I1)", "group": "Qwen final (I1)", "corpus": "-", "tested": "NOT TESTED"})
rows.append({"object": "ds_greedy_I2 seed 3 final patch at 40 requests (generation 39)", "group": "DeepSeek greedy final", "corpus": "-", "tested": "NOT TESTED (the tested 'final-greedy-seed3' is the 38-request state, generation 37)"})
write_csv(PM / "tables/correctness_unified.csv", rows)

# ---- flags and summary
def flag(r):
    f = []
    if r.get("tested") != "yes": return None
    if r.get("original4_identical") != r.get("original4_compared"): f.append("output differs on an original file")
    if isinstance(r.get("legal_encoder_files_identical"), int) and r["legal_encoder_files_identical"] != r["legal_encoder_files_compared"]: f.append("output differs on %d legal encoder file(s)" % (r["legal_encoder_files_compared"] - r["legal_encoder_files_identical"]))
    if r.get("mutants_identical") != r.get("mutants_compared"): f.append("output differs on %d mutant(s)" % (r["mutants_compared"] - r["mutants_identical"]))
    if r.get("crash_patch_only"): f.append("crashes where stock does not on %d mutant(s)" % r["crash_patch_only"])
    if r.get("asan_errors"): f.append("ASan error")
    if r.get("ubsan_messages_not_in_stock"): f.append("%s new UBSan message(s)" % r["ubsan_messages_not_in_stock"])
    if r.get("tsan_race_locations"): f.append("TSan race (%s locations)" % r["tsan_race_locations"])
    if isinstance(r.get("tsan_digest_mismatches"), int) and r["tsan_digest_mismatches"] > 0: f.append("%d concurrent digest mismatch(es)" % r["tsan_digest_mismatches"])
    if r.get("asan_run_completed") is False: f.append("ASan run aborted")
    if r.get("tsan_digest_mismatches", "").__class__ is str and r.get("tsan_returncode") not in (0, None): f.append("TSan run did not complete")
    return f
for r in rows:
    fl = flag(r)
    r["findings"] = "; ".join(fl) if fl else ("" if fl is None else "none in the tested conditions")
write_csv(PM / "tables/correctness_unified.csv", rows)
# stock classification of the 404-file corpus
cls = list(csv.DictReader(open(C2 / "stock-classification-1094785/classification.csv")))
m = [x for x in cls if int(x["id"]) < 404]
cnt = collections.Counter(); cnt_kind = collections.Counter()
for x in m:
    o = x["outcome"]
    if o == "decoded": key = "decoded"
    else:
        det = re.sub(r"\d+", "N", re.sub(r"[^\x20-\x7e]", "?", x["detail"] or o))
        key = ("uncaught C++ exception: " + det) if o.startswith("uncaught") else o.replace("signal 11", "signal N")
        key = re.sub(r"Error at byte: N", "(at byte N)", key); key = re.sub(r"Architecture \S not supported", "Architecture <byte> not supported", key)
    cnt[key] += 1; cnt_kind[(x["kind"], "decoded" if o == "decoded" else "not decoded")] += 1
write_csv(PM / "tables/stock_classification_404.csv", [{"outcome": k, "files": v} for k, v in cnt.most_common()])
write_csv(PM / "tables/stock_classification_404_by_kind.csv", [{"kind": k[0], "outcome": k[1], "files": v} for k, v in sorted(cnt_kind.items())])
meta = {"corpusA_prefix_identical_to_corpusB_first404": same_prefix, "stock_files_not_decoded_of_404": sum(1 for x in m if x["outcome"] != "decoded"),
        "uncaught_exceptions": sum(1 for x in m if x["outcome"].startswith("uncaught")), "killed_by_signal": sum(1 for x in m if x["outcome"].startswith("killed")),
        "stock_files_with_asan_error": sum(1 for x in m if x["asan_error"] not in ("0", "")), "stock_files_with_ubsan_msg": sum(1 for x in m if x["ubsan_messages"] not in ("0", "")),
        "stock_own_ubsan_in_sanitizer_subset": sorted(stock_ub)}
json.dump(meta, open(PM / "tables/stock_classification_meta.json", "w"), indent=1)
src("corr-1", "unified extended-correctness table", "runs/followup/correctness-*, runs/round2/correctness/{DIFF*,SAN*,stock-classification-*}", "raw.jsonl, *.err, summary.json, classification.csv", "see build_correctness.py")
if __name__ == "__main__":
    print(meta)
    for r in rows:
        print(f"{r['object'][:44]:44s} {r.get('tested','')[:10]:10s} | {r.get('findings','')}")
