#!/usr/bin/env python3
"""evidence_zh.md, part C: search vs independent sampling (section 5) and origin of the gain (section 6)."""
import sys, collections; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from docs_lib import *
from runsets import CONFIGS, CFG
R = tab("runs_all.csv"); CS = {r["config"]: r for r in tab("config_summary.csv")}
L = []; w = L.append
w("## 5. 搜索是否优于独立采样?\n")
w("### 5.1 每个配置的定义\n")
rows = [
 ["qwen_pop_I1", "qwen3-coder-next(只有一次探测请求记录了返回的模型 id,同名)", "I1(`archive/qwen-experiment/Search.cpp`,sha256 ce80cd7b…)", "种群 ≤ 6、锦标赛、失败重试、25% 收益分支;确认规则;20 s 采样,10% 均匀", "temperature 0.8,max_tokens 4096;预算 40 次模型调用(提供的客户端可能隐藏重试,HTTP 请求数未记录)"],
 ["qwen_bon_I1", "同上", "I1", "每次从原库;无反馈;确认规则", "同上"],
 ["qwen_pop_I3", "qwen3-coder-next(每个请求都记录,同名)", "I3(sha256 9431cd44…)", "同种群搜索;25% 收益分支", "temperature 0.8,max_tokens 4096,HTTP 超时 180 s,1 次尝试;预算恰好 40 个 HTTP 请求"],
 ["qwen_bon_I3", "同上", "I3", "匹配对照:同模型同提示同参数,每次从原库,无历史无反馈,确认规则", "同上"],
 ["ds_greedy_I2", "请求 deepseek-v4.1-flash;每个响应返回 **deepseek-v4.1-flash-1017**(已强制核对)", "I2(`d5aa9e7`,sha256 67935a2f…;续跑用 `Search_resume.cpp`)", "单条累计链;排序规则;无失败反馈;不种群", "temperature 0.8,max_tokens 32768,HTTP 超时 600 s;预算 40 个 HTTP 请求(种子 1、3、4、5 在作业时限处停在 39、38、34、34,由续跑补足)"],
 ["ds_bon_I2", "同上", "I2", "每次从原库;排序规则(记录最好一次);无反馈", "同上(种子 1 的作业时限 9600 s)"],
 ["ds_pop_I3", "同 DeepSeek", "I3", "种群搜索 + 25% 收益分支 + 失败重试;确认规则", "同 DeepSeek 参数;预算恰好 40 个 HTTP 请求;每个运行 2 段 Slurm 作业(续跑,跨节点时重测种群)"],
 ["ds_bon_I3", "同 DeepSeek", "I3", "匹配对照:每次从原库,无历史无反馈,确认规则", "同上(1 段)"]]
w(md(rows, ["配置", "模型(实际模型 id)", "代码版本", "算法", "关键参数与预算"]) + "\n")
w("**公共参数:** 全部配置 20 s perf 采样、10% 均匀抽取、`prompt_hints` 关闭(提示词里不加“该找哪类代码”的提示)、规则 α = 0.01 / 2% 门槛 / 10×9 测量;最终补丁独立复测 3 次。同一个种子编号在所有配置里使用同一条随机数流。\n")
w("### 5.2 逐种子结果\n")
w("**成本与过程**(每个运行一行;“请求数”在 I1 是模型调用数,其余是实际发出的 HTTP 请求数;total = prompt + completion,**reasoning 是 completion 的子集,没有重复相加**;“无 usage”请求的消耗未知,**不是 0**,也不在 total 里;续跑段的 token 和时间已计入所属运行):\n")
rows = []
for r in R:
    rows.append([r["run"], r["nodes"], r["http_requests"] or (r["api_calls_summary"] + "*"), r["ended_because"], r["prompt_tokens"], r["completion_tokens"], r["reasoning_tokens_subset_of_completion"] if r["reasoning_tokens_subset_of_completion"] != "0" else "0", r["total_tokens"],
                 r["no_usage_requests"] or "未记录", r["truncated_replies"] or ("未记录" if r["no_usage_requests"] == "" else "0"), f(r["search_elapsed_s"], 0), f(r["remeasure_elapsed_s"], 0)])
w(md(rows, ["运行", "节点(按运行顺序)", "请求数", "结束原因", "prompt", "completion", "其中 reasoning", "total", "无 usage 请求", "截断回复", "搜索耗时 s", "复测耗时 s"]) + "\n")
w("*I1 的“请求数”是模型调用数;I1 没有逐请求的 usage/截断记录,对应格显示“未记录”。搜索耗时是搜索的 wall-clock(续跑为各段之和,不含排队);复测耗时是搜索结束到第 3 次复测结束(I2/I1 由文件时间推得,I3 为作业起止时间;含重新构建)。\n")
w("\n**失败类型与结果**(失败类型计数来自 `results.jsonl` 每行的 `stage`;一个请求最多对应一行,重试和“无请求”的行见 `tables/runs_all.csv`):\n")
corr = {r["run"]: r for r in tab("correctness_per_run_final_patch.csv")}
rows = []
for r in R:
    c = corr[r["run"]]
    rows.append([r["run"], r["compile_fail"], r["check_fail"], r["unchanged"], r["http_fail"], r["measured_candidates"], r["confirmed_candidates"], f(r["search_best_confirmed_speedup"], 4), f(r["remeasure_speedup_median3"], 4), r["remeasure_passes"],
                 r["lineage_depth"], r["cumulative_updates"], r["final_patch_files"].replace("src/", "").replace(".cpp", "").replace(";", "; "), c["level"]])
w(md(rows, ["运行", "编译失败", "检查失败", "与原文相同", "HTTP 失败", "测到的候选", "确认的候选", "搜索中最佳确认", "独立复测 speedup", "复测通过", "谱系深度", "累计接受步数", "最终补丁改动的文件", "扩展正确性(最终补丁)"]) + "\n")
w("“搜索中最佳确认”对所有运行用同一个定义:`results.jsonl` 中满足“两次测量都通过规则”的候选里最好的 speedup(取两次中较差的 ratio)。I2 的排序规则本身不产生这个值,所以这一列对 I2 是诊断值。**“独立复测 speedup”才是对外报告的值**(固定最终补丁,3 次测量的中位数)。“累计接受步数”:种群搜索 = 最终补丁谱系中 `improved_on_parent` 的步数;greedy = 记录更新次数;best-of-N = 1(单个函数的一次改写)。“扩展正确性”见 §7:`not tested` 表示该最终补丁没有做过扩展测试(I1 的 10 个补丁;DeepSeek greedy 种子 3 的 40 请求最终补丁,只测过它 38 请求时的状态)。\n")
w("### 5.3 配置汇总(五个种子的中位数和完整范围)\n")
def mr(c, key, nd=3, sc=1.0):
    return f"{float(CS[c][key+'_median'])*sc:.{nd}f} [{float(CS[c][key+'_min'])*sc:.{nd}f}, {float(CS[c][key+'_max'])*sc:.{nd}f}]"
rows = []
for cid, *_ in CONFIGS:
    rows.append([CFGNAME[cid], mr(cid, "remeasured_speedup"), mr(cid, "search_best_confirmed_speedup"), f"{float(CS[cid]['total_tokens_median']):,.0f} [{float(CS[cid]['total_tokens_min']):,.0f}, {float(CS[cid]['total_tokens_max']):,.0f}]",
                 f"{float(CS[cid]['search_elapsed_s_median'])/60:.0f} min [{float(CS[cid]['search_elapsed_s_min'])/60:.0f}, {float(CS[cid]['search_elapsed_s_max'])/60:.0f}]", f"{float(CS[cid]['remeasure_elapsed_s_median'])/60:.1f} min",
                 f"{float(CS[cid]['course_metric_search_median']):.3e}", f"{float(CS[cid]['course_metric_remeasured_median']):.3e}"])
w(md(rows, ["配置", "独立复测 speedup", "搜索中最佳确认", "total tokens", "搜索耗时", "复测耗时(中位)", "课程指标 A:(搜索值−1)/tokens", "指标 B:(独立复测值−1)/tokens"]) + "\n")
w("**课程指标(README):`(best_confirmed_speedup − 1) / total_tokens`,读取 `credits.csv` 最后一行。** A 列对 I1、I3 就是这个定义(`credits.csv` 最后一行的 `best_confirmed_speedup`);I2 的 `credits.csv` 没有该列,A 用搜索中的排序最优值代替。B 列把分子换成固定最终补丁的独立复测值,更稳,但**不是**课程规定的定义。分母 total tokens 包含截断回复和失败请求,不包含“无 usage”请求(消耗未知)。\n")
w("**成本差距很大:** DeepSeek 每个运行的 total 约 27 万–62 万 token,其中 reasoning 占 completion 的绝大部分(各运行 96%–99%,中位数 97%);Qwen 约 2.4 万–4 万 token,没有 reasoning。所以 **Qwen 的课程指标比 DeepSeek 高一个数量级**(约 2×10⁻⁶ 对 2–4.5×10⁻⁷),尽管 DeepSeek 的绝对 speedup 更高。这是模型的成本结构差异,不能归因于搜索算法。\n")
w("### 5.4 同一模型内的比较:搜索 vs 独立采样\n")
w("四组比较,单位是**种子**(每个种子是一次独立搜索;同一补丁的三次复测不是三个种子)。检验:两侧各 5 个种子,**不配对**(同编号种子只是同一随机数流,结果并不成对);统计量 = 中位数之差,精确置换检验(C(10,5) = 252 种分组,双侧)和精确 Mann–Whitney 检验(双侧);**没有任何一个检验是预先登记的**,全部是探索性的;4 个主检验(独立复测 speedup)没有因多重比较调整,同时给出 Holm 校正后的 Mann–Whitney p。5 对 5 完全分离时精确 Mann–Whitney 的最小双侧 p = 2/252 = 0.0079。\n")
tests = tab("within_model_tests.csv")
TN = {"remeasured final speedup (primary)": "独立复测 speedup(主要)", "total tokens": "total tokens", "course metric (speedup-1)/tokens, remeasured speedup": "课程指标 B"}
CN = {"Qwen, I1 (original population search vs best-of-N)": "Qwen,I1(种群搜索 对 best-of-N)", "Qwen, I3 (README loop vs matched best-of-N)": "Qwen,I3(README 循环 对 匹配 best-of-N)",
      "DeepSeek, I2 (greedy chain vs best-of-N, rank rule)": "DeepSeek,I2(greedy 单链 对 best-of-N,排序规则)", "DeepSeek, I3 (README loop vs matched best-of-N)": "DeepSeek,I3(README 循环 对 匹配 best-of-N)"}
rows = []
for t in tests:
    t = dict(t); t["comparison"] = CN.get(t["comparison"], t["comparison"]); t["quantity"] = TN.get(t["quantity"], t["quantity"]) if t["quantity"] in TN else t["quantity"]
    if t["quantity"] in ("独立复测 speedup(主要)", "total tokens", "课程指标 B"):
        rows.append([t["comparison"], t["quantity"], f"{float(t['median_A']):.5g}", f"{float(t['median_B']):.5g}", t["range_A"], t["range_B"], f"{float(t['exact_permutation_p_two_sided_median_diff']):.4f}", f"{float(t['exact_mannwhitney_p_two_sided']):.4f}", t.get("holm_adjusted_mannwhitney_p_over_4_primary_tests", "") and f"{float(t['holm_adjusted_mannwhitney_p_over_4_primary_tests']):.3f}"])
w(md(rows, ["比较(A 对 B,A = 搜索)", "量", "A 中位数", "B 中位数", "A 范围", "B 范围", "置换 p", "Mann–Whitney p", "Holm 校正 MW p"]) + "\n")
w("**怎么解读(不选最小的 p 值,也不把“没发现显著差异”写成“相同”):**\n")
w("- **DeepSeek(两个版本都是):搜索明显高于 best-of-N。** I3:1.1648 [1.1375, 1.1811] 对 1.0732 [1.0685, 1.0737];I2:greedy 1.1758 [1.1574, 1.2155] 对 best-of-N 1.0725 [1.0667, 1.0740]。两种比较都是 5 个种子完全分离(搜索的每个种子都高于 best-of-N 的每个种子),精确 Mann–Whitney p = 0.0079,Holm 校正后 0.032;置换检验因为并列值只能到 0.0476。\n- **Qwen:两个版本都没有可靠差异。** I1:1.0573 对 1.0613(p = 0.69);I3:1.0745 对 1.0560(p = 0.31)。中位数的方向在两个版本里相反(I1 best-of-N 略高,I3 种群搜索略高),范围大幅重叠。**这不等于“种群搜索与 best-of-N 相同”**——5 个种子只够排除很大的差异。\n- **DeepSeek 更高的原因没有被单独证明。** 种群/greedy 比 best-of-N 多了继承、性能反馈、(种群的)失败反馈和函数收益权重,这些因素是一起变化的;本实验没有做逐项消融,所以不能说哪一个起了作用。§6.3 的叠加实验说明继承(把多个函数的赢家叠起来)可以解释很大一部分差距,但不是全部证据。\n- **跨模型的比较不能归因于算法:** 例如 DeepSeek 种群搜索 1.165 高于 Qwen 种群搜索 1.074,但两个模型的 token 量相差 10 倍以上、推理能力也不同。\n- **同一模型不同代码版本的比较(I2 greedy 1.1758 与 I3 种群搜索 1.1648)只作描述:** 两者范围大幅重叠,而且两版在规则(排序 vs 确认)、反馈、预算、是否收益分支上都不同,没有做检验。\n")
w("**成本差异:** 同一模型内,种群/greedy 比 best-of-N 多用 token:DeepSeek I3 366,952 对 320,397(置换 p = 0.24);I2 greedy 582,219 对 325,534(p = 0.048);Qwen I3 34,230 对 25,361(p = 0.048)。请求数相同(40),搜索耗时也更长(DeepSeek I3 约 191 分钟对 137 分钟,中位数)。课程指标 B 在 DeepSeek 上仍是搜索更高(I3:4.5×10⁻⁷ 对 2.3×10⁻⁷),在 Qwen 上两者相近(I3:2.17×10⁻⁶ 对 2.08×10⁻⁶,I1:1.98×10⁻⁶ 对 2.32×10⁻⁶)。\n")
w("**需要同时说的限制:** 5 个种子;节点类别与种子没有平衡(I1/I2 的 xcnc 与 xcnd 混用);DeepSeek I2 的运行有 8 个作业同时访问同一个模型端点,约 9 个 greedy 请求遇到 HTTP 502;DeepSeek I3 有 48 个无 usage 请求(HTTP 502),其 token 消耗未知,总量因此偏低。\n")
(PM / "intermediate" / "evidence_zh.part_c1.md").write_text("\n".join(L))
print("c1 ok")

# ---------------------------------------------------------------- 6
L = []; w = L.append
w("## 6. 速度提升主要来自哪些修改和机制?\n")
w("### 6.1 哪些函数反复成为赢家,各自做了什么(重新阅读了实际补丁)\n")
w("下表统计**最终补丁**里包含哪些函数的改动(种群搜索:谱系上的全部祖先,因为子补丁继承;greedy:全部被接受的步骤;best-of-N:单个函数)。每个配置 5 个最终补丁:\n")
fq = tab("functions_in_final_patches.csv"); by = collections.defaultdict(list)
for r in fq: by[r["config"]].append((r["function"], int(r["final_patches_containing_it_of_5"])))
rows = []
for cid, *_ in CONFIGS:
    top = [f"{fn} ({n}/5)" for fn, n in by[cid][:6]]
    rows.append([CFGNAME[cid], "; ".join(top)])
w(md(rows, ["配置", "最终补丁中最常出现的函数(出现次数/5)"]) + "\n")
w("**所有 DeepSeek 的 best-of-N 最终补丁(两个版本共 10 个)都只改 `Profile::GetMesg`**(speedup 1.067–1.074);Qwen 的 best-of-N 最终补丁 10 个里 9 个也是 `Profile::GetMesg`,另一个(I1 种子 2)是 `FieldBase::FieldBase`。`GetMesg` 是 profile 里最热的函数(约 19% 的样本),把线性扫描换成查表就是最容易找到的单点赢家。种群搜索和 greedy 的赢家集合更大:`Profile::GetMesg`、`FieldBase::FieldBase`(拷贝构造)、`Profile::GetFieldIndex`、`FieldBase::GetValue`、`Mesg::GetField`/`AddField` 等。\n")
w("**常见优化各自减少了什么工作**(以 greedy 种子 3 链的实际补丁为例,逐个读了 diff;“消息”表示只读了补丁头部的说明):\n")
w(md([
 ["`Profile::GetMesg`", "读 diff(0005、0011)", "**查找**:线性扫描 124 项 → 65536 项表(或排序表)一次读取", "最大的单步,约 6%(搜索时)"],
 ["`Profile::GetFieldIndex`", "读 diff(0003)", "**查找**:字段号线性扫描 → 位图+下标表缓存(缓存最近一个消息类型)", "搜索时约 1.5%;引入并发错误(见 §7)"],
 ["`FieldBase::FieldBase`(拷贝构造)", "读 diff(0004)", "**分配与复制**:原来先默认构造两个 `vector` 再赋值;现在在成员初始化列表里直接拷贝构造,省掉一次构造+一次赋值(字段在构造消息时被大量拷贝)", "搜索时约 4.4%(1 行改动)"],
 ["`FieldBase::GetValue`", "读 diff(0010)", "**逐字节拼装 → 一次 `memcpy`**(按 1/2/4/8 字节分支);假设小端机器", "搜索时约 0.7%"],
 ["`Mesg::AddField`", "读 diff(0008)", "**函数调用**:内联扫描已有字段,省掉对 `GetField` 的调用与返回指针", "搜索时约 1.4%"],
 ["`CRC::Get16`", "读 diff(0007)", "**查表次数减半**:16 项半字节表 → 256 项按字节的 constexpr 表", "搜索时约 0.25%"],
 ["`Decode::Resume`", "读 diff(0002)", "**成员读写 → 局部变量**(可放寄存器),在跳出循环时才写回", "搜索时约 0.4%"],
 ["`Field::GetType`、`GetNumSubFields`、`MesgDefinition::GetFieldByIndex`、`MesgBroadcaster::RemoveListener`", "消息(0001、0006、0009、0012)", "改写形式或加分支提示,**几乎没有减少工作**;补丁说明自己也承认在噪声内(0.03%–0.16%)", "与 §3.4 的空搜索噪声同量级"]],
 ["函数", "核对方式", "减少了什么工作", "搜索时单步收益"]) + "\n")
w("所以收益的主要来源是**三类**:消灭线性查找(`GetMesg`、`GetFieldIndex`)、减少构造/拷贝(`FieldBase` 拷贝构造)、把逐字节循环换成宽访问(`GetValue`)。其余多为噪声级的小步。\n")
w("### 6.2 一条有代表性的累计链(DeepSeek greedy,种子 3,中位数种子)\n")
ch = tab("chain_steps_ds_greedy_s3.csv")
rows = []
for c in ch:
    corr_txt = ""
    if c["step"] == "12":
        corr_txt = "TSan 4 处;4 线程运行未完成(= 旧最终状态 final-greedy-seed3)"
    elif c.get("corr_tsan_locations"):
        mm_ = c["corr_tsan_digest_mismatches"]
        corr_txt = f"TSan {c['corr_tsan_locations']} 处;" + (f"4 线程下 {mm_} 次与单线程不一致" if mm_.isdigit() and int(mm_) > 0 else ("4 线程运行未完成" if mm_ in ("-", "None") else "无并发不一致"))
    rows.append([c["step"], c["generation"], c["function"], f"{float(c['cumulative_speedup_at_search_time']):.4f}", f"{float(c['step_gain_pct']):.2f}%", "是(仅最终补丁)" if c["step"] == "13" else "否", corr_txt])
w(md(rows, ["步骤", "请求/代", "函数", "搜索时累计 speedup(记录)", "单步收益(相对上一个记录)", "是否独立复测", "该步骤的扩展正确性(步骤 1–11 和第 12 步(旧最终状态)测过;第 13 步未测)"]) + "\n")
w("**读这张表的规则:** (1) “搜索时累计 speedup”是**整个累计补丁**相对原库的 speedup(1/R),单步收益是记录的相对变化,**不能把各步百分比直接相加**,更不能把后面每一轮“继承了前面的收益”都算成一次新发现;(2) 只有最后一个数(1.1758,40 请求最终补丁的 3 次独立复测)是独立确认的;中间各步只有搜索时的两次测量;(3) 13 步里有 5 步(1、6、9、11、12)小于 0.2%,其中 2 步(6、12)不大于空搜索观察到的最大噪声单步 0.063%——它们在最终补丁里,但很可能没有贡献;(4) 步骤 3 引入 `GetFieldIndex` 缓存的那一步是**最早出现并发错误输出的补丁**(§7)。链上总共 40 个请求里只有 13 个被接受。\n")
w("### 6.3 best-of-N 候选的组合\n")
w("**做法(没有新的模型调用):** 取一个 DeepSeek best-of-N(I2)运行已经产生的全部候选;**每个函数**留搜索时 ratio 最低且 < 1 的那个候选;按搜索时 ratio 从好到坏排序;依次把前 K 个叠在一起(一个与已叠补丁冲突、不能干净应用的候选会被跳过并记录——5 个种子里只有种子 5 跳过 1 个);每个叠加状态用冻结的测量程序独立测 3 次(同时跑课程自带检查)。这 5 个种子共构造并测了 56 个叠加状态、168 次独立测量,**新增的模型调用为 0**。\n")
sb = tab("stacking_by_seed.csv"); ss = jt("stacking_summary.json")
rows = [[r["seed"], r["candidates_available"], f(r["best_of_N_final_remeasured"], 4), f(r["stack_K2_fixed"], 4), f(r["stack_K3_fixed"], 4), f(r["stack_K5_fixed"], 4), f"{r['bestK_posthoc']}", f(r["bestK_speedup_posthoc"], 4), f(r["last_K_speedup"], 4), f(r["greedy_final_remeasured_40req"], 4)] for r in sb]
rows.append(["中位数", "", f(ss["median_best_of_N"], 4), f(ss["median_K2"], 4), f(ss["median_K3"], 4), f(ss["median_K5"], 4), "", f(ss["median_bestK_posthoc"], 4), f(ss["median_lastK"], 4), f(ss["median_greedy"], 4)])
w(md(rows, ["种子", "可用候选函数数", "best-of-N 最终(单函数)", "固定 K=2", "固定 K=3", "固定 K=5", "**事后**最佳 K", "最佳 K 的 speedup(事后选择)", "叠到最后一个候选", "该种子 greedy(40 请求)"]) + "\n")
w(f"**汇总:** K=2 的中位数 1.127,K=3 为 1.143,K=5 为 1.158(范围 [1.142, 1.192]);事后最佳 K 为 1.187(范围 [1.158, 1.210])。“填补了 greedy − best-of-N 差距的多大比例”(逐种子计算后取中位数):K=2 {100*ss['gap_closed_median_stack_K2_fixed']:.0f}%、K=3 {100*ss['gap_closed_median_stack_K3_fixed']:.0f}%、K=5 {100*ss['gap_closed_median_stack_K5_fixed']:.0f}%、事后最佳 K {100*ss['gap_closed_median_bestK_speedup_posthoc']:.0f}%。\n")
w("**这个结果支持什么:** 把独立搜到的多个单函数赢家叠起来(没有失败反馈、没有种群、没有继承搜索),就能还原 greedy 与 best-of-N 之间**相当大一部分**差距(固定 K=5 约八成)。所以“greedy 更好”的很大一部分可以用**“保留并叠加多个函数的赢家”**解释。\n")
w("**它不支持什么:** (1) 不证明差距的**全部**来自叠加:固定 K 的叠加仍低于 greedy 的中位数 1.176;事后最佳 K 看起来逼近甚至超过,但那是事后选择的最大值,有乐观偏差;(2) 不能分别证明**反馈、选择、继承**各自的贡献——没有逐项消融;(3) 叠加用的候选按搜索时 ratio 排序,而搜索时的 ratio 含噪声(§3.4),排序本身带选择偏差;(4) 叠加的候选与 greedy 链里的赢家来自同一批函数,二者并不独立;(5) 叠加补丁同样含有未同步的静态状态,见 §7:20 个叠加补丁的扩展正确性在 §7 总表中。\n")
(PM / "intermediate" / "evidence_zh.part_c2.md").write_text("\n".join(L))
print("c2 ok")
