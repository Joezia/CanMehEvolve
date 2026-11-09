#!/usr/bin/env python3
"""evidence_zh.md, part D: correctness (section 7), conclusions, limits, missing evidence."""
import sys, collections; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from docs_lib import *
L = []; w = L.append
cu = tab("correctness_unified.csv"); cc = tab("correctness_by_config.csv"); meta = jt("stock_classification_meta.json")
w("## 7. 这些修改仍然正确吗?\n")
w("### 7.1 原来每轮检查已经做了什么,以及它与扩展测试的区别\n")
w("**每一个进入测速的候选**都经过课程提供的 `CanMehBench` 检查(README 规定,在计时之前做):(1) 库能载入且六个入口符号都在;(2) **解码校验值**:4 个固定活动文件(907,007 字节、34,251 条消息、428,714 个字段)折出的 64 位校验值必须与原库相同,每个文件解码两次;(3) **profile 查询摘要**:三个 profile 查询函数对**每个消息号 0–65535、每个字段号 0–255**的回答折成摘要,必须与原库相同——所以查表类补丁的**查表本身**在整个定义域上被穷尽核对;(4) **threading**:一次解码的处理器时间若超过墙钟时间的 1.15 倍就拒绝(候选自己开线程会被发现)。这些检查都是**单线程**、**只用这 4 个文件**、**只比较输出摘要**。\n")
w("**扩展正确性测试是附加的,不是搜索当时的准入规则,也不意味着搜索没有按课程要求做检查。** 它们补上课程检查没覆盖的几类问题:")
w(md([
 ["与原库的逐文件差分", "同一个文件分别用原库和候选库解码,比较(返回状态、消息数、字段数、摘要)", "更多输入(其他合法文件、边界值)上输出是否仍相同"],
 ["ASan + UBSan(单线程)", "用 `-fsanitize=address,undefined -O1` 重编译被补丁改过的翻译单元,在文件子集上运行", "越界读写、未定义行为"],
 ["TSan(4 线程)", "4 个线程**同时**解码同一批文件(冷启动:并发阶段在任何单线程解码之前),再逐线程与单线程参考摘要比较", "并发调用下的数据竞争和错误输出"],
 ["逐文件处理方式(plain,一个进程一个文件)", "每个文件单独起一个进程,记录:解码成功 / 抛异常(及文本) / 被信号杀死", "候选在恶意输入上是否出现崩溃(原库抛异常的地方候选是否崩溃)"]],
 ["测试", "做法", "补上的盲区"]) + "\n")
w("### 7.2 测试语料和真实测试规模\n")
w(md([
 ["语料 A(较早的对象:DeepSeek greedy/best-of-N 最终补丁、两个人工补丁、greedy 种子 3 的中间步骤)", "4 个标准文件 + 400 个**变异文件**(随机改字节、改定义区字节、截断;**重算了 CRC-16**,所以通过 CRC 检查,但内容不是合法 FIT 文件)= 404 个", "差分 404 个文件(原库对其中 177 个不能解码,所以 227 个可比);ASan/UBSan 71 个文件;TSan 4 线程 × 12 个文件;不含 SDK 编码器写出的合法文件"],
 ["语料 B(当前对象:I3 的 20 个最终补丁、20 个叠加补丁)", "语料 A + 55 个由 **SDK 自带编码器**写出的合法文件(原库对这 55 个全部成功解码)= 459 个", "差分 459 个文件(282 个可比,含 4 个原始文件和 55 个合法文件);ASan/UBSan 126 个文件(4 原始 + 55 合法 + 每 6 个变异取 1 个);TSan 4 线程 × 24 个文件;逐文件处理方式 459 个"]],
 ["", "组成", "各测试的真实规模"]) + "\n")
w("**CRC 正确不代表文件格式合法。** 变异文件的 CRC 是重新算的,头部和 CRC 都合法,但字段定义、基础类型、消息定义顺序被随机改动,违反 FIT 规范。它们只能说明“行为是否与原库相同”,而**不是**“正确输出是什么”。判断**解码合法文件时输出是否正确**,靠的是合法文件的差分(原库是行为参考,FIT 规范与 API 约定用来判断行为本身是否合理:合法文件必须解码出与原库相同的消息/字段值)。\n")
w("### 7.3 原库自己对 177 个文件的处理:最终分类\n")
w(f"语料 A 的 404 个文件里,原库解码成功 227 个,**{meta['stock_files_not_decoded_of_404']} 个没有成功**。它们不是“SDK 崩溃”这一类,而是下面的分类(一个文件一个进程,原库 `-O1`):\n")
sc = tab("stock_classification_404.csv")
w(md([[r["outcome"], r["files"]] for r in sc], ["原库的结局", "文件数"]) + "\n")
w(f"- **{meta['uncaught_exceptions']} 个是 SDK 的**设计内**拒绝**:解码器遇到格式错误的流时抛出 C++ 异常(截断、缺失消息定义、不支持的字节序、非法字段长度、开发者字段错误),这是 API 约定的报错方式(在驱动里被捕获并记录,不当作崩溃);**没有**返回 `Decode::Read == false` 的文件。\n- **{meta['killed_by_signal']} 个(文件 97,`defs` 类变异)被信号 11(段错误)杀死**:原库自己对畸形输入的内存错误,属于原库缺陷,不是候选引入。\n- 此外原库对 **{meta['stock_files_with_asan_error']} 个**文件触发 ASan 报告、对 **{meta['stock_files_with_ubsan_msg']} 个**文件触发 UBSan 报告(都出现在畸形输入上。对 55 个合法文件,原库没有 ASan 报告,但有 19 个文件触发 UBSan 消息——就是上面提到的 `fit_field_base.cpp` 对负数左移;4 个原始文件无报告)。\n")
w("因此差分表里“两个库都崩溃/抛异常:177”这一列**不是候选的缺陷**,只表示这些文件原库本身就不成功,无法比较。\n")
w("### 7.4 统一总表(每个已测对象一行)\n")
w("列说明:“原始 4 / 合法 55 / 变异”给出 可比文件数/其中输出完全相同(合法文件仅语料 B 有);“只有候选崩溃”指原库抛异常或正常、候选崩溃的变异文件数;“ASan”是 ASan 错误数,“UBSan 新”是原库没有的 UBSan 消息数;“TSan 位置”是 4 线程运行报告的不同数据竞争位置数;“并发不一致”是 4 线程里与单线程参考摘要不同的次数/比较次数;“—”表示不适用或该运行没有完成。**没有测试的对象不归入通过。**\n")
def cell(r, a, b):
    if r.get(a) in (None, ""): return "—"
    return f"{r.get(a)}/{r.get(b)}"
rows = []
for r in cu:
    if r["tested"] != "yes":
        rows.append([r["object"], "未测试" if r["tested"] == "NOT TESTED" else r["tested"], "", "", "", "", "", "", "", "", ""]); continue
    mm = r.get("tsan_digest_mismatches", "")
    comps = (int(r["tsan_subset_files"]) * 4) if str(r.get("tsan_subset_files", "")).isdigit() else ""
    rows.append([r["object"], r["corpus"].split(" ")[0], cell(r, "original4_compared", "original4_identical") if False else f"{r['original4_identical']}/{r['original4_compared']}",
                 (f"{r['legal_encoder_files_identical']}/{r['legal_encoder_files_compared']}" if str(r.get("legal_encoder_files_compared", "")).isdigit() else "—"), f"{r['mutants_identical']}/{r['mutants_compared']}",
                 r.get("crash_patch_only", ""), r.get("asan_errors", "") if r.get("asan_run_completed") != "False" else f"{r.get('asan_errors','')} (运行中止)", r.get("ubsan_messages_not_in_stock", ""), r.get("tsan_race_locations", ""),
                 (f"{mm}/{comps}" if str(mm).isdigit() else "运行未完成"), r["findings"].replace("none in the tested conditions", "无发现")])
rows.insert(0, ["stock(原库)", "A/B", "—", "—", "—", "—", "0", "0(原库自带 1 条 UBSan)", "0", "—", "基线"])
w(md(rows, ["对象", "语料", "原始 4(相同/可比)", "合法 55(相同/可比)", "变异(相同/可比)", "只有候选崩溃", "ASan", "UBSan 新", "TSan 位置", "并发不一致", "发现"]) + "\n")
w("(完整列在 `tables/correctness_unified.csv`;图 `fig7_correctness_matrix` 是同一内容的矩阵。)\n")
w("### 7.5 对各项问题的核实\n")
w("**① “无新增问题”与“完全没有告警”不是一回事。** 对 ASan/UBSan,表中数字是“**原库没有的**”消息数;原库自己有 1 条 UBSan 消息(`fit_field_base.cpp`:对负数左移),在 **46 个已完成的候选运行里同样出现**,在 13 个运行里消失(这些补丁重写了那段代码),另有 4 个运行因出错中止而无法判断。对 TSan,原库 4 线程运行**零**报告,所以任何报告都是新的。\n")
w("**② 只有竞争告警 vs 实际出现输出错误或崩溃。**\n")
w(md([
 ["仅 TSan 竞争告警,没观察到错误输出", "DeepSeek I3 的 best-of-N 5 个、种群 3 个(s3、s4、s5);I2 的 best-of-N 4 个(种子 1、3、4、5)、greedy 种子 2 和 5;Qwen I3 的 best-of-N 3 个(s2、s3、s5)、种群 s5;叠加 K=2/K=3/K=5 中的大多数。竞争的位置在 `fit_profile.cpp` 的 `GetMesg`(手写的 `static bool initialized` 惰性建表)"],
 ["4 线程下输出与单线程不一致(并发错误输出)", "greedy 种子 3 链的步骤 3、4、8、9、10(每个 36–39/48 次比较);叠加 s1-K3、s4-K3/K5/bestK、s5-K5/bestK(2–8 次);greedy 链里的不一致与 `GetFieldIndex` 共享缓存的出现吻合(见 ④);叠加补丁里不一致的具体原因没有逐个核对"],
 ["在合法文件上输出与原库不同", "**Qwen I3 种群搜索种子 3:55 个合法文件里只有 10 个相同(45 个不同)**;Qwen I3 种群种子 4:4 个不同;DeepSeek I3 种群种子 2:1 个不同。原始 4 个文件在所有补丁上都相同"],
 ["只在变异文件上不同", "greedy 种子 4(I2):4 个 `data` 变异文件的输出不同"],
 ["候选崩溃而原库不崩溃", "greedy 种子 1(I2)、DeepSeek I3 种群种子 1、叠加 s1-K5 与 s1-bestK9:在 11 个 `defs` 变异文件上只有候选崩溃(差分);语料 B 的逐文件运行里,这三个对象(DeepSeek I3 种群种子 1、叠加 s1-K5、s1-bestK9)各有 21 个文件被信号杀死(SIGFPE 12 个、SIGSEGV 9 个),均为 `defs` 变异文件,原库对其中多数抛异常、对个别(如文件 0048)正常解码;ASan 报告 1 个越界读"]],
 ["类别", "对象与证据"]) + "\n")
w("**③ 越界出现在哪类文件。** ASan/UBSan 的越界读报告(`fit_decode.cpp:819`,`baseTypeSizes[baseType]`,下标 31、数组只有 17 项)出现在 **`defs` 类变异文件**(定义区被改坏的文件)上,代码是**原库自己的 `Decode::ReadByte`**——它在校验 `baseType < FIT_BASE_TYPES` 之前就先读数组。原库在同一批 ASan 文件上没有这条报告;为什么原库没走到这里**没有查明**。另有文件(如 0048)原库正常解码、候选却收到 SIGFPE(整数除零),具体位置也没有定位。**4 个原始文件和 55 个合法文件**在这些补丁上的输出与原库完全相同(差分与逐文件运行都一致),没有出现越界。注意:这几个运行的 ASan 运行在第一个错误处中止,所以该运行里排在后面的文件没有被 ASan 检查(表中标“运行中止”)。\n")
w("**④ 最早引入缺陷的补丁及已确认的原因。** 逐步测过的只有 greedy 种子 3 链(语料 A):步骤 1–2(`RemoveListener`、`Decode::Resume`)在 TSan 下**零**告警、4 线程输出与单线程一致;**步骤 3(请求 12,`Profile::GetFieldIndex`)是最早出现问题的补丁**:TSan 位置 0 → 3,4 线程输出与单线程不一致 36/48 次;此后各步骤(能完成的)都保持 36–39/48 的不一致。**原因(代码阅读确认):**步骤 3 的补丁新增 `static const MESG *cachedMesg`、`static FIT_UINT16 cachedFieldIndex[256]`、`static FIT_UINT32 cachedFieldMask[8]`——函数每次被另一个消息类型调用时就改写这些共享变量,多线程交替查询不同消息类型时会读到别的消息类型的缓存,返回错误的字段下标。(没有把缓存改成加锁版本重新跑来反证,所以这是由“0→36 出现的位置恰是这个补丁”加代码机理得到的确认,不是干预实验。)对**其它**问题类别(合法文件差异、越界/崩溃),只测了最终补丁,没有逐步测试,**最早引入点和具体原因没有隔离,不能给出已确认的原因**。\n")
w("**⑤ 哪些结论针对哪组候选(“唯一干净”)。** 早先“人工补丁和 best-of-N 种子 2 是干净的”的说法**不准确**:更完整的对象集里,在各自测试条件下**没有任何发现**的是——人工补丁 1、2(语料 A);I2 best-of-N 种子 2(语料 A);greedy 种子 3 链的步骤 1、2(语料 A);Qwen I3 best-of-N 种子 1、4;Qwen I3 种群搜索种子 1、2;叠加 s2-K2(语料 B)。其中:\n- 语料 A 与 B 的测试规模不同(TSan 12 对 24 个文件、ASan 71 对 126 个文件、A 没有合法文件),二者的“无发现”不是同一强度。\n- **TSan 只会报告测试里实际发生的竞争。**对补丁加法的静态阅读(`tables/concurrency_patterns_by_patch.csv`)显示:Qwen I3 best-of-N 种子 1 的补丁含手写的 `static bool initialized` 惰性建表(与被 TSan 报告的补丁同一种写法),TSan 却没有报告——它是一次**漏报**,不能算安全。\n- 没有发现不等于正确:语料只有 459 个文件,TSan 只跑了 24 个文件。\n- 真正“由构造保证线程安全”的写法只有:函数内 `static const` 局部对象或 lambda 初始化的静态变量(C++11 保证一次性线程安全初始化)——两个人工补丁、I2 best-of-N 种子 2、Qwen I3 best-of-N 种子 4 和种群种子 1、2 就是这样写的;Qwen I3 种群种子 4 没有静态状态,但它在 4 个合法文件上输出不同。\n")
w("### 7.6 每个配置的最终补丁处于什么状态\n")
w(md([[CFGNAME[r["config"]], r["no finding in tested conditions"], r["TSan race only"], r["differs only on hostile mutants"], r["wrong output / crash / memory error"], r["not tested"], r.get("reading: unsafe", "0"), r.get("reading: safe/none", "0")] for r in cc],
     ["配置(每个 5 个最终补丁)", "无发现", "仅 TSan 竞争", "仅变异文件输出不同", "错误输出/崩溃/内存错误", "未测试", "代码阅读:含未同步共享状态", "代码阅读:无/线程安全"]) + "\n")
w("“错误输出/崩溃/内存错误”包括:合法文件输出不同、4 线程下输出不一致、候选独有崩溃、ASan 错误。I1(Qwen 原始实现)的 10 个最终补丁**没有做过任何扩展测试**;“代码阅读”列只是静态阅读,对 I1 的读数没有逐个人工核对。\n")
w("**性能数字与正确性状态并列。** 本文件所有 speedup 都是相应基准条件下的测量(4 个固定文件、单线程、`-O2`、同一节点对内的 ratio)。§5.2 逐种子表在每个最终补丁的 speedup 旁给出了扩展正确性状态,图 `fig1_seed_results_with_correctness` 把状态画在每个点上。\n")

w("## 8. 局限、缺失与未验证\n")
w("### 8.1 与旧汇总不一致的地方,以及本文件采用的定义\n")
w(md([
 ["greedy 链的记录更新次数", "早先的空搜索对比文字写 50 次", "本文件按 5 个 greedy 运行在 **40 个请求时**的 `rank_updates` 统计,共 51 次(种子 3 在续跑中又多了第 13 步,请求 39)。"],
 ["DeepSeek greedy 的中位数", "最初的 Phase 1 统计(3 个种子在 38/34/34 个请求处停止)是 1.1687", "本文件用 40 个请求的最终状态(种子 1、3、4、5 经续跑补足):1.1758。种子 3 的最终补丁因此多了一步。"],
 ["“确认”的 speedup", "Phase 1 把 `best_confirmed_speedup` 定义为 3 次独立复测的中位数;I3 的 `credits.csv` 最后一行是**搜索时**的确认值", "两者都给出:“独立复测”(主要,本文件所有比较用它)和“搜索中最佳确认”(例如 DeepSeek I3 种群 1.1648 对 1.1634)。课程指标 A 用后者、B 用前者。"],
 ["置换检验的 p", "早先写 0.0476", "5 对 5 完全分离时,中位数之差的置换 p 因并列值只能到 0.0476;精确 Mann–Whitney 为 0.0079(2/252)。本文件两个都给,不挑小的。"],
 ["“唯一干净”的补丁", "早先说人工补丁和 best-of-N 种子 2“干净”", "更完整的对象集和代码阅读后改为 §7.5 ⑤:没有发现的补丁不止这几个,且其中含 TSan 漏报;“没有发现”只针对各自的测试条件。"],
 ["正确性测试对象", "greedy 种子 3 的“final-greedy-seed3”", "测过的是 38 个请求时的状态(请求 37),不是 40 个请求的最终补丁(请求 39);表中标出未测。"]],
 ["项目", "旧汇总的说法", "本文件的做法"]) + "\n")

w("- **样本数:** 每个配置 5 个种子;大部分比较的 p 值是探索性的;5 个种子只能分辨大差异(DeepSeek 搜索 vs best-of-N),不能确认小差异(Qwen)。\n- **节点与批次:** 校准只在 xcnc2;C1/C2 只在 xcnd24 且各 5 次测量;I1/I2 的节点类别与种子不平衡;xcnc 与 xcnd 的基线耗时相差约 33%(358 对 480 ms),ratio 理论上抵消,但没有逐类验证加速比是否一致。\n- **端点并发:** I2 的 DeepSeek 运行有 8 个作业同时访问同一端点(违反“最多 4 个”的建议),I3 保持 4 个;约 58 个 DeepSeek 请求返回 HTTP 502 且无 usage,token 消耗未知(不是 0)。\n- **I1 的请求数:** 老 Qwen 运行记录的是“40 次模型调用”,提供的客户端可能在其中隐藏了重试,HTTP 请求数不可核实。\n- **人工对照:** 没有计时记录;AI 辅助。\n- **正确性覆盖:** 语料 459 个文件、TSan 24 个文件;I1 的 10 个补丁、greedy 种子 3 的 40 请求最终补丁、人工补丁在合法文件上的差分**未测试**;越界/崩溃和合法文件差异的**具体原因没有隔离**;没有把任何问题补丁修好后重测。\n- **组合实验:** 叠加的是 I2 best-of-N 的候选,没有用 I3 的候选重做;没有对反馈、选择、继承做逐项消融。\n- **同一种子编号共享随机数流:** 不同配置的函数抽取序列相关(见 §2.3);检验按“不配对的独立种子”处理,这一假设对 best-of-N 配置之间只是近似。\n- **C2 一小时计时:** 缺失,无法补成已完成。\n")
(PM / "intermediate" / "evidence_zh.part_d.md").write_text("\n".join(L))
print("d ok")
