#!/usr/bin/env python3
"""evidence_zh.md, part B: measurement trust (section 3) and controls (section 4)."""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from docs_lib import *
L = []; w = L.append
w("## 3. 我们的测速和判断可信吗?\n")
w("### 3.1 统计量的含义和当前实际规则\n")
w(md([
 ["一次测量", "10 个独立进程 × 每进程 9 次重复(`--repeat 10 --repetitions 9`);每个进程里原库与候选交替计时,约一半进程先测候选(`swapped`)以抵消顺序效应;每次重复内部迭代到至少 min-time(0.25 s,校准对按工作量缩放)。"],
 ["进程比值", "进程 p 的 `ratio_p = median(候选 9 次耗时) / median(原库 9 次耗时)`"],
 ["ratio、speedup", "`ratio = median_p(ratio_p)`;`speedup = 1 / ratio`;下降 % = 1 − ratio;提高 % = speedup − 1"],
 ["p 值", "对 `log(ratio_p)` 的 10 个值做**精确符号翻转检验**(2¹⁰ = 1024 种符号组合,双侧);最小可能 p = 2/1024 = 0.00195"],
 ["“判为更快”", "三个条件同时成立:平均 log 比 < 0(方向);p < α = 0.01(统计);ratio ≤ 0.98(幅度,即至少 2% 下降,`--min-effect 0.02`)"],
 ["不稳定", "进程比值的极差(最大 − 最小)> 0.25 视为不稳定:不更新记录,且会触发复测"],
 ["推断单位", "10 个**进程**(独立的 OS 进程,各自重新加载库),不是 90 次重复;所以 9 次重复之间的自相关不直接进入 p 值,只影响各进程中位数的噪声"]],
 ["量", "定义(`src/Search.cpp:384` `analyzeTimings`,`:364` `signFlipPValue`)"]) + "\n")
w("**三个层次不要混淆:**\n")
w(md([
 ["① 搜索中的排序(greedy / best-of-N,I2)", "第一次测量 r1 稳定且 < 记录 → 第二次测量 r2;`R = max(r1, r2)`;`R < 记录` 才更新。**没有 p 值检验、没有 2% 门槛**。作用是挑出“看起来更好”的候选"],
 ["② 搜索中的双次确认(种群搜索、匹配 best-of-N,I1/I3)", "第一次测量满足规则(或不稳定)才做第二次;两次都满足规则才记为 `confirmed`;候选的 ratio 取两次中**较差**的那个"],
 ["③ 最终独立复测", "一次运行结束后,把**固定的最终补丁**在单独作业里再完整测 3 次(每次 10×9);报告 3 次 ratio 的中位数对应的 speedup 和通过规则的次数。这是对外报告的数字"]],
 ["层次", "做法"]) + "\n")
w("我们用独立的 Python 实现重放了仓库里**所有**保存了原始 timings 的测量(Phase 0 的 680 个有效试验、全部误报测量、控制、搜索中和复测中的测量),决定与 C++ 保存值的差别:Phase 0 的 681 个文件重放与已存的逐试验结果 **0 条不一致**(其中 1 个文件损坏不可读,已排除并计数)。\n")

w("### 3.2 A. 已知真实比例的校准实验\n")
w("校准对由课程提供:原库和候选库做完全相同的事,只是候选的循环次数是原库(20000 单位)的 `候选单位/20000`;**精确真实比例 = 候选单位 / 参考单位**(假设耗时与工作量成正比,由下表偏差检验)。主要六对各做 100 个有效试验(两个批次、同一节点 xcnc2,各 50),4 个 sweep 对各 20 个(只做了批次 1)。一个 null 试验文件损坏,被排除并计数,所以 null 是 100 个有效试验。\n")
cal = tab("calibration_pairs.csv")
rows = [[r["pair"], f"{r['reference_units']}/{r['candidate_units']}", f(r["true_ratio_exact"], 5), f(r["true_reduction_pct"], 3) + "%", r["valid_trials"], r["judged_faster"],
         pct(r["rate"]), f"[{100*float(r['cp95_lo']):.3f}%, {100*float(r['cp95_hi']):.3f}%]", f(r["median_reported_ratio"], 5), f"{float(r['abs_bias']):+.5f}", f"{float(r['rel_error_pct']):+.3f}%"] for r in cal if r["pair"] in ("null", "faster-1-percent", "faster-2-percent", "faster-5-percent", "faster-10-percent", "slower-10-percent")]
w(md(rows, ["校准对", "参考/候选工作量", "精确真实比", "真实降幅", "有效试验", "判为更快", "比例", "95% CP 区间", "中位报告比", "绝对偏差", "相对误差"]) + "\n")
w("判为更快 = 单次完整测量(10×9)满足三个条件。区间为精确 Clopper–Pearson 双侧 95%。绝对偏差 = 中位报告比 − 精确真实比;相对误差 = 绝对偏差 ÷ 精确真实比。\n")
w("**四个加速点的检出率:** 1% → 1/100 (1.0%);2% → 42/100 (42.0%);5% → 99/100 (99.0%);10% → 100/100 (100.0%)。**已测点中达到 90% 检出率的最弱效应是 faster-5-percent(真实降幅 4.765%,speedup 1.050)**;分辨率只到已测的四个点。注意 faster-2-percent 的真实降幅是 1.965%,**略小于 2% 的幅度门槛**,所以 52/100 的试验 p 值通过但被幅度门槛挡住(见下表拒绝原因),42% 的检出率是“真实效应刚好在门槛边缘”的结果,不能说成“2% 能可靠检出”。\n")
w("**拒绝原因(互斥分类;D = 方向通过,P = p<0.01,M = ratio≤0.98):**\n")
rows = []
for r in cal:
    if r["pair"] in ("null", "faster-1-percent", "faster-2-percent", "faster-5-percent", "faster-10-percent", "slower-10-percent"):
        names = {"---": "三项都未通过", "D--": "仅方向通过", "DP-": "方向+p 通过,幅度未过", "DPM": "三项都通过(判为更快)", "-P-": "p 通过但方向为慢", "D-M": "方向+幅度通过,p 未过", "-PM": "p+幅度通过,方向未过", "--M": "仅幅度通过"}
        pat = json.loads(r["gate_patterns_DPM"]); rows.append([r["pair"], ";".join(f"{names.get(k, k)} {v}" for k, v in sorted(pat.items(), key=lambda kv: -kv[1]))])
w(md(rows, ["校准对", "各类试验数(键 = 通过的门槛;“-”表示该门槛未通过)"]) + "\n")
w("**sweep 对**(批次 1,各 20 个试验;候选工作量是原库的 1.05、1.10、2、4 倍;它们都比原库**慢**,正确地全部不被判为更快)。它们的用途是检查**比例估计随工作量缩放是否保持准确**——不是检出率:\n")
rows = [[r["pair"], f"{r['reference_units']}/{r['candidate_units']}", f(r["true_ratio_exact"], 5), r["valid_trials"], r["judged_faster"], f(r["median_reported_ratio"], 5), f"{float(r['abs_bias']):+.5f}", f"{float(r['rel_error_pct']):+.3f}%"] for r in cal if r["pair"].startswith("sweep")]
w(md(rows, ["对", "工作量", "精确真实比", "有效试验", "判为更快", "中位报告比", "绝对偏差", "相对误差"]) + "\n")
w("相对误差在 +0.04% 到 +0.64% 之间,随比例增大略增(估计比真实值略高,即略偏保守)。`sweep-110` 与 `slower-10-percent` 是同一配置的两个独立测量序列(中位报告比 1.10048 与 1.10090)。\n")
w("**两个故意错误的校准对**(应该被课程自带的检查拒绝,而不是给出一个数字):\n")
rows = [[r["pair"], r["expected_stage"], r["observed_stage"], r["message"][:110]] for r in tab("calibration_wrong_pairs.csv")]
w(md(rows, ["对", "期望被拒绝的阶段", "实际被拒绝的阶段", "拒绝信息"]) + "\n")
w("**单次判定 vs 双次确认(离线配对)。** 双次确认**不是**搜索里实际执行的流程,而是对已有单次试验的离线配对:同一批次、同一校准对内,按试验序号连续配对 (t1,t2)、(t3,t4)……,两个都通过才算接受。配对方式在看到任何 Phase 0 数据之前写进分析脚本(`scripts/analyze_phase0.py`),没有按结果挑选;配对数 = 50(每对),所以分母和单次判定(100 个试验)不同,不能混为同一个试验数量:\n")
rows = [[r["pair"], f"{r['judged_faster']}/{r['valid_trials']} = {pct(r['rate'])}", f"{r['two_stage_accepted']}/{r['two_stage_pairs']} = {pct(int(r['two_stage_accepted'])/int(r['two_stage_pairs']))}", f"[{100*float(r['two_stage_cp_lo']):.2f}%, {100*float(r['two_stage_cp_hi']):.2f}%]"] for r in cal if r["pair"] in ("null", "faster-1-percent", "faster-2-percent", "faster-5-percent", "faster-10-percent", "slower-10-percent")]
w(md(rows, ["校准对", "单次判定", "离线双次确认", "双次确认 95% CP"]) + "\n")
w("校准的局限:只在一个节点(xcnc2)、一个时间段做了 100 个试验;sweep 只有 20 个;检出率的分辨率只到 1%、2%、5%、10% 四个点。xcnd 节点的表现靠 §3.3 的 null 与 SDK 测量补充。\n")

w("### 3.3 B. 合成 null 与真实 SDK 的无效补丁\n")
w("两类数据**不混成一个误报率**:合成 null 是课程提供的“原库 vs 同一代码”的校准对(没有任何 SDK 因素);SDK inert 是在真实 SDK 里加一行注释的补丁(`runs/inert-check/inert.patch`,只改 `src/fit.cpp` 的一行注释和一个空行),经 `CanMehHarness` 的完整编译链路,等于“真实库、真实编译”下的 null。**机器码核查:** 该无效补丁和 16 个具有代表性的空搜索候选(每个空搜索运行的“最后一次被接受”和“最后一次测量”的候选)构建出的库,`.text` 段与原库逐字节相同,动态符号表也相同(17/17;`runs/round2/fpr/noop-verification-*`)——代码确实没有变化,所以任何“更快”的判定都是误报。288 个空搜索候选里只核查了这 16 个。\n")
fp = tab("fpr_summary.csv")
GN = {"Synthetic null": "合成 null", "calibration batches": "校准批次", "extra batches": "补充批次", "SDK inert": "SDK 无效补丁", "batch group A": "批次组 A", "batch group B": "批次组 B", "all batches": "全部批次", "both classes": "两类合并", "controls job": "控制作业", "hand-run measurements": "手工测量", "all xcnc": "全部 xcnc", "all xcnd": "全部 xcnd", "all": "全部"}
def gname(g):
    for k in sorted(GN, key=len, reverse=True): g = g.replace(k, GN[k])
    return g
rows = [[gname(r["group"]), r["valid_measurements"], r["false_accepts"], f"[0.000%, {100*float(r['cp95_hi']):.3f}%]", r["p_below_alpha_any_direction"], r["p_pass_and_direction_ok_but_blocked_by_2pct_gate"], r["unstable"],
         f"{float(r['ratio_median']):.5f} [{float(r['ratio_min']):.5f}, {float(r['ratio_max']):.5f}]", f"{float(r['lag1_ac_median_of_measurement_medians']):.3f} [{float(r['lag1_ac_min']):.2f}, {float(r['lag1_ac_max']):.2f}]"] for r in fp]
w(md(rows, ["组", "有效测量", "误接受", "95% CP", "p<0.01(任一方向)", "方向、p 通过但被 2% 门槛挡住", "unstable", "ratio 中位数 [最小, 最大]", "lag-1 自相关 中位数 [最小, 最大]"]) + "\n")
w("**这些数字怎么读:**\n")
w("- 所有分组误接受都是 0。**95% 上界是否低于 1% 要看分组**:合成 null 合并(500)为 0.735%(低于 1%);但 xcnc 单类 300 个为 1.22%、xcnd 单类 200 个为 1.83%、校准批次的 100 个为 3.62%(都不低于 1%)。SDK 无效补丁每个节点类别 402 个为 0.913%(低于 1%);两类合并 804 个为 0.458%。\n- p 值单独使用时并非没有误报:500 个合成 null 里有 7 个 p<0.01(与双侧 α = 1% 的期望 5 个相符),其中 3 个方向为快、但 ratio 高于 0.98 而被 **2% 幅度门槛挡住**;804 个 SDK 无效测量里 11 个 p<0.01,其中 6 个被幅度门槛挡住。也就是说**幅度门槛实际挡住了单靠 p 值会产生的假阳性**。\n- 无效补丁的 ratio 全部落在 [0.9971, 1.0024](SDK)和 [0.9852, 1.0138](合成 null)之内,远离 0.98;没有 unstable。\n- 批次明细(每个批次的节点、作业号、计数)在 `tables/fpr_by_batch.csv`(27 个批次)。\n")
w("**自相关(lag-1)怎么统计的:** 每个测量有 10 个进程;对每个进程的候选 9 次重复耗时序列算 lag-1 自相关(用序列自己的均值),取 10 个进程的**中位数**得到“这个测量的自相关”;上表是这些测量级数值的中位数与 [最小, 最大]。长度 9 的序列,样本自相关即使完全独立也有约 −1/9 ≈ −0.11 的偏差,合成 null 的 −0.111 正好如此;SDK 在 xcnd 上为 +0.150、在 xcnc 上为 +0.013,可能说明 xcnd 上重复之间有轻微的缓慢漂移(没有进一步调查原因)。搜索中全部 977 次测量的自相关中位数为 0.027,范围 [−0.33, 0.52]。\n")

w("### 3.4 C. 无实质优化的空搜索\n")
w("**做法:** 把 I2 的排序规则(记录更新:r1 稳定且 < 记录 → r2 → `R = max(r1,r2) < 记录`)用在“什么都不改”的候选上——模型被替换成往随机函数里插一行注释。**8 个运行**(xcnc 4 个、xcnd 4 个,种子 1–4),每个运行测量 36 个候选。没有任何模型调用。\n")
ns = jt("null_search_summary.json"); nr = tab("null_search_runs.csv")
w(md([[r["run"].replace("null-search-", ""), r["node"], r["measured_candidates"], r["updates"], f"{float(r['false_progress_pct']):.4f}%", f"{float(r['false_speedup']):.5f}", f"{float(r['max_single_update_pct']):.4f}%"] for r in nr],
     ["运行", "节点", "测量的候选数", "记录更新次数", "累计假进步", "对应 speedup", "最大单步更新"]) + "\n")
w("**指标:** 单步更新 = 100 × (1 − R_新 / R_前),单位 %(相对前一个记录);累计假进步 = 100 × (1 − 最终记录),单位 %(ratio 下降的百分点);speedup = 1/最终记录。\n")
w(f"**结果:** 8 个运行共 {ns['total_updates']} 次更新(每运行 2–4 次);单步更新中位数 {ns['median_single_update_pct']:.3f}%,最大 {ns['max_single_update_pct']:.3f}%;累计假进步中位数 {ns['false_progress_median']:.3f}%,最大 {ns['false_progress_max']:.3f}%;没有任何空候选在单次测量中通过完整规则。\n")
w(f"**与真实搜索比较(比较的是 DeepSeek greedy 的 5 个运行、40 请求时的全部 {ns['real_greedy_steps']} 次记录更新):** 真实更新的中位数为 {ns['real_median_step_pct']:.2f}%,最大 {ns['real_max_step_pct']:.2f}%;其中 {ns['real_steps_leq_max_null_step']}/{ns['real_greedy_steps']} 次不大于空搜索观察到的最大单步(0.063%),{ns['real_steps_leq_0.2pct']}/{ns['real_greedy_steps']} 次不大于 0.2%,{ns['real_steps_leq_0.5pct']}/{ns['real_greedy_steps']} 次不大于 0.5%。也就是说,**真实 greedy 链里相当一部分早期小步(尤其 0.2% 以下)在大小上与纯噪声产生的更新不可区分**;大步(几个百分点)远超噪声。\n")
w("**不能怎么用这个结果:** 8 个运行里观察到的最大漂移(0.109%)和最大单步(0.063%)**不是通用的噪声上限**——只有 8×36 个候选、4 个种子、两类节点;不能据此断言“超过它的步骤一定是真实改进”,也不能断言“低于它的步骤一定是噪声”。它只说明:排序规则本身在没有 2% 门槛和显著性检验时,会在 36 个候选里“收获”约 0.06–0.11% 的虚假进展。\n")
(PM / "intermediate" / "evidence_zh.part_b1.md").write_text("\n".join(L))

# ---------------------------------------------------------------- 4
L = []; w = L.append
w("## 4. 编译器与人工优化能做到什么?\n")
w("### 4.1 C1:编译器选项\n")
w("原库和候选都用 `g++ -O2 -std=c++17`。C1 在**同一节点(xcnd24)**上,把整个库分别用 `-O2`、`-O3`、`-O3 -march=native`(解析为 haswell)重新编译,用同样的 `measure-pair` 计时,每个比较重复 5 次测量。“批次”指不同的 Slurm 作业:`-O3` 比 `-O2` 在两个批次里各测了一次;`-march=native` 的第一个批次的初始化失败(`init-O3native.json` 里 ok=false),其 ratio 恒为 1.0 不是比较,已作废并由第二个批次取代。\n")
cs = tab("controls_summary.csv")
rows = [[r["comparison"], r["batch"], r["node"], r["n_measurements"], f(r["median_ratio"], 4), f(r["median_speedup"], 4), f"[{float(r['speedup_min']):.4f}, {float(r['speedup_max']):.4f}]", f"{r['passes_rule']}/{r['n_measurements']}"] for r in cs if r["control"] == "C1"]
w(md(rows, ["比较", "批次", "节点", "测量次数", "ratio 中位数", "speedup 中位数", "speedup 范围", "通过规则次数"]) + "\n")
w("**读法:** `-O3` 给出约 1.09(两个批次 1.0911 与 1.0898,在各自范围内重合),`-O3 -march=native` 给出 1.1084;native 相对 `-O3` 的直接比较为 1.0140(5 次测量都没过 2% 门槛,范围很窄)。同一作业里间接推得 1.1084/1.0898 = 1.0171,与直接测得的 1.0140 相差 0.3 个百分点,说明这些单节点、5 次测量的数字各自有约 ±0.2% 的不确定。注意:所有 C1 比较都来自同一个节点 xcnd24,没有跨节点重复;表里的绝对毫秒数(在 `tables/controls_summary.csv`)来自不同批次/节点,不应直接比较。\n")
w("### 4.2 C2:人工优化(重新阅读了实际补丁)\n")
hp = json.load(open(T / "human_patch_facts.json"))
w(f"两个人工补丁都只改 `src/fit_profile.cpp`(补丁文件:`runs/human-control/c2-1058781/attempt-1.patch`、`attempt-2.patch`):尝试 1 改 1 处({hp['attempt-1']['added_lines']} 行加、{hp['attempt-1']['removed_lines']} 行减);尝试 2 改 2 处({hp['attempt-2']['added_lines']} 行加、{hp['attempt-2']['removed_lines']} 行减),包含尝试 1 的全部改动。\n")
w("**改了什么(以实际补丁为准):**\n")
w(f"1. `Profile::GetMesg(num)`(两个补丁都有)。**原来:** 对 `mesgs[]` 数组(共 {hp['MESGS_entries_in_fit_profile.cpp']} 个消息类型)线性扫描,逐个比较 `mesgs[i].num == num`,找到就返回。解码时对每条消息都会调用(它是 profile 里最热的函数,约占样本的 19%)。**修改后:** 第一次调用时建一个 65536 项的指针表 `byNumber[消息号]`(每项指向对应的 `MESG`,没有则为空),之后每次查找是一次数组读。**为什么减少了工作:** 原来最坏要比较 124 次(具体次数取决于消息号在数组中的位置),现在是 1 次内存读取。一个简单例子:找消息号 20(record 消息)——原来从第 0 项开始逐项比较直到命中;现在直接读 `byNumber[20]`。\n")
w("2. `Profile::GetFieldIndex(mesgNum, fieldNum)`(仅尝试 2)。**原来:** 先 `GetMesg`,再对该消息的字段数组线性扫描找 `fields[i].num == fieldNum`。**修改后:** 建一张 `[消息类型][256]` 的字段号→下标表(124 × 256 × 2 字节),直接查表。\n")
w("**为什么人工版本与部分模型版本在并发安全性上不同。** 两个人工补丁把表放在函数内的 **`static const LookupTable table;`**——一个带构造函数的静态局部对象。C++11 保证这种静态局部对象的初始化是**线程安全的一次性初始化**,多线程同时第一次调用也只有一个线程执行构造,其余等待。大部分模型补丁写的是 `static bool initialized = false;` 加手写的 `if (!initialized) { 建表; initialized = true; }`:两个线程同时第一次调用会同时建表、同时读写 `initialized`,是数据竞争;另一些补丁(如 greedy 链的 `GetFieldIndex` 缓存 `cachedMesg`)在**后续每次调用**里改写共享的静态变量,即使不是第一次调用也会竞争并可能返回错误的下标(§7 中 4 线程测试里,链上第一次出现并发错误输出的补丁正是新增这类缓存的那一步)。课程自带检查只在单线程里解码、并检查候选自己不开线程,所以不会发现这类问题。\n")
w("**结果:**\n")
rows = [[r["comparison"], r["n_measurements"], f(r["median_speedup"], 4), f"[{float(r['speedup_min']):.4f}, {float(r['speedup_max']):.4f}]", f"{r['passes_rule']}/{r['n_measurements']}", r["node"]] for r in cs if r["control"] == "C2"]
w(md(rows, ["人工补丁", "测量次数", "speedup 中位数", "范围", "通过规则", "节点"]) + "\n")
w("两个补丁都是在一个作业(1068897,xcnd24)里各测 5 次,没有跨节点或跨批次的重复测量。**扩展正确性:** 两个补丁在 §7 的全部测试条件下(与原库差分、ASan/UBSan、4 线程 TSan)都没有发现问题(见 §7 总表;该测试语料不含 SDK 编码器写出的合法文件,只含 4 个原始文件和 400 个变异文件)。\n")
w("**人工时间证据的实际情况:** 课程要求“一个计时的小时”。仓库里**没有计时器记录**,只有文件时间戳:热点分析文件 `c2-1054632/hotspots.txt` 在 11 月 1 日 16:29;两个补丁文件在 11 月 2 日 10:30 和 10:51(整个人工环节的文件时间约 10:20–11:11,约 51 分钟)。**这不能证明满足“计时一小时”**,所以报告里不陈述已计时。AI 辅助说明:人工补丁是**人工指导、AI 辅助**完成的(代码、脚本由 Claude Code 在作者指导下编写),具体哪几行由谁键入没有记录。\n")
w("**与搜索结果对照:** 人工补丁(1.068、1.082)与 DeepSeek 的 best-of-N(中位数 1.073)属同一量级;`-O3`(1.090)和 `-O3 -march=native`(1.108)只改编译选项就超过了所有 best-of-N 配置和人工尝试 1;只有 DeepSeek 的种群搜索与 greedy(中位数 1.165–1.176)明显高于编译器选项。编译选项与源码补丁能否叠加没有测试。\n")
(PM / "intermediate" / "evidence_zh.part_b2.md").write_text("\n".join(L))
print("ok")
