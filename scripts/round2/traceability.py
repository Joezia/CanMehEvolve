#!/usr/bin/env python3
"""Round 2: per-run traceability table (runs/round2/TRACEABILITY.md): which jobs, nodes, code and binary produced every run, and the final patch hash."""
import glob, json, re
from pathlib import Path
R2 = Path(__file__).resolve().parent.parent.parent / "runs/round2"


def kv(path):
    d = {}
    for l in open(path, errors="replace"):
        for m in re.finditer(r"(\w+)=(\S+)", l):
            d.setdefault(m.group(1), m.group(2))
    return d


L = ["# Round 2: traceability per run", "",
     "Segment = one Slurm job of the self-managing chain (host, start, end). Final = the separate job that re-measured the fixed final patch three times. `Search.cpp` and binary hashes are the ones recorded by the segment jobs.", "",
     "| run | chain | segment jobs (host, start -> end) | final-evaluation job (host) | code commit(s) | Search.cpp sha256 | binary sha256 | best.patch sha256 | HTTP requests |", "|---|---|---|---|---|---|---|---|---|"]
for spec in sorted(glob.glob(str(R2 / "chains/[A-D].txt"))):
    for line in open(spec):
        if not line.strip():
            continue
        rid = json.loads(line)["id"]
        d = R2 / "runs" / rid
        segs, commits, sc, bn = [], [], set(), set()
        for f in sorted(glob.glob(str(d / "segments/*.node.txt"))):
            k = kv(f)
            segs.append("%s (%s, %s -> %s)" % (k.get("job"), k.get("host"), k.get("start", "")[5:16], k.get("end", "")[5:16]))
            commits.append(k.get("git_commit", "")[:7]); sc.add(k.get("search_cpp_sha256", "")[:12]); bn.add(k.get("binary_sha256", "")[:12])
        fk = kv(d / "final/node.txt") if (d / "final/node.txt").exists() else {}
        bp = ""
        for l in open(d / "final/node.txt", errors="replace") if (d / "final/node.txt").exists() else []:
            if l.strip().endswith("best.patch"):
                bp = l.split()[0][:12]
        s = json.load(open(d / "summary.json"))
        L.append("| %s | %s | %s | %s (%s) | %s | %s | %s | %s | %s |" % (rid, Path(spec).stem, "; ".join(segs), fk.get("job", "-"), fk.get("host", "-"), ",".join(sorted(set(commits))),
                                                                      ",".join(sorted(sc)), ",".join(sorted(bn)), bp or "-", s.get("http_attempts")))
(R2 / "TRACEABILITY.md").write_text("\n".join(L) + "\n")
print("\n".join(L[:8]))
