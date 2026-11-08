#!/usr/bin/env python3
"""Follow-up 4 helper: a corpus of FIT files for differential and sanitizer tests: the four standard files plus deterministic mutants.

Every mutant keeps a valid header and CRCs (they are recomputed), so the decoder does not reject it up front and the lookup, conversion and
field-handling code is exercised on unusual values: random bytes in the data section, bytes in the first 300 bytes (definition messages: field
numbers, base types, sizes), and truncations. The SDK's own FIT CRC-16 is reimplemented here (src/fit_crc.cpp).
usage: gen_corpus.py OUTDIR [--per-file 100] [--seed 1]    -> OUTDIR/<NNNN>/x.fit and OUTDIR/index.json
"""
import argparse, json, random
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("out")
ap.add_argument("--data", default="build/data")
ap.add_argument("--per-file", type=int, default=100)
ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--valid-dir", default="", help="directory of legal files written by the SDK encoder (scripts/round2/gen_valid_fit.cpp); appended with kind \"valid\"")
a = ap.parse_args()
TABLE = [0x0000, 0xCC01, 0xD801, 0x1400, 0xF001, 0x3C00, 0x2800, 0xE401, 0xA001, 0x6C00, 0x7800, 0xB401, 0x5000, 0x9C01, 0x8801, 0x4400]


def crc16(data):
    crc = 0
    for b in data:
        tmp = TABLE[crc & 0xF]
        crc = (crc >> 4) & 0x0FFF
        crc = crc ^ tmp ^ TABLE[b & 0xF]
        tmp = TABLE[crc & 0xF]
        crc = (crc >> 4) & 0x0FFF
        crc = crc ^ tmp ^ TABLE[(b >> 4) & 0xF]
    return crc


def fix(buf):
    hs = buf[0]
    if hs >= 14:
        c = crc16(bytes(buf[:12]))
        buf[12], buf[13] = c & 0xFF, c >> 8
    c = crc16(bytes(buf[:-2]))
    buf[-2], buf[-1] = c & 0xFF, c >> 8
    return buf


rng = random.Random(a.seed)
out = Path(a.out)
out.mkdir(parents=True, exist_ok=True)
index = []


def emit(name, kind, data):
    i = len(index)
    d = out / ("%04d" % i)
    d.mkdir(exist_ok=True)
    (d / "x.fit").write_bytes(bytes(data))
    index.append({"id": i, "base": name, "kind": kind, "bytes": len(data)})


for f in sorted(Path(a.data).glob("*.fit")):
    base = bytearray(f.read_bytes())
    emit(f.name, "original", base)
    n = len(base)
    for m in range(a.per_file):
        b = bytearray(base)
        kind = rng.choice(["data", "data", "defs", "defs", "trunc"])
        if kind == "data":
            for _ in range(rng.randint(1, 6)):
                b[rng.randrange(14, n - 2)] = rng.randrange(256)
        elif kind == "defs":
            for _ in range(rng.randint(1, 3)):
                b[rng.randrange(14, min(300, n - 2))] = rng.randrange(256)
        else:
            cut = rng.randrange(60, n - 2)
            b = b[:cut] + bytearray(2)
            # keep header data_size consistent with the cut so the decoder reads a short valid stream
            ds = len(b) - b[0] - 2
            b[4:8] = ds.to_bytes(4, "little")
        emit(f.name, kind, fix(b))
if a.valid_dir:
    for f in sorted(Path(a.valid_dir).glob("*.fit")):
        emit(f.name, "valid", bytearray(f.read_bytes()))      # appended last: ids of the earlier entries do not change
(out / "index.json").write_text(json.dumps(index))
print("wrote", len(index), "files to", out)
