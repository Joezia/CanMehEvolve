#!/usr/bin/env python3
"""Static reading of every final patch for shared mutable state, then cross-tabulated with what ThreadSanitizer actually observed.
Patterns (regexes over the patch's added lines; matched lines are stored in the CSV so each classification can be checked by eye):
  magic_static   : function-local static initialised by a lambda / const object -> C++11 guarantees thread-safe one-time initialisation
  plain_flag     : `static bool initialized = false;` + manual lazy build -> data race if two threads make the first call
  mutable_cache  : static variables overwritten on later calls (e.g. cached message pointer / field index) -> races in steady state and wrong values
  none           : no function-local static state added"""
import sys, re, glob; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from pm_lib import *

def classify(path):
    t = Path(path).read_text(errors="replace")
    add = [l[1:] for l in t.splitlines() if l.startswith("+") and not l.startswith("+++")]
    st = [l.strip() for l in add if re.search(r"\bstatic\b", l) and not re.search(r"static_cast|static_assert|\bstatic (inline|constexpr) (\w+ )?\w+\(", l)]
    pats = set()
    for l in st:
        if re.search(r"static\s+(const\s+)?(bool|FIT_BOOL|int|FIT_UINT\d+)\s+\w*(init|ready|built|valid|done)\w*\s*(=\s*(false|0|FIT_FALSE))?\s*;", l, re.I):
            pats.add("plain_flag")
        elif re.search(r"static\s+(const\s+)?(auto|bool|std::array<[^>]*>|\w+)\s+\w+\s*=\s*(\[|\w+\()?.*\[", l) or re.search(r"static\s+const\s+\w+\s+\w+;\s*$", l) or re.search(r"=\s*\[\]|\[&?\]\s*\(|=\s*\[\s*\w*\s*\]\s*\(", l):
            pats.add("magic_static")
        if re.search(r"cached|cache", l, re.I):
            pats.add("mutable_cache")
        if re.search(r"static\s+(const\s+)?\w+\s*\*?\s*\w*(lookup|table|sorted|cache)\w*(\[[^\]]*\])*\s*(=\s*\{\s*\})?;", l, re.I) and not re.search(r"const\s+auto|=\s*\[", l):
            pats.add("lookup_storage")
    return st, pats

items = []
for p in sorted(glob.glob(str(ROOT / "experiments/patches/final-cumulative/*.patch"))):
    n = Path(p).name.split(".")[0]; items.append(("final-" + n if n.startswith(("greedy", "bestofn")) else n, p, "I2 final (earlier objects)"))
for u in range(1, 14):
    pass
d3 = [d for d in (ROOT / "runs/deepseek").glob("greedy-s3-[0-9]*") if "resume" not in d.name][0]
for s in jload(d3 / "summary.json")["rank_updates"]:
    items.append((f"s3-gen{s['generation']}", str(d3 / "patches" / f"gen_{s['generation']}.patch"), "I2 chain step (seed 3, cumulative patch)"))
rs = ROOT / "runs/followup/resume-greedy-s3-1088410"
if (rs / "best.patch").exists(): items.append(("s3-gen39 (40-request final)", str(rs / "best.patch"), "I2 final at 40 requests (untested by sanitizers)"))
for d in sorted((ROOT / "runs/round2/runs").glob("*")): items.append(("r2-" + d.name, str(d / "best.patch"), "I3 final"))
for d in sorted((ROOT / "runs/main").glob("*")):
    if (d / "best.patch").exists(): items.append(("I1-" + d.name.rsplit("-", 1)[0], str(d / "best.patch"), "I1 final (Qwen original; not sanitizer-tested)"))
for n in (1, 2): items.append((f"human-attempt-{n}", str(ROOT / f"runs/human-control/c2-1058781/attempt-{n}.patch"), "human C2"))
tsan = {r["object"]: r for r in csv.DictReader(open(PM / "tables/correctness_unified.csv"))}
# manual reading of the added code (checked by eye in the patch text) overrides the regex where the regex is known to be wrong
OVERRIDE = {
    "final-bestofn-seed2": "thread-safe one-time init (static const bool initialized = lambda)",
    "r2-qwen-bestofn-s1": "unsynchronised lazy init (static bool initialized + manual build)",
    "r2-qwen-bestofn-s3": "unsynchronised lazy init (static vector filled when empty)",
    "r2-qwen-bestofn-s4": "thread-safe one-time init (static const auto sorted = lambda)",
    "r2-qwen-bestofn-s5": "mutable shared cache (static cache pointer overwritten on later calls)",
    "r2-qwen-population-s1": "thread-safe one-time init (static std::array lookup = lambda)",
    "r2-qwen-population-s2": "thread-safe one-time init (static const auto sorted = lambda)",
    "r2-qwen-population-s4": "no function-local static state added",
    "final-greedy-seed4": "mutable shared cache (GetFieldIndex tables allocated lazily into static pointer array) + thread-safe GetMesg init",
    "s3-gen6": "no function-local static state added", "s3-gen11": "no function-local static state added",
    "s3-gen12": "mutable shared cache (static cachedMesg / cachedFieldIndex rewritten when the queried message changes)",
    "s3-gen13": "mutable shared cache (static cachedMesg / cachedFieldIndex rewritten when the queried message changes)",
    "human-attempt-1": "thread-safe one-time init (static const LookupTable table)", "human-attempt-2": "thread-safe one-time init (static const LookupTable / FieldIndexTable)",
}
def label(pats):
    if "mutable_cache" in pats: return "mutable shared cache or lazily built tables (races in steady state)"
    if "plain_flag" in pats: return "unsynchronised lazy init (race on the first calls)"
    if "magic_static" in pats: return "thread-safe one-time init"
    return "no function-local static state added" if not pats - {"lookup_storage"} else "other"
out = []
for name, path, grp in items:
    st, pats = classify(path)
    key = name.replace("final-", "final-") if name.startswith("final-") else name
    tr = tsan.get(key) or tsan.get(name.replace("greedy", "greedy")) or {}
    reading = OVERRIDE.get(name, label(pats))
    unsafe = not (reading.startswith("thread-safe") or reading.startswith("no function-local"))
    obs = tr.get("tsan_race_locations", "")
    out.append({"object": name, "group": grp, "reading_of_added_code": reading, "reading_checked_by_eye": name in OVERRIDE, "regex_patterns": ";".join(sorted(pats)) or "none",
                "reading_says_unsafe": unsafe, "tsan_observed_race": (int(obs) > 0) if str(obs).isdigit() else "",
                "unsafe_pattern_but_no_race_observed": bool(unsafe and str(obs).isdigit() and int(obs) == 0), "static_lines_added": " || ".join(st)[:600],
                "tsan_tested": bool(tr.get("tsan_subset_files")), "tsan_race_locations_observed": tr.get("tsan_race_locations", ""), "tsan_digest_mismatches": tr.get("tsan_digest_mismatches", "")})
write_csv(PM / "tables/concurrency_patterns_by_patch.csv", out)
if __name__ == "__main__":
    for o in out: print(f"{o['object'][:34]:34s} {o['reading_of_added_code'][:60]:60s} tsan_loc={o['tsan_race_locations_observed']!s:3s} mism={o['tsan_digest_mismatches']!s:6s} | {o['static_lines_added'][:90]}")
