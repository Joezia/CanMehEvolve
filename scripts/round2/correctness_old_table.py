#!/usr/bin/env python3
"""Per-patch, per-test-condition table for the follow-up correctness runs (round 1.5; no rerun). Replaces the earlier prose summary, which called one patch
"the only clean one" although several others were equally clean. Conditions are reported side by side; warning counts are NOT used to rank severity.
Inputs: runs/followup/correctness-diff-*/summary.json, correctness-sanitize-*/{summary.json,<variant>-{asan,tsan}.err}. Output: runs/followup/CORRECTNESS_BY_PATCH.md
Note on the corpus of that round: legal files = the 4 standard files only; the 400 other files are mutants with recomputed CRCs (stress inputs, NOT legal files)."""
import glob, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent.parent
F = ROOT / "runs/followup"
J = lambda p, d=None: json.load(open(p)) if Path(p).exists() else d
diff, san, errdir = {}, {}, {}
for f in sorted(glob.glob(str(F / "correctness-diff-*/summary.json"))):
    diff.update(J(f, {}) or {})
for d in sorted(glob.glob(str(F / "correctness-sanitize-*"))):
    for k, v in (J(d + "/summary.json", {}) or {}).items():
        san[k] = v
        errdir[k.split("|")[0]] = d


def norm(txt):
    # file + message with every number replaced: a patched file shifts line numbers, so the same stock UB must not be counted as new
    return {m.group(1) + " " + re.sub(r"-?\d+", "N", m.group(2)) for m in re.finditer(r"(src/[\w./]+):\d+:\d+: runtime error: (.*)", txt)}


def read(name, cfg):
    d = errdir.get(name)
    p = Path(d) / ("%s-%s.err" % (name, cfg)) if d else None
    return p.read_text(errors="replace") if p and p.exists() else ""


stock_ub = norm(read("stock", "asan"))
names = sorted({k.split("|")[0] for k in san if k.split("|")[0] != "stock"} | set(diff))
L = ["# Follow-up correctness results per patch and test condition", "",
     "Corpus: the 4 standard files plus 400 mutants with recomputed CRCs (not legal files). The stock library itself dies on 177 of the 404 files (uncaught exception), so the differential comparison covers 227 files.",
     "UBSan: messages that do NOT also occur with the stock library (the stock library has %d of its own: %s)." % (len(stock_ub), "; ".join(sorted(stock_ub))), "",
     "| patch | differential vs stock: compared / identical / differing | crash in both (same input) | crash only in patch | crash only in stock | ASan errors | UBSan messages not in stock | ASan-run digest differences | TSan distinct race locations | TSan digest mismatches (4 threads) | TSan run result |",
     "|---|---|---|---|---|---|---|---|---|---|---|"]
for n in names:
    dv = diff.get(n, {})
    sa, st_ = san.get(n + "|asan", {}), san.get(n + "|tsan", {})
    new_ub = norm(read(n, "asan")) - stock_ub
    races = set(re.findall(r"SUMMARY: ThreadSanitizer: (?:data race|[\w ]+) .*?/(src/[\w./]+:\d+)", read(n, "tsan")))
    mm = re.search(r"digest_mismatches (\d+)", st_.get("output", "") or "")
    rc = st_.get("returncode")
    res = "completed" if (mm and rc == 0) else ("completed with race reports (exit %s)" % rc if mm else "did not finish (exit %s, no digest line)" % rc)
    L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
        n, ("%s / %s / %s" % (dv.get("compared"), dv.get("identical"), dv.get("n_differences"))) if dv else "-", dv.get("n_crash_in_both", "-") if dv else "-",
        dv.get("n_crash_in_candidate", "-") if dv else "-", dv.get("n_crash_in_stock", "-") if dv else "-", sa.get("asan_errors", "-"), (str(len(new_ub)) if sa else "-"),
        sa.get("digest_differences_vs_stock", "-"), (str(len(races)) if st_ else "-"), mm.group(1) if mm else "-", res if st_ else "-"))
(F / "CORRECTNESS_BY_PATCH.md").write_text("\n".join(L) + "\n")
print("\n".join(L))
