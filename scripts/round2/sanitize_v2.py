#!/usr/bin/env python3
"""Follow-up 4b: build the stock SDK and each patch variant under sanitizers and run the driver (driver.cpp) on corpus files.

asan  : -fsanitize=address,undefined, single thread, ~70 corpus files (4 originals + mutants) -> memory errors, undefined behaviour, digest differences vs stock.
tsan  : -fsanitize=thread, 4 threads decoding concurrently, 4 originals + 8 mutants -> data races (shared lazily built tables or caches in patched code).
Only translation units named in a patch are recompiled for a variant; the other objects are the stock ones. No harness and no timing are involved.
usage: sanitize.py --corpus DIR --variants variants.json --out OUT [--jobs 12]
"""
import argparse, json, os, re, shutil, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--corpus", required=True)
ap.add_argument("--variants", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--jobs", type=int, default=12)
ap.add_argument("--configs", default="plain,asan,tsan", help="comma separated subset of plain,asan,tsan")
ap.add_argument("--stock-src", default="build/FITSDK-prefix/src/FITSDK/src")
ap.add_argument("--project-src", default="src")
ap.add_argument("--scratch", default=str(Path.home() / ".sanitize-scratch"))
a = ap.parse_args()
OUT, SC = Path(a.out), Path(a.scratch)
OUT.mkdir(parents=True, exist_ok=True)
shutil.rmtree(SC, ignore_errors=True)
SC.mkdir(parents=True)
corpus = Path(a.corpus)
index = json.load(open(corpus / "index.json"))
CFG = {"plain": [], "asan": ["-fsanitize=address,undefined"], "tsan": ["-fsanitize=thread"]}
COMMON = ["-std=c++17", "-O1", "-g", "-fno-omit-frame-pointer"]


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, errors="replace", **kw)


def subset(name, ids):
    d = SC / name
    d.mkdir()
    for i in ids:
        os.symlink((corpus / ("%04d" % i)).resolve(), d / ("%04d" % i))
    return str(d)


orig = [r["id"] for r in index if r["kind"] == "original"]
valid = [r["id"] for r in index if r["kind"] == "valid"]
asan_ids = orig + valid + [r["id"] for r in index if r["kind"] not in ("original", "valid") and r["id"] % 6 == 0]
tsan_ids = orig + valid[:12] + [r["id"] for r in index if r["kind"] == "data"][:4] + [r["id"] for r in index if r["kind"] == "defs"][:4]
plain_ids = [r["id"] for r in index]
SUB = {"asan": subset("sub-asan", asan_ids), "tsan": subset("sub-tsan", tsan_ids), "plain": subset("sub-plain", plain_ids)}
print("subsets:", {k: len(v) for k, v in {"asan": asan_ids, "tsan": tsan_ids, "plain": plain_ids}.items()}, flush=True)

stock = SC / "stock"
shutil.copytree(a.stock_src, stock / "src")
tus = sorted(p.stem for p in (stock / "src").glob("*.cpp"))


def compile_tu(args):
    src_root, objdir, stem, flags = args
    r = sh(["g++", *COMMON, *flags, "-I", str(src_root / "src"), "-c", str(src_root / "src" / (stem + ".cpp")), "-o", str(objdir / (stem + ".o"))])
    return stem, r.returncode, r.stderr[-300:]


def build_base(cfg):
    flags = CFG[cfg]
    od = SC / ("obj-" + cfg)
    od.mkdir()
    with ThreadPoolExecutor(a.jobs) as ex:
        res = list(ex.map(compile_tu, [(stock, od, s, flags) for s in tus]))
    bad = [r for r in res if r[1]]
    if bad:
        sys.exit("stock build failed under %s: %s" % (cfg, bad[0]))
    r = sh(["g++", *COMMON, *flags, "-I", str(Path(a.project_src).resolve()), "-I", str(stock / "src"), "-c", str(Path(__file__).resolve().parent.parent / "followup" / "driver.cpp"), "-o", str(od / "driver.o")])
    if r.returncode:
        sys.exit("driver build failed: " + r.stderr[-500:])
    return od


def link(cfg, objdir, exe):
    r = sh(["bash", "-c", "g++ %s %s/*.o -o %s -lpthread" % (" ".join(CFG[cfg]), objdir, exe)])
    return r.returncode == 0, r.stderr[-300:]


def counts(txt):
    return {"asan_errors": len(re.findall(r"ERROR: AddressSanitizer", txt)), "ubsan_runtime_errors": len(re.findall(r"runtime error:", txt)),
            "tsan_warnings": len(re.findall(r"WARNING: ThreadSanitizer", txt))}


def run_mode(cfg, exe):
    if cfg == "plain":
        # every corpus file, one line each: status (0 ok, 1 Decode::Read returned false, 2 exception) and the exception text
        # one process per file: a stock or candidate library that dies on a hostile file must not hide the files after it. A line per file:
        # "<path> <status> <messages> <text>", status 0 ok, 1 Decode::Read false, 2 exception, 3 killed by a signal or timeout (text says which)
        lines, errs, rc = [], [], 0
        for d in sorted(Path(SUB["plain"]).iterdir()):
            f = str(d.resolve() / "x.fit")
            try:
                q = sh([str(exe), "classify", str(d)], timeout=60)
            except subprocess.TimeoutExpired:
                lines.append("%s 3 0 timeout" % f)
                continue
            if q.returncode != 0:
                lines.append("%s 3 0 returncode_%d" % (f, q.returncode))
                errs.append(q.stderr[-200:])
            else:
                lines.extend(l.replace("\n", " ") for l in q.stdout.splitlines() if l.strip())
        return subprocess.CompletedProcess([], 0, "\n".join(lines) + "\n", "\n".join(errs))
    elif cfg == "asan":
        r = sh([str(exe), "single", SUB["asan"]], env=dict(os.environ, ASAN_OPTIONS="detect_leaks=0", UBSAN_OPTIONS="print_stacktrace=1"))
    else:
        # ThreadSanitizer needs ASLR off on kernels with high mmap entropy (otherwise it dies with "unexpected memory mapping")
        r = sh(["setarch", "x86_64", "-R", str(exe), "threads", "4", "1", SUB["tsan"]], env=dict(os.environ, TSAN_OPTIONS="halt_on_error=0 second_deadlock_stack=1"))
    return r


results = {}
for cfg in [c for c in ("plain", "asan", "tsan") if c in a.configs.split(",")]:
    base = build_base(cfg)
    # stock reference run
    exe = SC / ("drv-stock-" + cfg)
    ok, err = link(cfg, base, exe)
    if not ok:
        sys.exit("link stock failed: " + err)
    ref = run_mode(cfg, exe)
    ref_lines = ref.stdout.splitlines()
    (OUT / ("stock-%s.out" % cfg)).write_text(ref.stdout)
    (OUT / ("stock-%s.err" % cfg)).write_text(ref.stderr[-20000:])
    results[("stock", cfg)] = {"returncode": ref.returncode, **counts(ref.stderr)}
    print("stock", cfg, results[("stock", cfg)], flush=True)

    def one(v):
        d = SC / ("var-%s-%s" % (cfg, v["name"]))
        shutil.copytree(stock / "src", d / "src")
        p = sh(["bash", "-c", "cd %s && patch -p1 -s < %s" % (d, v["patch"])])
        if p.returncode:
            return v["name"], {"patch_failed": p.stdout[-200:] + p.stderr[-200:]}
        changed = sorted(set(re.findall(r"^\+\+\+ b/src/(\w+)\.cpp", Path(v["patch"]).read_text(), re.M)))
        od = SC / ("obj-%s-%s" % (cfg, v["name"]))
        shutil.copytree(base, od)
        for s in changed:
            _, rc, err = compile_tu((d, od, s, CFG[cfg]))
            if rc:
                return v["name"], {"compile_failed": s, "stderr": err}
        exe = SC / ("drv-%s-%s" % (cfg, v["name"]))
        ok, err = link(cfg, od, exe)
        if not ok:
            return v["name"], {"link_failed": err}
        r = run_mode(cfg, exe)
        (OUT / ("%s-%s.out" % (v["name"], cfg))).write_text(r.stdout)
        (OUT / ("%s-%s.err" % (v["name"], cfg))).write_text(r.stderr[-20000:])
        res = {"changed_units": changed, "returncode": r.returncode, **counts(r.stderr)}
        if cfg == "plain":
            lines = r.stdout.splitlines()
            res["files"] = len(lines)
            res["handling_differences_vs_stock"] = sum(1 for x, y in zip(lines, ref_lines) if x.split(" ", 1)[1:] != y.split(" ", 1)[1:] and x.split()[0] == y.split()[0])
        elif cfg == "asan":
            lines = r.stdout.splitlines()
            res["files"] = len(lines)
            res["digest_differences_vs_stock"] = sum(1 for x, y in zip(lines, ref_lines) if x.split()[1:] != y.split()[1:] and x.split()[0] == y.split()[0])
        else:
            res["output"] = r.stdout.strip()[-200:]
        shutil.rmtree(od, ignore_errors=True)
        shutil.rmtree(d, ignore_errors=True)
        return v["name"], res

    variants = json.load(open(a.variants))
    with ThreadPoolExecutor(max(1, a.jobs // 3)) as ex:
        for name, res in ex.map(one, variants):
            results[(name, cfg)] = res
            print(name, cfg, res, flush=True)
    (OUT / "summary.json").write_text(json.dumps({"%s|%s" % k: v for k, v in results.items()}, indent=1) + "\n")
print("done")
