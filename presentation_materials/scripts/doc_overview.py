#!/usr/bin/env python3
"""overview_zh.md: project logic and main findings (numbers read from tables)."""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from docs_lib import *
from runsets import CONFIGS
CS = {r["config"]: r for r in tab("config_summary.csv")}; cc = {r["config"]: r for r in tab("correctness_by_config.csv")}
fp = {r["group"]: r for r in tab("fpr_summary.csv")}; cal = {r["pair"]: r for r in tab("calibration_pairs.csv")}; ns = jt("null_search_summary.json"); ss = jt("stacking_summary.json")
cs = {(r["control"], r["comparison"], r["batch"]): r for r in tab("controls_summary.csv")}
def mr(c, k="remeasured_speedup"): return f"{float(CS[c][k+'_median']):.3f} [{float(CS[c][k+'_min']):.3f}, {float(CS[c][k+'_max']):.3f}]"
o3 = [r for r in tab("controls_summary.csv") if r["comparison"].startswith("-O3 vs stock")]
nat = [r for r in tab("controls_summary.csv") if r["comparison"].startswith("-O3 -march=native vs stock") and r["valid_comparison"] == "True"][0]
h1 = [r for r in tab("controls_summary.csv") if "attempt 1" in r["comparison"]][0]; h2 = [r for r in tab("controls_summary.csv") if "attempt 2" in r["comparison"]][0]
L = []; w = L.append
w("# 总览(中文):项目逻辑与主要发现\n")
w("> 本文件只给逻辑主线和结论;每个数字的完整表格、算法和来源在 `evidence_zh.md`、`tables/`、`sources.csv`;图在 `figures/`。不按实验完成时间或作业编号组织;不同模型、算法、代码版本是**实验条件**:I1 = 原始种群搜索实现(Qwen),I2 = 排序规则的 greedy/best-of-N(DeepSeek),I3 = README 完整循环及匹配 best-of-N(两个模型)。\n")
w("## 一句话\n")
w("我们让两个大语言模型改写 Garmin FIT SDK 解码器里的函数,用一套经过校准的统计规则判断“是否真的更快”,用编译器选项、人工补丁和独立采样作对照,并用比课程自带检查更严格的测试检查结果是否仍然正确。**最高的加速(DeepSeek 的种群搜索/greedy,约 1.165–1.176 倍)确实存在且能被独立复测重复,但这些补丁没有一个在全部扩展测试下“无发现”;最安全的(人工补丁,1.068–1.082)和最简单的(best-of-N 的单点查表,≈1.07)速度提升更低。**\n")
w("## 研究逻辑(六步)\n")
w("1. **要回答什么:** LLM 驱动的补丁搜索能否得到真实、正确的加速,收益来自哪里?一个加速数字回答不了(噪声、种子运气、没有对照、可能不正确、成本不同)。\n2. **实现了什么:** 只写了 `src/Search.cpp`(函数选择、提示词、种群/greedy/best-of-N、判定规则、预算与续跑),其余五个程序用课程提供的。工作负载:解码 4 个活动文件(907,007 字节、34,251 条消息、428,714 个字段,校验值 92bebfd7f8978fc8),`g++ -O2`,E5-2620 v3 节点。\n3. **测量可信吗:** 规则 = 10 个进程 × 9 次重复,精确符号翻转 p < 0.01 且 ratio ≤ 0.98。校准:真实降幅 4.765% 的检出率 99/100,1% 为 1/100,2%(实际 1.965%,恰在门槛下)为 42/100;无变化对和变慢对 0/100 误判。误报:合成 null 0/500(上界 0.735%),真实 SDK 无效补丁 0/804(上界 0.458%,每个节点类别 0/402,上界 0.913%)。")
w(f"空搜索(36 个无变化候选 × 8 次):排序规则自己会“收获”{ns['false_progress_median']:.3f}%(最大 {ns['false_progress_max']:.3f}%)的假进步,最大单步 {ns['max_single_update_pct']:.3f}%——所以搜索中的小步不能当作证据,只有最终固定补丁的独立复测才是对外数字。\n")
w(f"4. **和谁比:** 编译器:`-O3` {float(o3[0]['median_speedup']):.3f},`-O3 -march=native` {float(nat['median_speedup']):.3f}(同一节点、各 5 次测量);人工补丁(`GetMesg`/`GetFieldIndex` 线性扫描改查表)attempt 1 = {float(h1['median_speedup']):.3f}、attempt 2 = {float(h2['median_speedup']):.3f};同一模型同预算(40 个请求)的 best-of-N 独立采样。\n5. **收益来自哪里:** best-of-N 的 10 个 DeepSeek 最终补丁**都只改一个函数 `Profile::GetMesg`**(线性扫描 → 查表,≈1.07);greedy/种群把更多函数的赢家叠起来(`FieldBase` 拷贝构造、`GetFieldIndex`、`GetValue`……)到 1.16–1.18。把 best-of-N 自己的候选直接叠起来(不再调用模型)固定 K=5 的中位数 {ss['median_K5']:.3f},填补了约 {100*ss['gap_closed_median_stack_K5_fixed']:.0f}% 的差距。\n6. **正确性边界:** 课程自带检查(4 个文件的校验值、profile 全域摘要、单线程)每个候选都过了;更严格的测试(合法文件差分、ASan/UBSan、4 线程 TSan)发现:很多补丁把表放在手写的 `static bool initialized` 里(竞争),greedy 链里的 `GetFieldIndex` 共享缓存会在多线程下返回错误结果;3 个种群搜索补丁在 SDK 编码器写出的**合法文件**上输出与原库不同(Qwen 种子 3:55 个里 45 个不同)。\n")
w("## 主要结果表(独立复测的固定最终补丁,5 个种子的中位数 [完整范围])\n")
rows = []
for cid, *_ in CONFIGS:
    c = cc[cid]
    rows.append([CFGNAME[cid], mr(cid), f"{float(CS[cid]['total_tokens_median']):,.0f}", f"{float(CS[cid]['course_metric_remeasured_median']):.2e}",
                 f"无发现 {c['no finding in tested conditions']} / 仅 TSan 竞争 {c['TSan race only']} / 仅变异文件不同 {c['differs only on hostile mutants']} / 错误输出·崩溃 {c['wrong output / crash / memory error']} / 未测 {c['not tested']}"])
w(md(rows, ["配置", "speedup 中位数 [范围]", "total tokens(中位数)", "(speedup−1)/tokens", "5 个最终补丁的扩展正确性状态"]) + "\n")
w("对照:`-O3` 1.090,`-O3 -march=native` 1.108(单节点);人工补丁 1.068 / 1.082(全部扩展测试无发现,语料不含合法编码器文件);best-of-N 叠加 K=2/3/5:1.127 / 1.143 / 1.158,事后最佳 K 1.187(事后选择)。\n")
w("同一模型内的搜索 vs best-of-N(5 对 5,不配对,探索性):**DeepSeek** 两个版本都是完全分离,Mann–Whitney p = 0.0079(Holm 校正 0.032);**Qwen** 两个版本都无可靠差异(p = 0.69 与 0.31)。跨模型的差别不能归因于算法。\n")
w("## 回答八个问题\n")
w(md([
 ["我们确实建立并验证了什么测量能力?", "一套带精确 p 值和 2% 门槛的判定规则,经已知比例校准(0/100 误判无变化与变慢;4.8% 下降 99% 检出)、合成 null 0/500 和真实 SDK 无效补丁 0/804 的误报检验;并量化了排序规则在纯噪声下会虚构 ≈0.08% 的进步。校准只在一个节点,检出率只有 4 个点。"],
 ["哪种搜索在什么条件下成绩更高?", "只有 **DeepSeek** 上,带继承的搜索(种群、greedy)显著高于同预算的独立采样(1.165–1.176 对 1.073);Qwen 上没有可检出差异。更高的代价:token 多 15%–79%、耗时更长。"],
 ["编译器、人工、独立采样、组合各解释了什么?", "`-O3` 1.09、native 1.108 只改选项就超过所有 best-of-N(≈1.07);人工两个补丁 1.068/1.082 与 best-of-N 同量级;best-of-N 全是单个函数的查表;叠加多个独立赢家解释了 greedy 与 best-of-N 差距的约八成(固定 K=5),但不是全部。"],
 ["哪些速度收益通过了哪些正确性检查?", "全部过了课程自带检查。扩展测试下:人工 2/2、I2 best-of-N 种子 2、Qwen I3 的 4 个补丁(其中 1 个经静态阅读含未同步惰性初始化,TSan 漏报)在各自测试条件下无发现;DeepSeek 种群/greedy 的 10 个补丁里 9 个测过、0 个无发现:3 个有错误输出/崩溃/合法文件输出不同,1 个仅变异文件输出不同,5 个仅 TSan 竞争;1 个(greedy 种子 3 的 40 请求最终补丁)未测。详见 evidence §7。"],
 ["哪些结论受样本数、成本、节点、输入范围或测试覆盖限制?", "5 个种子;节点类别与种子不平衡;I1 请求数不可核实;DeepSeek 有 58 个无 usage 的 502;正确性语料 459 个文件、TSan 24 个文件;I1 补丁未测;组合只用 I2 候选;C2 无计时。"],
 ["哪些结果与预期不同,最值得展示?", "见下面三个候选核心发现。"]],
 ["问题", "回答"]) + "\n")
w("## 最多三个“老师最不应该错过”的核心发现候选(按推荐顺序)\n")
w("### 候选 1:加速最高的补丁在扩展测试下都有发现,而人工补丁没有\n")
w("- **一句话:** 搜索找到的最大加速(1.165–1.176)靠的是叠加多个函数的改动,而这些补丁里没有一个在全部扩展测试下“无发现”,人工写的两个补丁(1.068/1.082)却没有发现。\n- **数字:** DeepSeek 种群/greedy 10 个最终补丁:9 个测过,无发现 0;错误输出/崩溃/合法文件不同 3(greedy 种子 1、DeepSeek 种群种子 1 与 2),仅变异文件不同 1(greedy 种子 4),仅 TSan 竞争 5;Qwen I3 种群:合法文件上 45/55 与 4/55 个输出不同。greedy 种子 3 链第 3 步(`GetFieldIndex` 共享缓存)起,4 线程下 36–39/48 次与单线程不一致。人工补丁:全部测试无发现(语料 A)。\n- **最适合的图/表:** `fig1_seed_results_with_correctness`(每个种子的 speedup 与正确性标记)+ `fig5_chain_seed3`(哪一步开始出错)。\n- **必须同时说的限制:** 课程自带检查全部通过,扩展测试不是搜索当时的准入规则;TSan 只报告实际发生的竞争(有漏报);问题的具体原因只在 greedy 链第 3 步确认,其余没有隔离;I1 的 10 个补丁与 greedy 种子 3 的最终补丁没测;人工补丁的测试语料不含合法编码器文件。\n")
w("### 候选 2:DeepSeek 上“搜索”确实比独立采样好,但很大一部分只是“把多个函数的赢家叠起来”\n")
w(f"- **一句话:** 在 DeepSeek 上,有继承的搜索(1.165/1.176)显著高于同样 40 次请求的独立采样(1.073,5 对 5 完全分离);把独立采样自己的候选叠起来就能追回约八成差距;在 Qwen 上没有可检出差异。\n- **数字:** Mann–Whitney p = 0.0079(Holm 后 0.032);叠加 K=2 / 3 / 5 / 事后最佳 K:{ss['median_K2']:.3f} / {ss['median_K3']:.3f} / {ss['median_K5']:.3f} / {ss['median_bestK_posthoc']:.3f};best-of-N 的 10 个最终补丁全是 `Profile::GetMesg`;请求数相同,token 多 15%–79%。\n- **最适合的图/表:** `fig1`(分组比较)、`fig6_stacking`(叠加曲线)、`fig9_request_funnel`(40 个请求实际去了哪里)。\n- **必须同时说的限制:** 5 个种子;没有对反馈、选择、继承做逐项消融,不能说哪个起作用;叠加用的是搜索时排序,事后最佳 K 有乐观偏差;跨模型不能归因于算法;Qwen 的“没有差异”不等于“相同”。\n")
w("### 候选 3:测量本身是可信的——但小步不能当证据\n")
w(f"- **一句话:** 我们的判定规则经已知比例校准,在 1300 多个无变化测量(合成 500 + 真实 SDK 804)里没有一次误报;但搜索里用来选“下一步”的排序规则在纯噪声下会虚构 0.06–0.11% 的进步,所以只有最终固定补丁的独立复测才可靠。\n- **数字:** 校准:真实降幅 4.765% → 99/100;1% → 1/100;2%(实际 1.965%)→ 42/100;无变化与变慢 0/200。误报:合成 null 0/500(上界 0.735%),SDK 无效补丁 0/804(每类 0/402,上界 0.913%);p 值单独会通过 7/500 与 11/804 但被 2% 门槛挡住 3 与 6 次。空搜索 8 次 × 36 候选:24 次更新,累计假进步中位数 {ns['false_progress_median']:.3f}%、最大 {ns['false_progress_max']:.3f}%;真实 greedy 链 51 次更新里 15 次不大于 0.2%。\n- **最适合的图/表:** `fig2_calibration_detection`、`fig3_false_accept_bounds`、`fig8_null_search_steps`。\n- **必须同时说的限制:** 校准只在一个节点(xcnc2)、只有 4 个效应点;合成 null 的 xcnd 只有 200 个;空搜索的最大漂移不是噪声上限,不能据此断言超过它的步骤一定真实。\n")
w("## 还需要你们决定的\n")
w("- 汇报只能选少数点:我建议主线 = 候选 2 的“搜索 vs 独立采样”(因为它直接回答课程问题),把候选 1 作为“边界”,候选 3 用一张校准/误报图一带而过。\n- 候选 1 的“补丁被发现有问题”的措辞要避免写成“原先没有按课程要求检查”;课程自带检查都做了。\n")
(PM / "overview_zh.md").write_text("\n".join(L))
print("overview ok")
