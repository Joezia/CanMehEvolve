#!/usr/bin/env python3
"""How does the STOCK SDK handle every file of the correctness corpus? One process per file (plain -O1 build, ASan+UBSan build), with a timeout, so that every
outcome is told apart: decoded, Decode::Read returned false (the SDK's normal error return), uncaught C++ exception (text kept), killed by a signal, memory-sanitizer
error, timeout. Writes classification.csv and classification_summary.md. usage: classify_stock.py --corpus DIR --out OUT"""
import argparse, csv, json, os, re, shutil, subprocess
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ap = argparse.ArgumentParser()
ap.add_argument("--corpus", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--jobs", type=int, default=12)
a = ap.parse_args()
ROOT = Path(__file__).resolve().parent.parent.parent
SDK = ROOT / "build/FITSDK-prefix/src/FITSDK/src"
OUT = Path(a.out)
OUT.mkdir(parents=True, exist_ok=True)
SC = Path.home() / ".classify-scratch"
shutil.rmtree(SC, ignore_errors=True)
SC.mkdir(parents=True)
COMMON = ["-std=c++17", "-O1", "-g", "-fno-omit-frame-pointer"]


def build(tag, flags):
    od = SC / tag
    od.mkdir()
    tus = sorted(SDK.glob("*.cpp"))

    def one(f):
        return subprocess.run(["g++", *COMMON, *flags, "-I", str(SDK), "-c", str(f), "-o", str(od / (f.stem + ".o"))], capture_output=True).returncode
    with ThreadPoolExecutor(a.jobs) as ex:
        assert not any(ex.map(one, tus)), "stock build failed"
    subprocess.run(["g++", *COMMON, *flags, "-I", str(ROOT / "src"), "-I", str(SDK), "-c", str(ROOT / "scripts/followup/driver.cpp"), "-o", str(od / "driver.o")], check=True)
    exe = SC / ("drv-" + tag)
    subprocess.run(["bash", "-c", "g++ %s %s/*.o -o %s -lpthread" % (" ".join(flags), od, exe)], check=True)
    return exe


plain, asan = build("plain", []), build("asan", ["-fsanitize=address,undefined"])
index = json.load(open(Path(a.corpus) / "index.json"))


def classify(r):
    d = Path(a.corpus) / ("%04d" % r["id"])
    out = {"id": r["id"], "kind": r["kind"], "base": r["base"]}
    try:
        p = subprocess.run([str(plain), "classify", str(d)], capture_output=True, text=True, errors="replace", timeout=60)
    except subprocess.TimeoutExpired:
        out.update(outcome="timeout (60 s)", detail="")
        return out
    if p.returncode < 0:
        out.update(outcome="killed by signal %d" % -p.returncode, detail=p.stderr[-120:])
    else:
        parts = p.stdout.strip().split(" ", 3)
        status = parts[1] if len(parts) > 1 else "?"
        out.update(outcome={"0": "decoded", "1": "Decode::Read returned false"}.get(status, "uncaught exception"), detail=(parts[3] if len(parts) > 3 else ""))
    q = subprocess.run([str(asan), "classify", str(d)], capture_output=True, text=True, errors="replace", timeout=300, env=dict(os.environ, ASAN_OPTIONS="detect_leaks=0"))
    out["asan_error"] = int("ERROR: AddressSanitizer" in q.stderr)
    out["ubsan_messages"] = len(set(re.findall(r"runtime error: (.*)", re.sub(r"-?\d+", "N", q.stderr))))
    return out


with ThreadPoolExecutor(a.jobs) as ex:
    rows = list(ex.map(classify, index))
with open(OUT / "classification.csv", "w", newline="") as f:
    w = csv.DictWriter(f, ["id", "kind", "base", "outcome", "detail", "asan_error", "ubsan_messages"])
    w.writeheader()
    w.writerows(rows)
cnt = Counter((r["kind"], r["outcome"] + ((": " + r["detail"][:70]) if r["outcome"] == "uncaught exception" else "")) for r in rows)
L = ["# How the stock SDK handles the corpus (one process per file)", "", "| file kind | outcome | files |", "|---|---|---|"]
L += ["| %s | %s | %d |" % (k, o, n) for (k, o), n in sorted(cnt.items())]
L += ["", "ASan errors in stock: %d files; files with UBSan messages: %d" % (sum(r["asan_error"] for r in rows), sum(1 for r in rows if r["ubsan_messages"]))]
(OUT / "classification_summary.md").write_text("\n".join(L) + "\n")
print("\n".join(L))
