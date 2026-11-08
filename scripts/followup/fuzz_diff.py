#!/usr/bin/env python3
"""Follow-up 4a: differential test of patched libraries against the stock library on the corpus (scripts/followup/gen_corpus.py).

For each patch variant a candidate library is built by the project's own harness (`CanMehHarness measure-patch`, minimal timing, which also runs the
harness checks: output digest, profile digest, single thread). Then, in a separate process per variant (crash isolation), stock and candidate are
loaded with dlopen and every corpus file is decoded by both through the workload's exported entry points (canmehLoadDataFiles / canmehDecode /
canmehMessageCount / canmehFieldCount). Outcomes (digest, messages, fields) must be identical; any difference, and any crash that happens in only
one library, is a finding. Equal crashes (both libraries die on the same hostile input) are counted separately and are not differences.
usage: fuzz_diff.py --work W --corpus DIR --out OUT --variants variants.json
  variants.json: [{"name": "...", "patch": "/abs/path.patch"}, ...]
"""
import argparse, ctypes, json, os, subprocess, sys, time
from pathlib import Path


def child(ref, cand, corpus, start, end, outfile):
    r = ctypes.CDLL(ref, mode=ctypes.RTLD_LOCAL)
    c = ctypes.CDLL(cand, mode=ctypes.RTLD_LOCAL)
    for lib in (r, c):
        lib.canmehLoadDataFiles.argtypes = [ctypes.c_char_p]
        lib.canmehLoadDataFiles.restype = ctypes.c_int
        for n in ("canmehDecode", "canmehMessageCount", "canmehFieldCount"):
            getattr(lib, n).restype = ctypes.c_ulonglong
    out = open(outfile, "a")
    for i in range(start, end):
        d = os.path.join(corpus, "%04d" % i).encode()
        res = {}
        for name, lib in (("ref", r), ("cand", c)):
            out.write(json.dumps({"i": i, "start": name}) + "\n"); out.flush()
            n = lib.canmehLoadDataFiles(d)
            dg = lib.canmehDecode()
            res[name] = [n, int(dg), int(lib.canmehMessageCount()), int(lib.canmehFieldCount())]
        out.write(json.dumps({"i": i, "ref": res["ref"], "cand": res["cand"]}) + "\n"); out.flush()
    out.write(json.dumps({"done": True}) + "\n"); out.close()


def child_one(lib, corpus, i):
    c = ctypes.CDLL(lib, mode=ctypes.RTLD_LOCAL)
    c.canmehLoadDataFiles.argtypes = [ctypes.c_char_p]
    for n in ("canmehDecode", "canmehMessageCount", "canmehFieldCount"):
        getattr(c, n).restype = ctypes.c_ulonglong
    c.canmehLoadDataFiles(os.path.join(corpus, "%04d" % i).encode())
    c.canmehDecode()


def run_variant(ref, cand, corpus, n_files, outdir):
    outfile = outdir / "raw.jsonl"
    outfile.write_text("")
    pos, crashes = 0, []
    while pos < n_files:
        p = subprocess.run([sys.executable, __file__, "--child", ref, cand, str(corpus), str(pos), str(n_files), str(outfile)], capture_output=True, text=True, errors="replace")
        lines = [json.loads(l) for l in outfile.read_text().splitlines() if l.strip()]
        if lines and lines[-1].get("done"):
            break
        # the child died: attribute the crash to the library whose "start" line is the last one written
        last = [l for l in lines if "start" in l or "ref" in l]
        if not last:
            crashes.append({"i": pos, "who": "load", "rc": p.returncode, "stderr": p.stderr[-200:]})
            break
        cur = last[-1]
        if "start" in cur:
            who = cur["start"]
            if who == "ref":
                # the stock library died first, so the candidate never ran on this file: run it alone to see whether it dies too
                q = subprocess.run([sys.executable, __file__, "--child-one", cand, str(corpus), str(cur["i"])], capture_output=True, text=True, errors="replace")
                who = "both" if q.returncode != 0 else "stock_only"
            else:
                who = "cand_only"
            crashes.append({"i": cur["i"], "who": who, "rc": p.returncode})
            pos = cur["i"] + 1
            with open(outfile, "a") as f:
                f.write(json.dumps({"i": cur["i"], "crash": who, "rc": p.returncode}) + "\n")
        else:
            pos = cur["i"] + 1
    rows = [json.loads(l) for l in outfile.read_text().splitlines() if l.strip()]
    done = {r["i"]: r for r in rows if "ref" in r}
    crash = {r["i"]: r for r in rows if "crash" in r}
    diffs = [{"i": i, "ref": r["ref"], "cand": r["cand"]} for i, r in done.items() if r["ref"] != r["cand"]]
    only_cand = [i for i, c in crash.items() if c["crash"] == "cand_only"]
    only_ref = [i for i, c in crash.items() if c["crash"] == "stock_only"]
    both = [i for i, c in crash.items() if c["crash"] == "both"]
    return {"files": n_files, "compared": len(done), "identical": len(done) - len(diffs), "differences": diffs[:20], "n_differences": len(diffs),
            "crash_in_candidate": only_cand[:20], "n_crash_in_candidate": len(only_cand), "crash_in_stock": only_ref[:20], "n_crash_in_stock": len(only_ref), "n_crash_in_both": len(both)}


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--child-one":
        child_one(sys.argv[2], sys.argv[3], int(sys.argv[4]))
        sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        child(*sys.argv[2:4], sys.argv[4], int(sys.argv[5]), int(sys.argv[6]), sys.argv[7])
        sys.exit(0)
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--variants", required=True)
    ap.add_argument("--harness", default="build/CanMehHarness")
    ap.add_argument("--shard", default="0/1", help="i/n: run variants with index %% n == i")
    a = ap.parse_args()
    out = Path(a.out)
    (out / "libs").mkdir(parents=True, exist_ok=True)
    n_files = len(json.load(open(Path(a.corpus) / "index.json")))
    ref = str(Path(a.work) / "libfit_ref.so")
    summary = {}
    si, sn = map(int, a.shard.split("/"))
    for vi, v in enumerate(json.load(open(a.variants))):
        if vi % sn != si:
            continue
        t0 = time.time()
        vd = out / v["name"]
        vd.mkdir(exist_ok=True)
        m = subprocess.run([a.harness, "measure-patch", "--work", a.work, "--patch", v["patch"], "--no-decision", "--repeat", "1", "--repetitions", "3"],
                           capture_output=True, text=True, errors="replace")
        try:
            mj = json.loads(m.stdout)
        except Exception:
            mj = {"ok": False, "error": (m.stderr or m.stdout)[:300]}
        (vd / "build.json").write_text(json.dumps({k: mj.get(k) for k in ("ok", "stage", "error", "build_s")}))
        if not mj.get("ok"):
            summary[v["name"]] = {"build_failed": mj.get("stage") or mj.get("error")}
            print(v["name"], "build/harness check failed:", summary[v["name"]], flush=True)
            continue
        cand = str(out / "libs" / (v["name"] + ".so"))
        subprocess.run(["cp", str(Path(a.work) / "libfit_cand.so"), cand], check=True)
        r = run_variant(ref, cand, a.corpus, n_files, vd)
        r["seconds"] = round(time.time() - t0, 1)
        summary[v["name"]] = r
        (out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
        print(v["name"], {k: r[k] for k in ("compared", "identical", "n_differences", "n_crash_in_candidate", "n_crash_in_stock", "n_crash_in_both")}, flush=True)
    (out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
