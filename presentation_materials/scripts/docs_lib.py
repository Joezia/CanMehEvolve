"""Helpers shared by the document generators: load tables, render markdown tables."""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from pm_lib import *
T = PM / "tables"
def tab(name): return list(csv.DictReader(open(T / name)))
def jt(name): return json.load(open(T / name))
def f(x, nd=3):
    try: return f"{float(x):.{nd}f}"
    except Exception: return str(x)
def pct(x, nd=1):
    try: return f"{100*float(x):.{nd}f}%"
    except Exception: return str(x)
def md(rows, header=None, align=None):
    """rows: list of lists of str; header: list of str."""
    out = []
    esc = lambda c: str(c).replace("|", "\\|")
    rows = [[esc(c) for c in r] for r in rows]
    if header:
        out.append("| " + " | ".join(header) + " |"); out.append("|" + "|".join("---" for _ in header) + "|")
    for r in rows: out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)
CFGNAME = {
 "qwen_pop_I1": "Qwen 种群搜索 (I1)", "qwen_bon_I1": "Qwen best-of-N (I1)", "qwen_pop_I3": "Qwen 种群搜索 (I3, README 循环)", "qwen_bon_I3": "Qwen best-of-N (I3, 匹配对照)",
 "ds_greedy_I2": "DeepSeek greedy 单链 (I2)", "ds_bon_I2": "DeepSeek best-of-N (I2, 排序规则)", "ds_pop_I3": "DeepSeek 种群搜索 (I3, README 循环)", "ds_bon_I3": "DeepSeek best-of-N (I3, 匹配对照)"}
