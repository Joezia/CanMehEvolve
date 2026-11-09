#!/usr/bin/env python3
"""Round 2 aggregation: every number comes from raw run files. Writes runs/round2/RESULTS.md and results.json. Tolerant of unfinished runs (they are listed as such).

Sections
  1  one row per formal run: model id(s) returned, code commit, seed, hosts/CPUs of every segment, HTTP requests, tokens, time, ending, null_ok per segment
  2  five-seed summaries per configuration (median and full range) with the correctness status of the final patches
  3  false-accept rates: synthetic null pair and SDK inert patch, by node class, with Clopper-Pearson intervals; failed or interrupted trials listed apart
  4  no-op machine-code check, extended correctness results per patch and test condition, how the stock library handles the files it cannot decode
Interpretation is not made here.
"""
import glob, itertools, json, math, re, statistics as st
from pathlib import Path
from scipy.stats import beta

ROOT = Path(__file__).resolve().parent.parent.parent
R2 = ROOT / "runs/round2"
def J(p, d=None):
    try:
        return json.load(open(p)) if Path(p).exists() else d
    except Exception:       # an unfinished or empty file of a run that is still going
        return d


def jl(p):
    try:
        return [json.loads(l) for l in open(p) if l.strip()]
    except Exception:
        return []


def kv(p):
    d = {}
    try:
        for l in open(p):
            if "=" in l:
                k, v = l.strip().split("=", 1)
                d.setdefault(k, v)
    except Exception:
        pass
    return d


def cp(k, n):
    if n == 0:
        return float("nan"), float("nan")
    return (0.0 if k == 0 else beta.ppf(0.025, k, n - k + 1)), (1.0 if k == n else beta.ppf(0.975, k + 1, n - k))


def rng(v):
    v = [x for x in v if x is not None]
    return "%.4g [%.4g, %.4g]" % (st.median(v), min(v), max(v)) if v else "n/a"


def perm_p(x, y):
    a = list(x) + list(y)
    n = len(x)
    obs = abs(st.median(x) - st.median(y))
    hit = tot = 0
    for idx in itertools.combinations(range(len(a)), n):
        p = [a[i] for i in idx]
        q = [a[i] for i in range(len(a)) if i not in idx]
        tot += 1
        hit += abs(st.median(p) - st.median(q)) >= obs - 1e-15
    return hit / tot


L = ["# Round 2 results (raw numbers; interpretation is in the separate Chinese note)", ""]
S = {}

# ---------------------------------------------------------------- 1. runs
runs = {}
for spec in sorted(glob.glob(str(R2 / "chains/[A-D].txt"))):
    for line in open(spec):
        if line.strip():
            r = json.loads(line)
            runs[r["id"]] = r
rows = []
for rid, spec in sorted(runs.items()):
    d = R2 / "runs" / rid
    summ = J(d / "summary.json", {})
    part = J(d / "summary_partial.json", {})
    res = jl(d / "results.jsonl")
    cred = [l.split(",") for l in open(d / "credits.csv").read().splitlines()[1:]] if (d / "credits.csv").exists() else []
    segs = sorted(glob.glob(str(d / "segments/*.node.txt")))
    hosts, cpus, commits, bins = [], [], set(), set()
    for f in segs:
        n = kv(f)
        if "host" in n:
            hosts.append(n["host"])
        if "cpu" in n:
            cpus.append(n["cpu"])
        commits.add(n.get("git_commit", ""))
        bins.add(n.get("binary_sha256", "")[:12])
    null_ok = [J(f, {}).get("null_ok") for f in sorted(glob.glob(str(d / "segments/*.init.json")))]
    attempts = sum(int((x.get("llm") or {}).get("http_attempts", 0) or 0) for x in res)
    models = sorted({(x.get("llm") or {}).get("model_returned") for x in res if (x.get("llm") or {}).get("model_returned")})
    nousage = sum(1 for x in res if x.get("llm") and not x["llm"].get("usage_seen"))
    trunc = sum(1 for x in res if (x.get("llm") or {}).get("finish_reason") == "length")
    nocall = sum(1 for x in res if not x.get("llm"))
    stages = {}
    for x in res:
        k = "valid" if x.get("ok") else (x.get("stage") or "other")
        stages[k] = stages.get(k, 0) + 1
    fin = J(d / "final/evaluate-best/summary.json", {})
    last = cred[-1] if cred else None
    done = bool(summ)
    row = {"id": rid, "model": spec["model_key"], "arm": "population" if spec["mode"] == "search" else "best-of-N", "seed": spec["seed"],
           "state": "complete" if done else ("running/partial" if part or res else "not started"), "ended": (summ or part).get("ended_because", ""),
           "models_returned": models, "code_commits": sorted(c for c in commits if c), "binary12": sorted(b for b in bins if b), "hosts": hosts, "cpus": sorted(set(cpus)),
           "segments": len(segs), "null_ok_per_segment": null_ok, "http_attempts": attempts, "rows": len(res), "rows_without_request": nocall, "no_usage_requests": nousage,
           "truncated": trunc, "stages": stages,
           "prompt_tokens": int(last[2]) if last else None, "completion_tokens": int(last[3]) if last else None, "total_tokens": int(last[4]) if last else None,
           "elapsed_s": float(last[7]) if last else None,
           "best_confirmed_speedup": float(last[5]) if last else None, "best_retained_speedup": float(last[6]) if last else None,
           "final_ratios": [m["analysis"]["ratio"] for m in fin.get("measurements", []) if m["analysis"].get("valid")],
           "final_passes": fin.get("measurements_passing_rule"), "final_median_speedup": fin.get("median_speedup"),
           "final_state": "re-measured" if fin else ("no confirmed patch" if (d / "final/NO_CONFIRMED_PATCH").exists() else ("abandoned" if (d / "ABANDONED").exists() else "pending"))}
    ts = row["total_tokens"]
    row["course_quotient_credits"] = (row["best_confirmed_speedup"] - 1) / ts if ts and row["best_confirmed_speedup"] else None
    row["metric_remeasured"] = (row["final_median_speedup"] - 1) / ts if ts and row["final_median_speedup"] else None
    rows.append(row)
S["runs"] = rows
L += ["## 1. Formal runs (all 20 listed, finished or not)", "",
      "| run | state | ended | model id returned | HTTP requests | rows (no request) | tokens | trunc. | no-usage | segments | hosts | best confirmed (credits) | best retained | re-measured (3x) | final state |",
      "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    L.append("| %s | %s | %s | %s | %s | %s (%s) | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
        r["id"], r["state"], r["ended"], ",".join(r["models_returned"]) or "-", r["http_attempts"], r["rows"], r["rows_without_request"], r["total_tokens"], r["truncated"], r["no_usage_requests"],
        r["segments"], "/".join(sorted(set(r["hosts"]))), ("%.4f" % r["best_confirmed_speedup"]) if r["best_confirmed_speedup"] else "-",
        ("%.4f" % r["best_retained_speedup"]) if r["best_retained_speedup"] else "-", ("%.4f (pass %s/3)" % (r["final_median_speedup"], r["final_passes"])) if r["final_median_speedup"] else "-", r["final_state"]))

# ---------------------------------------------------------------- 2. configurations
L += ["", "## 2. Five-seed summaries per configuration (never pooled across models)", "",
      "| configuration | runs complete | best confirmed in credits.csv: median [min, max] | re-measured final patch | total tokens | HTTP requests | course quotient from credits.csv | extended-correctness status of final patches |",
      "|---|---|---|---|---|---|---|---|"]
corr_status = {}
for f in glob.glob(str(R2 / "correctness/*/summary.json")):
    for k, v in (J(f, {}) or {}).items():
        corr_status[k] = v
S["configs"] = {}
for mk in ("ds", "qwen"):
    for arm in ("population", "best-of-N"):
        rs = [r for r in rows if r["model"] == mk and r["arm"] == arm]
        comp = [r for r in rs if r["state"] == "complete"]
        S["configs"]["%s|%s" % (mk, arm)] = {"complete": len(comp), "values": [r["best_confirmed_speedup"] for r in comp]}
        L.append("| %s %s | %d/5 | %s | %s | %s | %s | %s | see section 4 |" % (mk, arm, len(comp), rng([r["best_confirmed_speedup"] for r in comp]), rng([r["final_median_speedup"] for r in comp]),
                 rng([r["total_tokens"] for r in comp]), rng([r["http_attempts"] for r in comp]), rng([r["course_quotient_credits"] for r in comp])))
for mk in ("ds", "qwen"):
    a = [r["best_confirmed_speedup"] for r in rows if r["model"] == mk and r["arm"] == "population" and r["state"] == "complete"]
    b = [r["best_confirmed_speedup"] for r in rows if r["model"] == mk and r["arm"] == "best-of-N" and r["state"] == "complete"]
    if len(a) == 5 and len(b) == 5:
        L.append("")
        L.append("%s: population vs best-of-N, exploratory exact permutation test of the median difference p = %.4f (n = 5 vs 5; chosen before seeing these data but not a pre-registered primary test)" % (mk, perm_p(a, b)))

# ---------------------------------------------------------------- 3. false accepts
L += ["", "## 3. False-accept rates (frozen rule: ratio <= 0.98, sign-flip p < 0.01, not unstable; 10 processes x 9 repetitions)", ""]
fp = {}


def node_class(host):
    return "xcnc" if str(host).startswith("xcnc") else ("xcnd" if str(host).startswith("xcnd") else "other")


# synthetic null: phase 0 (xcnc2) + round-2 top-ups
null_rows = []
for r in jl(ROOT / "runs/phase0b-1069564/final/rule_rows.jsonl"):
    if "/null/" in r.get("file", "") and r.get("valid"):
        null_rows.append(("xcnc", "phase0-xcnc2", r["faster"]))
invalid_null = 0
for d in sorted(glob.glob(str(R2 / "fpr/null-*"))):
    n = kv(d + "/node.txt")
    cls = node_class(n.get("host"))
    rr = jl(d + "/rule_rows.jsonl")
    valid = [x for x in rr if x.get("valid")]
    files = len(glob.glob(d + "/trials/t*.json"))
    invalid_null += files - len(valid)
    for x in valid:
        null_rows.append((cls, "round2-" + n.get("host", "?"), x["faster"]))
for key, sel in (("synthetic null, node class xcnc", [x for x in null_rows if x[0] == "xcnc"]), ("synthetic null, node class xcnd", [x for x in null_rows if x[0] == "xcnd"]),
                 ("synthetic null, all valid trials", null_rows)):
    k = sum(1 for x in sel if x[2])
    lo, hi = cp(k, len(sel))
    fp[key] = {"n": len(sel), "false_accepts": k, "cp95": [lo, hi]}
# SDK inert: follow-up round + round 2
sdk = []
bad_sdk = 0
for d in sorted(glob.glob(str(ROOT / "runs/followup/sdk-inert-*")) + glob.glob(str(R2 / "fpr/sdk-inert-*"))):
    n = kv(d + "/node.txt")
    cls = node_class(n.get("host"))
    ev = J(next(iter(glob.glob(d + "/evaluate-*/summary.json")), ""), None)
    files = glob.glob(d + "/evaluate-*/m*.json")
    if ev is None:
        bad_sdk += len(files)
        continue
    for m in ev["measurements"]:
        if m["analysis"].get("valid"):
            sdk.append((cls, n.get("host"), m["analysis"]["faster"], m["analysis"]["ratio"], m["analysis"]["unstable"]))
        else:
            bad_sdk += 1
for cls in ("xcnc", "xcnd"):
    sel = [x for x in sdk if x[0] == cls]
    k = sum(1 for x in sel if x[2])
    lo, hi = cp(k, len(sel))
    fp["SDK inert patch, node class " + cls] = {"n": len(sel), "false_accepts": k, "cp95": [lo, hi], "ratio_median": st.median(x[3] for x in sel) if sel else None,
                                                "ratio_range": [min(x[3] for x in sel), max(x[3] for x in sel)] if sel else None, "unstable": sum(1 for x in sel if x[4])}
S["fpr"] = fp
L += ["| measurement | valid trials | false accepts | 95% Clopper-Pearson | note |", "|---|---|---|---|---|"]
for k, v in fp.items():
    L.append("| %s | %d | %d | [%.3f%%, %.3f%%] | %s |" % (k, v["n"], v["false_accepts"], 100 * v["cp95"][0], 100 * v["cp95"][1],
             ("ratio median %.5f, range [%.5f, %.5f], unstable %d" % (v["ratio_median"], *v["ratio_range"], v["unstable"])) if v.get("ratio_median") else ""))
L += ["", "Failed, unreadable or interrupted trials are NOT counted as valid trials: synthetic null %d, SDK inert %d (files without a valid analysis). Reaching 400 valid trials per stratum is a target; a shortfall is reported as it is." % (invalid_null, bad_sdk), ""]
if (R2 / "fpr").exists():
    for d in sorted(glob.glob(str(R2 / "fpr/null-*")) + glob.glob(str(R2 / "fpr/sdk-inert-*"))):
        n = kv(d + "/node.txt")
        L.append("- %s: host %s, cpu %s, start %s, end %s" % (Path(d).name, n.get("host"), n.get("cpu", ""), n.get("start"), n.get("end", "unfinished")))

# ---------------------------------------------------------------- 4. no-op and correctness
L += ["", "## 4. Machine-code check of the no-op candidates, extended correctness, stock failures", ""]
nv = next(iter(sorted(glob.glob(str(R2 / "fpr/noop-verification-*/noop_verification.json")))), None)
if nv:
    d = J(nv)
    L.append("No-op check: %d candidate libraries built; .text identical to stock in %d; dynamic symbols identical in %d." % (
        sum(1 for r in d["results"] if r.get("built")), sum(1 for r in d["results"] if r.get("text_identical_to_stock")), sum(1 for r in d["results"] if r.get("dynamic_symbols_identical"))))
else:
    L.append("No-op check: not finished.")
diff = {}
for f in glob.glob(str(R2 / "correctness/DIFF*/summary.json")):
    diff.update(J(f, {}) or {})
san = {}
for f in sorted(glob.glob(str(R2 / "correctness/SAN*/summary.json"))):
    san.update(J(f, {}) or {})


def norm(txt):
    out = set()
    for l in txt.splitlines():
        m = re.search(r"(src/[\w./]+):\d+:\d+: runtime error: (.*)", l)
        if m:
            out.add(m.group(1) + " " + re.sub(r"-?\d+", "N", m.group(2)))     # numbers replaced: patched files shift line numbers
    return out


def races(txt):
    return sorted(set(re.findall(r"SUMMARY: ThreadSanitizer: (.+?) /.*?/(src/[\w./]+:\d+) in (.*)", txt)))


def err_text(name, cfg):
    p = next(iter(glob.glob(str(R2 / ("correctness/SAN*/%s-%s.err" % (name, cfg))))), None)
    return Path(p).read_text(errors="replace") if p else None


stock_ub = norm(err_text("stock", "asan") or "")


def plain_load(name):
    f = next(iter(sorted(glob.glob(str(R2 / ("correctness/SAN*/%s-plain.out" % name))))[::-1]), None)
    o = {}
    if f:
        for l in open(f, errors="replace"):
            m = re.search(r"/(\d{4})/x\.fit (\d) (\d+) ?(.*)", l)
            if m:
                o[m.group(1)] = (m.group(2), m.group(3), re.sub(r"\d+", "N", m.group(4)))
    return o


plain_stock = plain_load("stock")


def plain_cmp(name):
    c = plain_load(name)
    if not c or not plain_stock:
        return "-"
    diff = [k for k in plain_stock if c.get(k) != plain_stock[k]]
    kills = [k for k in diff if c.get(k, ("",))[0] == "3" and plain_stock[k][0] != "3"]
    return "%d of %d files handled differently (%d newly killed by a signal)" % (len(diff), len(plain_stock), len(kills))
L += ["", "### Extended checks per patch and test condition (not ranked; counts of warnings are not a severity measure)", "",
      "| patch | legal encoder files: differential (compared/identical) | mutants (not legal): differential (compared/identical, crash in both, crash only in candidate) | how files are handled, vs stock (plain build) | ASan | UBSan: messages not in stock | TSan (4 threads): distinct race locations, digest mismatches, run result |",
      "|---|---|---|---|---|---|---|"]
names = sorted({k.split("|")[0] for k in san if "|" in k} | set(diff))
# legal (SDK-encoder-written) files versus mutants, recomputed from the raw per-file records of the differential test
_idxf = next(iter(sorted(glob.glob(str(R2 / "correctness/DIFF*/index.json")))), None)
_kind = {r["id"]: r["kind"] for r in J(_idxf)} if _idxf else {}
legal = {}
for rawf in glob.glob(str(R2 / "correctness/DIFF*/*/raw.jsonl")):
    rows = [json.loads(l) for l in open(rawf) if l.strip()]
    done_ = {r["i"]: r for r in rows if "ref" in r}
    crash_ = {r["i"]: r for r in rows if "crash" in r}
    lv = [i for i in done_ if _kind.get(i) == "valid"]
    legal[Path(rawf).parent.name] = {"compared": len(lv), "identical": sum(1 for i in lv if done_[i]["ref"] == done_[i]["cand"]),
                                     "crash": sum(1 for i in crash_ if _kind.get(i) == "valid"),
                                     "mut_compared": sum(1 for i in done_ if _kind.get(i) != "valid"),
                                     "mut_identical": sum(1 for i in done_ if _kind.get(i) != "valid" and done_[i]["ref"] == done_[i]["cand"])}
for nme in names:
    dv = diff.get(nme, {})
    sa = san.get(nme + "|asan", {})
    sp = san.get(nme + "|plain", {})
    stt = san.get(nme + "|tsan", {})
    ub = norm(err_text(nme, "asan") or "") - stock_ub
    tt = err_text(nme, "tsan") or ""
    rc = races(tt)
    mm = re.search(r"digest_mismatches (\d+)", stt.get("output", "") or "")
    L.append("| %s | %s | %s | %s | %s | %s | %s |" % (
        nme, ("%s/%s%s" % (legal[nme]["compared"], legal[nme]["identical"], (", crashes %d" % legal[nme]["crash"]) if legal[nme]["crash"] else "")) if nme in legal else "-",
        ("%s/%s, both-crash %s, cand-only crash %s" % (legal[nme]["mut_compared"], legal[nme]["mut_identical"], dv.get("n_crash_in_both"), dv.get("n_crash_in_candidate"))) if (dv and nme in legal) else "-",
        plain_cmp(nme) if sp else "-",
        ("%s ASan errors, %s digest differences" % (sa.get("asan_errors"), sa.get("digest_differences_vs_stock"))) if sa else "-",
        (str(len(ub)) + (": " + "; ".join(sorted(ub))[:160] if ub else "")) if sa else "-",
        ("%d locations; mismatches %s; returncode %s" % (len(rc), mm.group(1) if mm else "n/a (no output)", stt.get("returncode"))) if stt else "-"))
S["correctness"] = {"diff": diff, "san": {k: v for k, v in san.items()}}
# how the stock library handles each corpus file
cls_file = next(iter(sorted(glob.glob(str(R2 / "correctness/SAN*/stock-plain.out")))[::-1]), None)
idxf = next(iter(sorted(glob.glob(str(R2 / "correctness/SAN*/index.json")))), None)
if cls_file and idxf:
    idx = {("%04d" % r["id"]): r for r in J(idxf)}
    cnt = {}
    for line in open(cls_file):
        parts = line.rstrip("\n").split(" ", 3)
        if len(parts) < 2:
            continue
        m = re.search(r"/(\d{4})/", parts[0])
        kind = idx[m.group(1)]["kind"] if m else "?"
        parts = parts[:3] + [re.sub(r"\d+", "N", re.sub(r"[^\x20-\x7e]", "?", parts[3]))] if len(parts) > 3 else parts   # byte offsets and raw bytes out of the message
        status = {"0": "decoded", "1": "Decode::Read returned false", "2": "exception: " + (parts[3] if len(parts) > 3 else ""), "3": "killed/timeout: " + (parts[3] if len(parts) > 3 else "")}.get(parts[1], parts[1])
        cnt[(kind, status)] = cnt.get((kind, status), 0) + 1
    L += ["", "### How the stock library handles the corpus (plain build, exceptions caught)", "", "| file kind | outcome | files |", "|---|---|---|"]
    for (kind, status), n in sorted(cnt.items()):
        L.append("| %s | %s | %d |" % (kind, status, n))
(R2 / "RESULTS.md").write_text("\n".join(L) + "\n")
(R2 / "results.json").write_text(json.dumps(S, indent=1, default=str) + "\n")
print("\n".join(L[:60]))
