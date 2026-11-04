#!/usr/bin/env python3
"""Write experiments/patches/final-cumulative/README.md: for each run's fixed final patch, its re-measured speedup, the functions it changes
(from the run's accepted search steps) and a short description of what each kind of change does and why it might be faster.
Facts (functions, speedups, sha256) come from the run files; the one-line descriptions were written from reading the incremental diffs
(`patches/` for seed 3, `experiments/patches/greedy-s*-unexplained/` for the others) and are hedged: none of them was verified by profiling, and per-step effects were never independently confirmed."""
import hashlib, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "experiments/patches/final-cumulative"
DESC = {
    "Profile::GetMesg": ("replaces the linear scan over all message types by a table indexed by message number (65,536 entries or a smaller guarded table)",
                         "it runs for every message and field of the decode, so one array read replaces a scan; the table is built lazily (plain `bool` flag in most winners: not thread-safe)"),
    "Profile::GetFieldIndex": ("answers field-number lookups from a cached or precomputed table instead of scanning `mesg->fields`", "called per field; the scan becomes a bit test / array read; the cached variant keeps unsynchronised statics"),
    "FieldBase::FieldBase": ("copy constructor copies `values` and `stringIndexes` in the member-initialiser list instead of default-constructing then assigning", "avoids two default constructions and assignments for every copied field"),
    "FieldBase::GetValue": ("reads 1/2/4/8-byte values with one `memcpy` instead of assembling bytes in a loop", "one load instead of several shift/or steps per value; assumes a little-endian host"),
    "FieldBase::GetFLOAT64Value": ("rewrites the type switch to read values directly with invalid checks instead of `ConvertBaseType` (uses `goto`)", "skips generic conversion; semantic equivalence beyond the harness checks is unverified"),
    "FieldBase::GetNumValues": ("divides by the element size with a shift table instead of a division", "avoids an integer division per call; assumes power-of-two element sizes"),
    "FieldBase::Read": ("restructures the field read (string and numeric cases) with `memcpy` and fewer repeated lookups", "less work per byte when decoding field data"),
    "FieldBase::SetUINT64ZValue": ("adds `__attribute__((flatten))`", "compiler hint to inline callees; effect is a guess"),
    "Field::Field": ("constructor from (message number, field number) answers profile lookups from small static caches", "avoids repeated profile lookups; unsynchronised statics"),
    "Field::GetNum": ("loads `profile` and `profileIndex` into locals and reorders the checks", "tiny; likely within noise"),
    "Field::GetType": ("single-return form", "probably none; within noise"),
    "Field::GetNumSubFields": ("branch hints on the null/range checks", "probably marginal; within noise"),
    "Mesg::GetField": ("scans the field vector four elements at a time through a raw pointer", "fewer loop-control steps per lookup"),
    "Mesg::AddField": ("scans existing fields directly instead of calling `GetField`", "one call and pointer return less per added field"),
    "Mesg::GetActiveSubFieldIndexByFieldIndex": ("caches referenced-field lookups across sub-fields", "avoids repeated `GetField`/`GetFLOAT64Value` for sub-fields sharing a reference field"),
    "Decode::Resume": ("keeps byte index and offset in locals inside the per-byte loop", "avoids reloading and storing members every byte"),
    "CRC::Get16": ("byte-wise 256-entry table instead of two 16-entry nibble steps", "half the table lookups per byte"),
    "FieldDefinition::GetNum": ("adds `__attribute__((pure))`", "compiler hint; effect is a guess"),
    "MesgDefinition::GetFieldByIndex": ("raw data pointer and branch hint", "tiny; within noise"),
    "MesgBroadcaster::RemoveListener": ("hand-written erase instead of `std::find` + `erase`", "not on the decode path; likely noise"),
}
L = ["# Final patches of each run (cumulative against stock)", "",
     "Each file is the run's **fixed final patch** as one diff against stock SDK 21.201.0 (apply one of them to stock with `git apply`; never several). "
     "Speedups are the median of three independent re-measurements (`runs/<run>/evaluate-best/summary.json`). The submitted, step-by-step explained series is the median-seed greedy chain "
     "(`patches/` at the repository root); the other chains are experiment records (`experiments/patches/greedy-s*-unexplained/`, provenance-only messages). The descriptions below were written from reading the diffs; none is verified by profiling.", "",
     "| run | final patch | speedup (re-measured) | functions changed (accepted search steps) | sha256 of patch |", "|---|---|---|---|---|"]
used = []
for d in sorted((ROOT / "runs/deepseek").glob("*-s[1-5]-[0-9]*")):
    if "resume" in d.name or not d.is_dir():
        continue
    arm, seed = re.match(r"(greedy|bestofn)-s(\d)-", d.name).groups()
    ev = json.load(open(d / "evaluate-best/summary.json"))
    ups = json.load(open(d / "summary.json"))["rank_updates"]
    labels = []
    # greedy: every accepted step builds on the previous one, so the final patch contains all of them;
    # best-of-N: every candidate starts from stock, so the final patch is only the last accepted candidate
    for u in (ups if arm == "greedy" else ups[-1:]):
        if u["label"] not in labels:
            labels.append(u["label"])
    used += labels
    f = OUT / ("%s-seed%s.cumulative-vs-stock.patch" % (arm, seed))
    L.append("| %s seed %s | `%s` | %.3f | %s | `%s` |" % (arm, seed, f.name, ev["median_speedup"], ", ".join("`%s`" % x for x in labels), hashlib.sha256(f.read_bytes()).hexdigest()[:16]))
L += ["", "## What each changed function does (idea; implementations differ between chains, see the incremental patches)", "", "| function | change | why it might be faster / caveat |", "|---|---|---|"]
for k in sorted(set(used)):
    a, b = DESC.get(k, ("(not described)", ""))
    L.append("| `%s` | %s | %s |" % (k, a, b))
missing = [k for k in set(used) if k not in DESC]
(OUT / "README.md").write_text("\n".join(L) + "\n")
print("functions without description:", missing)
