#!/usr/bin/env python3
"""Check that the "no-op" candidates of the null-search and the inert SDK patch really change no machine code.

For each patch the candidate library is built by the project's harness (measure-patch, minimal timing) and its .text section is compared byte for byte with
the stock library built in the same work directory (objcopy -O binary --only-section=.text), together with the dynamic symbol list. Identical code means
there is no optimisation to find, so any 'faster' verdict on such a candidate would be a false accept; "functionally equivalent" is not enough evidence on its own.
usage: verify_noop.py --work W --out OUT
"""
import argparse, glob, hashlib, json, re, subprocess
from pathlib import Path
ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
OUT = Path(a.out)
OUT.mkdir(parents=True, exist_ok=True)
ROOT = Path(__file__).resolve().parent.parent.parent


def text_sha(lib):
    tmp = OUT / "text.bin"
    subprocess.run(["objcopy", "-O", "binary", "--only-section=.text", str(lib), str(tmp)], check=True)
    h = hashlib.sha256(tmp.read_bytes()).hexdigest()
    n = tmp.stat().st_size
    tmp.unlink()
    return h, n


def symbols(lib):
    r = subprocess.run(["nm", "-D", "--defined-only", str(lib)], capture_output=True, text=True)
    return sorted(l.split()[-1] for l in r.stdout.splitlines() if l.strip())


ref = Path(a.work) / "libfit_ref.so"
ref_h, ref_n = text_sha(ref)
ref_sym = symbols(ref)
patches = [("inert-check", ROOT / "runs/inert-check/inert.patch")]
for d in sorted(glob.glob(str(ROOT / "runs/followup/null-search-xcn*"))):
    steps = [json.loads(l) for l in open(d + "/steps.jsonl") if l.strip()]
    upd = [r for r in steps if r.get("updated")]
    last_any = [r for r in steps if r.get("stage") == "measured"][-1]
    for tag, r in (("last-accepted", upd[-1] if upd else None), ("last-measured", last_any)):
        if r:
            patches.append(("%s-%s-attempt%d" % (Path(d).name, tag, r["attempt"]), Path(d) / "patches" / ("a%03d.patch" % r["attempt"])))
res = []
for name, p in patches:
    m = subprocess.run([str(ROOT / "build/CanMehHarness"), "measure-patch", "--work", a.work, "--patch", str(p), "--no-decision", "--repeat", "1", "--repetitions", "3"], capture_output=True, text=True)
    try:
        ok = json.loads(m.stdout).get("ok")
    except Exception:
        ok = False
    if not ok:
        res.append({"patch": name, "built": False})
        continue
    cand = Path(a.work) / "libfit_cand.so"
    h, n = text_sha(cand)
    res.append({"patch": name, "patch_file": str(p.relative_to(ROOT)), "built": True, "text_bytes": n, "text_identical_to_stock": h == ref_h and n == ref_n,
                "dynamic_symbols_identical": symbols(cand) == ref_sym})
    print(res[-1], flush=True)
(OUT / "noop_verification.json").write_text(json.dumps({"stock_text_sha256": ref_h, "stock_text_bytes": ref_n, "results": res}, indent=1) + "\n")
print("all identical:", all(r.get("text_identical_to_stock") for r in res if r.get("built")), "built:", sum(1 for r in res if r.get("built")), "of", len(res))
