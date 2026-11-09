#!/usr/bin/env python3
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from pm_lib import *
parts = ["evidence_zh.part_a.md", "evidence_zh.part_b1.md", "evidence_zh.part_b2.md", "evidence_zh.part_c1.md", "evidence_zh.part_c2.md", "evidence_zh.part_d.md"]
txt = "\n\n".join((PM / "intermediate" / p).read_text() for p in parts)
(PM / "evidence_zh.md").write_text(txt + "\n"); print(len(txt))
