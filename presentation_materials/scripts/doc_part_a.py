#!/usr/bin/env python3
"""evidence_zh.md, part A: reading guide, project and pipeline, methods, requirement checklist."""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from docs_lib import *
L = []
w = L.append
w("# 证据文件(中文):按研究问题组织\n")
w("> 本文件的数字全部由 `presentation_materials/scripts/` 中的脚本从服务器上的原始文件(`runs/`)重新计算,没有读取旧报告里的汇总。每个关键数字的来源见 `sources.csv`,完整表格在 `tables/`。图在 `figures/`。\n")
w("## 0. 先读这里:术语和实验条件\n")
w("**比值与加速比。** 一次测量给出 `ratio = 候选耗时 / 参考(原库)耗时`,小于 1 表示更快。具体算法:每个进程内部对候选和参考各测 9 次,取各自的中位数相除得到进程比值;10 个进程的进程比值再取中位数,就是这次测量的 `ratio`。`speedup = 1 / ratio`。\n")
w("**耗时下降百分比与速度提高百分比不是同一个数。** 下降 = (1 − ratio) × 100%;速度提高 = (speedup − 1) × 100%。例如:\n")
rows = []
for red in (2, 5, 10, 15, 20):
    ratio = 1 - red / 100; rows.append([f"{red}%", f"{ratio:.3f}", f"{1/ratio:.4f}", f"{(1/ratio-1)*100:.1f}%"])
w(md(rows, ["耗时下降", "ratio", "speedup", "速度提高"]) + "\n")
w("本文件对外统一用 speedup(如 1.176 表示 17.6% 更快)。2% 门槛是对 **ratio ≤ 0.98**(下降至少 2%,对应 speedup ≥ 1.0204)。\n")
w("**三个代码版本(实验条件,不是时间线)。** 不同条件下的运行始终分开报告,从不混合计算中位数:\n")
w(md([["I1", "种群搜索 + best-of-N,两次测量确认规则;课程提供的 HTTP 客户端(每次调用最多 3 次隐藏重试);预算 = 40 次模型调用", "`archive/qwen-experiment/Search.cpp`(sha256 ce80cd7b…)", "Qwen 种群搜索、Qwen best-of-N"],
       ["I2", "排序规则启发式:greedy 单链 / best-of-N;每次调用恰好 1 个 HTTP 请求;预算 = 40 个 HTTP 请求(作业到时限的运行用续跑补足)", "`src/Search.cpp` @ d5aa9e7(sha256 67935a2f…)", "DeepSeek greedy、DeepSeek best-of-N(排序规则)"],
       ["I3", "README 完整循环:种群 ≤ 6 + 二选一锦标赛 + 失败反馈 + 函数收益权重;或匹配的 best-of-N(确认规则);预算恰好 40 个 HTTP 请求;检查点续跑", "`src/Search.cpp` @ 527c5d0(sha256 9431cd44…)", "DeepSeek 与 Qwen 的种群搜索和匹配 best-of-N"]],
      ["版本", "做什么", "代码", "用于哪些配置"]) + "\n")
w("共 8 个配置 × 5 个种子 = 40 个搜索运行:\n")
w(md([[k, v] for k, v in CFGNAME.items()], ["配置编号", "名称"]) + "\n")
w("**重要:同一个模型的搜索与 best-of-N 才构成算法对照**;不同模型之间的差异不能单独归因于算法(模型、token 量、推理能力都不同)。\n")

# ---------------------------------------------------------------- 1
w("## 1. 我们到底做了什么\n")
w("### 1.1 研究问题,以及为什么一个加速数字不够\n")
w("项目问的是:让大语言模型改写 Garmin FIT SDK 解码器里的函数,**能不能得到真实、可复现、正确的加速,以及这些加速来自搜索算法还是来自别的因素**。只报告一个加速数字无法回答,因为:\n")
w("1. 那个数字可能只是噪声——需要知道测量规则的误报率(Phase 0 校准、合成 null、真实 SDK 的无效补丁、空搜索)。\n2. 最好的那个种子可能是运气——需要 5 个种子的中位数和范围。\n3. 没有对照就不知道谁的功劳——需要编译器选项(C1)、人工优化(C2)、同预算独立采样(C3)。\n4. 速度快不等于仍然正确——需要比课程自带检查更严格的扩展正确性检查。\n5. 成本不同——token、时间、请求数。\n")
w("### 1.2 被优化的程序和工作负载,以及可核查的信息表\n")
w("被优化的是 **Garmin FIT SDK 21.201.0 的 C++ 解码器**(约 5500 个可改写的函数/单元,称 region)。工作负载:用 SDK 解码 4 个活动文件,把每一个解码出的字段值折进一个 64 位校验值,由课程提供的 `CanMehBench` 对原库和候选库计时。下表是可核查信息(来源见每行):\n")
rows = [[r["item"], r["value"], r["source"]] for r in tab("data_and_environment.csv")]
w(md(rows, ["项目", "值", "来源"]) + "\n")
es = jt("environment_summary.json")
w(f"**节点差异。** 同一份原库,`xcnc` 节点上一次完整解码约 358–360 ms,`xcnd` 节点约 480 ms(40 个运行的基线范围 {es['baseline_ms_min']:.0f}–{es['baseline_ms_max']:.0f} ms)。所以**不同节点的绝对毫秒数不能直接比较**;本文件只比较同一进程对内测得的 ratio/speedup。I1 和 I2 的运行混合使用 xcnc 和 xcnd(与种子没有平衡),I3 的运行主要在 xcnc(逐运行节点见 `tables/run_baselines_and_parameters.csv`)。\n")
w("### 1.3 课程提供了什么,我们实现了什么\n")
w("课程提供 6 个程序:`CanMehHarness`(复制 SDK、拼接补丁、编译并检查候选库)、`CanMehBench`(在同一进程里对两个库交替计时、做校验)、`CanMehCalibrate`(校准对)、`CanMehDataGenerator`(生成 4 个文件)、`CanMehDecodeForSampler`(供 perf 采样)和需要自己写的 `CanMehSearch`。**我们实际编写的只有 `src/Search.cpp`**(主循环、系统提示词与用户提示词、回复解析、判定规则 `candidateIsFaster`/`analyzeTimings`、种群与函数选择、预算与续跑),以及运行和分析用的脚本(`scripts/`)。其余五个程序按课程原样使用。(I3 中还用我们自己的 HTTP 适配代替课程客户端,目的是让“请求数”可核查,见 §2.)\n")
w("### 1.4 每一轮从选函数到保留候选的完整流程\n")
w("""```
一次运行开始(每个种子一次):
  CanMehHarness init  → null_ok 检查(原库 vs 原库必须不被判快)    [所有 40 个运行 null_ok = true]
  perf 采样 20 秒      → 每个 region 的样本数                      [5514 个 region 里只有约 76 个有样本]

每一轮(一次模型请求):
  1. 选父补丁 与 选函数                                            (见 §2)
  2. CanMehHarness show:取该函数在"父补丁"下的当前文本
  3. 构造提示词:函数文件和名字、行数、原库一次解码耗时、父补丁与"目前最好"的 ratio(best-of-N 显示 1.000)、
                  [仅种群搜索] 上次失败的原因和被拒绝的代码、当前函数全文
  4. 请求模型(DeepSeek-v4.1-flash 或 Qwen3-coder-next,temperature 0.8)
  5. 从回复里取出 ```cpp 代码块;替换同名函数                       → 失败类型:无代码 / 被截断 / 与原文相同
  6. CanMehHarness splice:生成相对 SDK 原始源码的补丁
  7. CanMehHarness measure-patch --no-decision:
        编译并链接候选库                                            → 失败类型:compile / link
        课程自带检查:库能载入、4 个文件的解码校验值一致、profile 查询摘要一致、候选自己不开线程、处理器时间
                                                                    → 失败类型:correctness / profile / threading / crash / load
        10 个进程 × 每进程 9 次重复,每个进程里原库与候选交替计时    → 返回原始 timings
  8. 我们的规则读原始 timings 计算 ratio、符号翻转 p、不稳定标志
        第一次测量通过规则(或不稳定)才做第二次测量
  9. 保留/记录候选(种群搜索:所有测到的候选都进种群;greedy/best-of-N:按排序规则更新"记录")
 10. [仅种群搜索] 若是可修复的失败(compile/link/检查失败),下一轮用同一个函数、同一个父补丁带着失败原因重试一次
 11. 请求计入预算;达到 40 个 HTTP 请求结束

一次运行结束后(单独的作业):
  把"固定的最终补丁"独立地再测 3 次(三次 10×9 测量,规则同上)→ 这是对外报告的"独立复测加速比"
```
""")
w("**系统提示词**要求模型保持签名、对每个输入行为完全一致(校验值和 profile 全域扫描会拒绝任何行为差异)、不要使用线程,只改这一个函数。提示词**没有**提到线程安全或并发调用——这和 §7 的发现直接相关。\n")

# ---------------------------------------------------------------- 2
w("## 2. 三种搜索方法:实际实现和证据\n")
w("### 2.1 统一比较表(以当前实际代码为准;“仅部分模式存在”的机制已标出)\n")
w(md([
 ["每次从哪个版本开始改", "**父补丁**(从种群里选出的一个已测候选,含它继承的全部改动)", "**当前记录补丁**(累计所有已接受的改动)", "**原库**(每次都从零开始)"],
 ["父补丁如何选", "二选一锦标赛:随机取两个种群成员,ratio 较小者当父(种群为空时用原库)。`pickParent`", "永远是记录补丁(无选择)", "无父补丁"],
 ["如何选函数", "与另两种相同的“采样加权 90% / 均匀 10%”;**另有 25% 的“收益分支”(仅此模式)**", "采样加权 90% / 均匀 10%", "采样加权 90% / 均匀 10%"],
 ["是否继承已有修改", "是(子补丁在父补丁之上拼接)", "是(累计)", "否"],
 ["接收性能反馈", "是:提示词里有父补丁和“目前保留的最好”的 ratio", "是:同样的两个数字", "否:提示词里两个数字固定为 1.000"],
 ["接收失败反馈", "是:compile/link/检查失败后下一轮带失败原因和被拒绝的代码重试一次(I3、I1)", "否", "否"],
 ["保留候选的条件", "每个测到的候选都进种群(哪怕更慢);种群超过 6 个时淘汰 ratio 最大的", "记录规则:第一次测量稳定(不 unstable)且 ratio < 记录,第二次测量也稳定,R = max(两次 ratio) < 记录 → 成为新记录。**不要求 p<0.01,不要求 2% 门槛**(I2)", "同左,但永远不继承;只记录“最好的一次”(I2);I3 的匹配版本用确认规则"],
 ["什么条件称为“统计确认的加速”", "两次测量都满足:平均 log 比 < 0、精确符号翻转 p < 0.01、ratio ≤ 0.98(且不 unstable)", "搜索中只有诊断标记 `confirmed`(两次都通过规则);对外的确认值来自固定最终补丁的 3 次独立复测", "I3、I1:同种群搜索的两次确认;I2:同 greedy 的诊断标记"],
 ["适用的代码版本", "I1、I3", "I2", "I1、I2、I3"]],
 ["", "种群搜索", "greedy 单链", "best-of-N"]) + "\n")
w("**说明:** (1) 种群搜索中候选的 ratio 是**整个累计补丁**对原库的 ratio;一个已经被确认的父补丁的所有后代,即使自己的改动没有贡献,也会因继承而再次被确认。`improved_on_parent` 才是“这一步比父补丁更好”。(2) I2 的排序规则没有显著性检验,也没有 2% 门槛,所以 §3C 要专门检验“空搜索会不会靠噪声产生假进步”。\n")
w("### 2.2 函数性能采样如何变成选择概率\n")
w("`perf` 对解码循环采样 20 秒,把每个样本归到它所在的 region(函数)。设 region r 得到 s_r 个样本,总样本 S,region 总数 N = 5514。`pickRegion` 的逻辑:\n")
w("""```
pickRegion():                                     # src/Search.cpp:1352
    if 种群搜索 and U1 < 0.25 and 存在“收益 > 0”的 region:   # 收益 = 已接受候选相对其父补丁的 ratio 改善量
        return 收益最大的 region                             # “利用历史收益”的分支(I1、I3 的种群搜索才有)
    if S > 0 and U2 >= 0.10:                                 # 90%:按样本加权
        return 以概率 s_r / S 抽到 r
    return 在全部 5514 个 region 上均匀抽一个                # 10%:均匀
```
""")
w("没有收益记录或不是种群搜索时,一次抽取选中 region r 的概率就是 **P(r) = 0.9 · s_r / S + 0.1 / 5514**。有收益记录的种群搜索:P(r) = 0.25 · 1[r 是收益最大者] + 0.75 · (0.9 · s_r / S + 0.1 / 5514)。\n")
w("**实际作用。** 5514 个 region 里只有约 76 个有样本。所以 90% 的抽取集中在这 76 个热点函数,其中最热的 `Profile::GetMesg` 约占样本的 19%;而 10% 的均匀抽取里,约 98.6% 落在**没有样本**的函数上(多数是一行的 getter/setter,被编译器内联,不会出现在 profile 里,但改写它们仍可能有收益)。下表是一个运行(ds_pop_I3 种子 1)里前 10 个函数的样本占比和每次抽取的概率:\n")
ex = tab("region_probability_example_ds_pop_I3_s1.csv")
w(md([[r["rank"], r["label"], r["samples"], f"{float(r['share_of_attributed_samples_pct']):.1f}%", f"{float(r['p_weighted_draw_pct']):.2f}%", r["draws_observed_in_this_run"]] for r in ex],
     ["名次", "函数", "样本数", "占有样本的比例", "单次抽取概率(无收益分支)", "本运行实际抽到次数"]) + "\n")
w("**各 DeepSeek I3 运行汇总:预期与实际抽取份额(8 个最热函数,10 个运行、共 370 次独立抽取):**\n")
ev = tab("../figure_data/region_expected_vs_observed.csv") if False else list(csv.DictReader(open(PM / "figure_data/region_expected_vs_observed.csv")))
w(md([[r["function"], f"{float(r['mean_sample_share_pct']):.1f}%", f"{float(r['expected_pct']):.1f}%", f"{float(r['observed_pct']):.1f}%", f"{r['observed_draws']}/{r['total_draws']}"] for r in ev],
     ["函数", "平均样本占比", "按公式预期的抽取份额", "实际抽取份额", "实际次数"]) + "\n")
w("`FieldBase::FieldBase` 的实际份额(14.1%)高于按公式预期的 6.0%。分开看:DeepSeek 种群搜索(有 25% 收益分支)占 32/170 = 18.8%,三个没有收益分支的 DeepSeek/Qwen best-of-N 与 greedy 配置占 9.0%–10.8%。收益分支确实让种群搜索更常回到已经有收益的函数;没有收益分支的配置里仍略高于 6.5%,但**同一个种子编号在所有配置里使用同一条 mt19937 随机数流**,没有收益分支的 4 个配置的抽取序列因此高度相关(有效独立样本大约只有 5 个种子 × 40 次),这点超出预期不能当作 4 倍的独立证据。\n")
w("### 2.3 同一个函数能否被重复选择?为什么 40 次请求不等于 40 次成功优化\n")
w("**能。** 每次抽取都是有放回的独立抽取,没有“已选过就排除”的机制;种群搜索的失败重试还会**有意**在同一函数上再抽一次。下表是各配置(5 个种子汇总)的实际情况(只统计非重试的独立抽取):\n")
rs = tab("region_selection_by_config.csv")
w(md([[CFGNAME[r["config"]], r["draws_total"], f(r["distinct_regions_median"], 0), f(r["repeat_draws_median"], 0), f(r["max_times_one_region_median"], 0), pct(r["zero_sample_draw_share_observed"]), pct(r["top5_profile_region_share_observed"])] for r in rs],
     ["配置", "独立抽取总数", "每运行不同函数数(中位数)", "每运行重复抽取数(中位数)", "同一函数最多被抽到(中位数)", "落在无样本函数的比例", "落在前 5 热点的比例"]) + "\n")
w("(I1、I2 的运行只保存了前 40 个热点的样本,统计“无样本函数”时把第 41 名之后的有样本函数也算成了无样本,所以这两版的“无样本比例”略偏高。)\n")
w("**40 次请求去了哪里。** 下表是每个配置的 40 次请求的结局(各结局数量取 5 个种子的中位数,所以每行之和不严格等于 40)。“确认但不比父补丁好”的绝大部分是**继承**:一个父补丁已经确认,它的后代只要没破坏它就会再次通过规则。\n")
fn = tab("request_funnel.csv")
w(md([[r["label"], f(r["http_or_no_code_or_truncated"], 0), f(r["unchanged"], 0), f(r["compile_fail"], 0), f(r["check_fail"], 0), f(r["measured_not_confirmed"], 0), f(r["confirmed_inherited_or_not_better_than_parent"], 0), f(r["new_step_accepted"], 0)] for r in fn],
     ["配置", "无可用回复(HTTP 错误/无代码/截断)", "与原文相同", "编译或链接失败", "未通过课程检查", "测了但没被确认更快", "确认但不比父补丁好", "新步骤被接受 / best-of-N 独立确认"]) + "\n")
w("所以:**40 次请求 ≠ 40 次成功优化**。例如 DeepSeek 种群搜索(I3)每个运行中位数约 8 次请求遇到 HTTP 502(没有回复,也没有 usage),约 7 次编译失败;整个搜索里“比父补丁更好”(`improved_on_parent`)的候选中位数 12 个,其中进入最终补丁谱系的约 5 个,最终补丁的谱系深度中位数 8 层。\n")
w("### 2.4 源码位置\n")
w(md([
 ["函数选择 `pickRegion`", "`src/Search.cpp:1352`(I3);`archive/qwen-experiment/Search.cpp:1061`(I1);`git show d5aa9e7:src/Search.cpp` 第 1321 行(I2)"],
 ["父补丁 `pickParent`", "`src/Search.cpp:1345`;I1:`archive/.../Search.cpp:1055`;I2:`d5aa9e7` 第 1314 行(排序规则下返回记录补丁/原库)"],
 ["判定规则 `analyzeTimings` / `signFlipPValue`", "`src/Search.cpp:384` / `:364`"],
 ["排序规则(greedy/best-of-N, I2/I3 代码里的 rankMode)", "`src/Search.cpp:1600`(`possiblyBetter`、`R = max(ratio_1, ratio_2)`)"],
 ["确认规则、`improved_on_parent`、种群更新", "`src/Search.cpp:1662`(`needSecond`)、`:1668`(`confirmed`)、`:1671`(`improved`)、`:1712`/`:1715`(入种群/淘汰)"],
 ["失败重试", "`src/Search.cpp:1381`(`isRepairable`)和 `repair.active`"],
 ["提示词", "`src/Search.cpp:581`(`systemPrompt`)、`:601`(`userPrompt`)"],
 ["采样与权重", "`src/Search.cpp:1253`–`1290`(perf 采样、`weighRanges`)"],
 ["预算与续跑(仅 I3)", "`src/Search.cpp` 循环头 `if (calls >= budget)`;`state.json`、`--resume`"]], ["机制", "位置"]) + "\n")

# requirements
w("### 2.5 课程要求核对表(“实现了”与“正式实验实际使用了”分开)\n")
rq = tab("requirements_checklist.csv")
w(md([[r["requirement"], r["implemented_in_code"], r["used_in_the_formal_runs"], r["evidence"], r["status"]] for r in rq], ["要求", "代码里是否实现", "正式实验里是否实际使用", "证据", "状态"]) + "\n")
w("状态:满足 = 已实现且正式运行使用;部分 = 部分满足(括号内是缺口)。\n")
(PM / "intermediate" / "evidence_zh.part_a.md").write_text("\n".join(L))
print(len("\n".join(L)))
