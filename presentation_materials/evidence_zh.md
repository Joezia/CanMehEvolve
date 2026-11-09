# 证据文件(中文):按研究问题组织

> 本文件的数字全部由 `presentation_materials/scripts/` 中的脚本从服务器上的原始文件(`runs/`)重新计算,没有读取旧报告里的汇总。每个关键数字的来源见 `sources.csv`,完整表格在 `tables/`。图在 `figures/`。

## 0. 先读这里:术语和实验条件

**比值与加速比。** 一次测量给出 `ratio = 候选耗时 / 参考(原库)耗时`,小于 1 表示更快。具体算法:每个进程内部对候选和参考各测 9 次,取各自的中位数相除得到进程比值;10 个进程的进程比值再取中位数,就是这次测量的 `ratio`。`speedup = 1 / ratio`。

**耗时下降百分比与速度提高百分比不是同一个数。** 下降 = (1 − ratio) × 100%;速度提高 = (speedup − 1) × 100%。例如:

| 耗时下降 | ratio | speedup | 速度提高 |
|---|---|---|---|
| 2% | 0.980 | 1.0204 | 2.0% |
| 5% | 0.950 | 1.0526 | 5.3% |
| 10% | 0.900 | 1.1111 | 11.1% |
| 15% | 0.850 | 1.1765 | 17.6% |
| 20% | 0.800 | 1.2500 | 25.0% |

本文件对外统一用 speedup(如 1.176 表示 17.6% 更快)。2% 门槛是对 **ratio ≤ 0.98**(下降至少 2%,对应 speedup ≥ 1.0204)。

**三个代码版本(实验条件,不是时间线)。** 不同条件下的运行始终分开报告,从不混合计算中位数:

| 版本 | 做什么 | 代码 | 用于哪些配置 |
|---|---|---|---|
| I1 | 种群搜索 + best-of-N,两次测量确认规则;课程提供的 HTTP 客户端(每次调用最多 3 次隐藏重试);预算 = 40 次模型调用 | `archive/qwen-experiment/Search.cpp`(sha256 ce80cd7b…) | Qwen 种群搜索、Qwen best-of-N |
| I2 | 排序规则启发式:greedy 单链 / best-of-N;每次调用恰好 1 个 HTTP 请求;预算 = 40 个 HTTP 请求(作业到时限的运行用续跑补足) | `src/Search.cpp` @ d5aa9e7(sha256 67935a2f…) | DeepSeek greedy、DeepSeek best-of-N(排序规则) |
| I3 | README 完整循环:种群 ≤ 6 + 二选一锦标赛 + 失败反馈 + 函数收益权重;或匹配的 best-of-N(确认规则);预算恰好 40 个 HTTP 请求;检查点续跑 | `src/Search.cpp` @ 527c5d0(sha256 9431cd44…) | DeepSeek 与 Qwen 的种群搜索和匹配 best-of-N |

共 8 个配置 × 5 个种子 = 40 个搜索运行:

| 配置编号 | 名称 |
|---|---|
| qwen_pop_I1 | Qwen 种群搜索 (I1) |
| qwen_bon_I1 | Qwen best-of-N (I1) |
| qwen_pop_I3 | Qwen 种群搜索 (I3, README 循环) |
| qwen_bon_I3 | Qwen best-of-N (I3, 匹配对照) |
| ds_greedy_I2 | DeepSeek greedy 单链 (I2) |
| ds_bon_I2 | DeepSeek best-of-N (I2, 排序规则) |
| ds_pop_I3 | DeepSeek 种群搜索 (I3, README 循环) |
| ds_bon_I3 | DeepSeek best-of-N (I3, 匹配对照) |

**重要:同一个模型的搜索与 best-of-N 才构成算法对照**;不同模型之间的差异不能单独归因于算法(模型、token 量、推理能力都不同)。

## 1. 我们到底做了什么

### 1.1 研究问题,以及为什么一个加速数字不够

项目问的是:让大语言模型改写 Garmin FIT SDK 解码器里的函数,**能不能得到真实、可复现、正确的加速,以及这些加速来自搜索算法还是来自别的因素**。只报告一个加速数字无法回答,因为:

1. 那个数字可能只是噪声——需要知道测量规则的误报率(Phase 0 校准、合成 null、真实 SDK 的无效补丁、空搜索)。
2. 最好的那个种子可能是运气——需要 5 个种子的中位数和范围。
3. 没有对照就不知道谁的功劳——需要编译器选项(C1)、人工优化(C2)、同预算独立采样(C3)。
4. 速度快不等于仍然正确——需要比课程自带检查更严格的扩展正确性检查。
5. 成本不同——token、时间、请求数。

### 1.2 被优化的程序和工作负载,以及可核查的信息表

被优化的是 **Garmin FIT SDK 21.201.0 的 C++ 解码器**(约 5500 个可改写的函数/单元,称 region)。工作负载:用 SDK 解码 4 个活动文件,把每一个解码出的字段值折进一个 64 位校验值,由课程提供的 `CanMehBench` 对原库和候选库计时。下表是可核查信息(来源见每行):

| 项目 | 值 | 来源 |
|---|---|---|
| FIT SDK version | 21.201.0 | runs/phase1-final/VERSIONS.txt (fit_sdk=21.201.0) |
| workload | decode the 4 activity files with the SDK decoder; every decoded field value folded into a 64-bit checksum; timed with CanMehBench (reference vs candidate library in one process pair) | README.md Architecture; src/workloads/SdkDecode.cpp |
| data: total bytes | 907007 | runs/round2/runs/ds-population-s1/bench.err; runs/phase1-final/run_facts.json data.identifiers |
| data: messages decoded | 34251 | same |
| data: fields decoded | 428714 | same |
| data: checksum (CanMehBench fold) | 92bebfd7f8978fc8 | same |
| data file intervals.fit | 102887 bytes; 3626 messages; 46984 fields; sha256 449c8f032de7ffa4... | build/data/*.fit; counts from the stock decoder (scripts/followup/driver.cpp 'single' mode on the 4 originals); sums equal the CanMehBench totals |
| data file long_run.fit | 403783 bytes; 14410 messages; 187256 fields; sha256 3c9f63c71ac0d063... | build/data/*.fit; counts from the stock decoder (scripts/followup/driver.cpp 'single' mode on the 4 originals); sums equal the CanMehBench totals |
| data file ride.fit | 302889 bytes; 10809 messages; 140448 fields; sha256 2ba822794922b430... | build/data/*.fit; counts from the stock decoder (scripts/followup/driver.cpp 'single' mode on the 4 originals); sums equal the CanMehBench totals |
| data file treadmill.fit | 97448 bytes; 5406 messages; 54026 fields; sha256 46a60603dab88e46... | build/data/*.fit; counts from the stock decoder (scripts/followup/driver.cpp 'single' mode on the 4 originals); sums equal the CanMehBench totals |
| regions (functions / units the search can rewrite) | 5514 | profile_samples.json (round-2 runs) |
| regions with profile samples (per run, 20 s perf) | 76 (ds-population-s1); ~70-80 in other runs | runs/*/profile.json, profile_samples.json |
| compiler | c++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0 (GCC) | runs/*/run.json compiler_version |
| compiler options for stock and candidates | -std=c++17 -O2 (C1 controls: -O3, -O3 -march=native which resolves to haswell) | runs/*/run.json (opt, cxxstd); runs/controls-native-1071478/node.txt |
| measurement parameters | 10 processes x 9 repetitions per measurement (--repeat 10 --repetitions 9), min-time 0.25 s, alpha 0.01, minimum effect 2%, unstable if ratio spread > 0.25 | runs/*/run.json meta, rule; src/Search.cpp constants |
| machine | NUS cluster compute nodes xcnc*/xcnd*: 2 x Intel Xeon E5-2620 v3 @ 2.40 GHz (6 cores, 2 threads each, 24 logical CPUs, max 3.2 GHz, 64 GB, 30 MiB L3), governor schedutil, Linux 6.8.0-1xx; whole node per job | runs/phase1-final/node_hardware/*.txt; runs/*/node.txt |
| models: Qwen | requested qwen3-coder-next, returned qwen3-coder-next (server fingerprint vllm-0.26.0-1cf708c9); temperature 0.8; max_tokens 4096 | runs/setup/llm-check.json; runs/main/*/run.json; runs/round2/runs/qwen-*/results.jsonl llm.model_returned |
| models: DeepSeek | requested deepseek-v4.1-flash, every response returned deepseek-v4.1-flash-1017 (expected id enforced); temperature 0.8; max_tokens 32768; request timeout 600 s | runs/deepseek/*/run.json; results.jsonl llm.model_returned |
| endpoint | https://soclaas-api.comp.nus.edu.sg/v1 (chat completions); one HTTP request per model call in code I2/I3 | runs/*/run.json base_url |

**节点差异。** 同一份原库,`xcnc` 节点上一次完整解码约 358–360 ms,`xcnd` 节点约 480 ms(40 个运行的基线范围 358–482 ms)。所以**不同节点的绝对毫秒数不能直接比较**;本文件只比较同一进程对内测得的 ratio/speedup。I1 和 I2 的运行混合使用 xcnc 和 xcnd(与种子没有平衡),I3 的运行主要在 xcnc(逐运行节点见 `tables/run_baselines_and_parameters.csv`)。

### 1.3 课程提供了什么,我们实现了什么

课程提供 6 个程序:`CanMehHarness`(复制 SDK、拼接补丁、编译并检查候选库)、`CanMehBench`(在同一进程里对两个库交替计时、做校验)、`CanMehCalibrate`(校准对)、`CanMehDataGenerator`(生成 4 个文件)、`CanMehDecodeForSampler`(供 perf 采样)和需要自己写的 `CanMehSearch`。**我们实际编写的只有 `src/Search.cpp`**(主循环、系统提示词与用户提示词、回复解析、判定规则 `candidateIsFaster`/`analyzeTimings`、种群与函数选择、预算与续跑),以及运行和分析用的脚本(`scripts/`)。其余五个程序按课程原样使用。(I3 中还用我们自己的 HTTP 适配代替课程客户端,目的是让“请求数”可核查,见 §2.)

### 1.4 每一轮从选函数到保留候选的完整流程

```
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

**系统提示词**要求模型保持签名、对每个输入行为完全一致(校验值和 profile 全域扫描会拒绝任何行为差异)、不要使用线程,只改这一个函数。提示词**没有**提到线程安全或并发调用——这和 §7 的发现直接相关。

## 2. 三种搜索方法:实际实现和证据

### 2.1 统一比较表(以当前实际代码为准;“仅部分模式存在”的机制已标出)

|  | 种群搜索 | greedy 单链 | best-of-N |
|---|---|---|---|
| 每次从哪个版本开始改 | **父补丁**(从种群里选出的一个已测候选,含它继承的全部改动) | **当前记录补丁**(累计所有已接受的改动) | **原库**(每次都从零开始) |
| 父补丁如何选 | 二选一锦标赛:随机取两个种群成员,ratio 较小者当父(种群为空时用原库)。`pickParent` | 永远是记录补丁(无选择) | 无父补丁 |
| 如何选函数 | 与另两种相同的“采样加权 90% / 均匀 10%”;**另有 25% 的“收益分支”(仅此模式)** | 采样加权 90% / 均匀 10% | 采样加权 90% / 均匀 10% |
| 是否继承已有修改 | 是(子补丁在父补丁之上拼接) | 是(累计) | 否 |
| 接收性能反馈 | 是:提示词里有父补丁和“目前保留的最好”的 ratio | 是:同样的两个数字 | 否:提示词里两个数字固定为 1.000 |
| 接收失败反馈 | 是:compile/link/检查失败后下一轮带失败原因和被拒绝的代码重试一次(I3、I1) | 否 | 否 |
| 保留候选的条件 | 每个测到的候选都进种群(哪怕更慢);种群超过 6 个时淘汰 ratio 最大的 | 记录规则:第一次测量稳定(不 unstable)且 ratio < 记录,第二次测量也稳定,R = max(两次 ratio) < 记录 → 成为新记录。**不要求 p<0.01,不要求 2% 门槛**(I2) | 同左,但永远不继承;只记录“最好的一次”(I2);I3 的匹配版本用确认规则 |
| 什么条件称为“统计确认的加速” | 两次测量都满足:平均 log 比 < 0、精确符号翻转 p < 0.01、ratio ≤ 0.98(且不 unstable) | 搜索中只有诊断标记 `confirmed`(两次都通过规则);对外的确认值来自固定最终补丁的 3 次独立复测 | I3、I1:同种群搜索的两次确认;I2:同 greedy 的诊断标记 |
| 适用的代码版本 | I1、I3 | I2 | I1、I2、I3 |

**说明:** (1) 种群搜索中候选的 ratio 是**整个累计补丁**对原库的 ratio;一个已经被确认的父补丁的所有后代,即使自己的改动没有贡献,也会因继承而再次被确认。`improved_on_parent` 才是“这一步比父补丁更好”。(2) I2 的排序规则没有显著性检验,也没有 2% 门槛,所以 §3C 要专门检验“空搜索会不会靠噪声产生假进步”。

### 2.2 函数性能采样如何变成选择概率

`perf` 对解码循环采样 20 秒,把每个样本归到它所在的 region(函数)。设 region r 得到 s_r 个样本,总样本 S,region 总数 N = 5514。`pickRegion` 的逻辑:

```
pickRegion():                                     # src/Search.cpp:1352
    if 种群搜索 and U1 < 0.25 and 存在“收益 > 0”的 region:   # 收益 = 已接受候选相对其父补丁的 ratio 改善量
        return 收益最大的 region                             # “利用历史收益”的分支(I1、I3 的种群搜索才有)
    if S > 0 and U2 >= 0.10:                                 # 90%:按样本加权
        return 以概率 s_r / S 抽到 r
    return 在全部 5514 个 region 上均匀抽一个                # 10%:均匀
```

没有收益记录或不是种群搜索时,一次抽取选中 region r 的概率就是 **P(r) = 0.9 · s_r / S + 0.1 / 5514**。有收益记录的种群搜索:P(r) = 0.25 · 1[r 是收益最大者] + 0.75 · (0.9 · s_r / S + 0.1 / 5514)。

**实际作用。** 5514 个 region 里只有约 76 个有样本。所以 90% 的抽取集中在这 76 个热点函数,其中最热的 `Profile::GetMesg` 约占样本的 19%;而 10% 的均匀抽取里,约 98.6% 落在**没有样本**的函数上(多数是一行的 getter/setter,被编译器内联,不会出现在 profile 里,但改写它们仍可能有收益)。下表是一个运行(ds_pop_I3 种子 1)里前 10 个函数的样本占比和每次抽取的概率:

| 名次 | 函数 | 样本数 | 占有样本的比例 | 单次抽取概率(无收益分支) | 本运行实际抽到次数 |
|---|---|---|---|---|---|
| 1 | Profile::GetMesg | 1376 | 19.4% | 17.48% | 0 |
| 2 | Field::GetType | 708 | 10.0% | 9.00% | 2 |
| 3 | Field::GetNum | 515 | 7.3% | 6.54% | 1 |
| 4 | FieldBase::FieldBase | 495 | 7.0% | 6.29% | 16 |
| 5 | Field::Field | 403 | 5.7% | 5.12% | 2 |
| 6 | Profile::GetFieldIndex | 367 | 5.2% | 4.66% | 1 |
| 7 | FieldBase::GetValue | 286 | 4.0% | 3.63% | 0 |
| 8 | Mesg::GetField | 265 | 3.7% | 3.37% | 0 |
| 9 | FieldBase::Read | 176 | 2.5% | 2.24% | 1 |
| 10 | FieldBase::GetNumValues | 167 | 2.4% | 2.12% | 1 |

**各 DeepSeek I3 运行汇总:预期与实际抽取份额(8 个最热函数,10 个运行、共 370 次独立抽取):**

| 函数 | 平均样本占比 | 按公式预期的抽取份额 | 实际抽取份额 | 实际次数 |
|---|---|---|---|---|
| Profile::GetMesg | 19.2% | 17.3% | 15.4% | 57/370 |
| Field::GetType | 10.5% | 9.5% | 7.8% | 29/370 |
| Field::GetNum | 7.3% | 6.6% | 6.5% | 24/370 |
| FieldBase::FieldBase | 6.6% | 6.0% | 14.1% | 52/370 |
| Field::Field | 5.5% | 4.9% | 4.6% | 17/370 |
| Profile::GetFieldIndex | 4.6% | 4.2% | 4.9% | 18/370 |
| FieldBase::GetValue | 4.4% | 4.0% | 3.8% | 14/370 |
| Mesg::GetField | 3.4% | 3.0% | 1.9% | 7/370 |

`FieldBase::FieldBase` 的实际份额(14.1%)高于按公式预期的 6.0%。分开看:DeepSeek 种群搜索(有 25% 收益分支)占 32/170 = 18.8%,三个没有收益分支的 DeepSeek/Qwen best-of-N 与 greedy 配置占 9.0%–10.8%。收益分支确实让种群搜索更常回到已经有收益的函数;没有收益分支的配置里仍略高于 6.5%,但**同一个种子编号在所有配置里使用同一条 mt19937 随机数流**,没有收益分支的 4 个配置的抽取序列因此高度相关(有效独立样本大约只有 5 个种子 × 40 次),这点超出预期不能当作 4 倍的独立证据。

### 2.3 同一个函数能否被重复选择?为什么 40 次请求不等于 40 次成功优化

**能。** 每次抽取都是有放回的独立抽取,没有“已选过就排除”的机制;种群搜索的失败重试还会**有意**在同一函数上再抽一次。下表是各配置(5 个种子汇总)的实际情况(只统计非重试的独立抽取):

| 配置 | 独立抽取总数 | 每运行不同函数数(中位数) | 每运行重复抽取数(中位数) | 同一函数最多被抽到(中位数) | 落在无样本函数的比例 | 落在前 5 热点的比例 |
|---|---|---|---|---|---|---|
| Qwen 种群搜索 (I1) | 164 | 18 | 14 | 8 | 15.9% | 46.3% |
| Qwen best-of-N (I1) | 200 | 20 | 20 | 7 | 11.5% | 44.5% |
| Qwen 种群搜索 (I3, README 循环) | 172 | 18 | 13 | 6 | 11.6% | 45.9% |
| Qwen best-of-N (I3, 匹配对照) | 200 | 22 | 18 | 7 | 10.5% | 44.0% |
| DeepSeek greedy 单链 (I2) | 203 | 23 | 19 | 7 | 13.3% | 47.3% |
| DeepSeek best-of-N (I2, 排序规则) | 200 | 21 | 19 | 7 | 11.5% | 43.0% |
| DeepSeek 种群搜索 (I3, README 循环) | 170 | 19 | 15 | 8 | 7.6% | 51.8% |
| DeepSeek best-of-N (I3, 匹配对照) | 200 | 20 | 20 | 7 | 10.5% | 45.5% |

(I1、I2 的运行只保存了前 40 个热点的样本,统计“无样本函数”时把第 41 名之后的有样本函数也算成了无样本,所以这两版的“无样本比例”略偏高。)

**40 次请求去了哪里。** 下表是每个配置的 40 次请求的结局(各结局数量取 5 个种子的中位数,所以每行之和不严格等于 40)。“确认但不比父补丁好”的绝大部分是**继承**:一个父补丁已经确认,它的后代只要没破坏它就会再次通过规则。

| 配置 | 无可用回复(HTTP 错误/无代码/截断) | 与原文相同 | 编译或链接失败 | 未通过课程检查 | 测了但没被确认更快 | 确认但不比父补丁好 | 新步骤被接受 / best-of-N 独立确认 |
|---|---|---|---|---|---|---|---|
| Qwen population (I1) | 0 | 3 | 7 | 4 | 11 | 5 | 6 |
| Qwen best-of-N (I1) | 1 | 4 | 11 | 2 | 18 | 0 | 3 |
| Qwen population (I3) | 0 | 3 | 7 | 8 | 12 | 1 | 4 |
| Qwen best-of-N (I3) | 1 | 4 | 8 | 3 | 19 | 0 | 3 |
| DeepSeek greedy (I2) | 4 | 2 | 7 | 2 | 12 | 2 | 11 |
| DeepSeek best-of-N (I2) | 0 | 4 | 4 | 1 | 25 | 0 | 4 |
| DeepSeek population (I3) | 8 | 1 | 7 | 1 | 1 | 9 | 12 |
| DeepSeek best-of-N (I3) | 4 | 3 | 5 | 1 | 15 | 0 | 13 |

所以:**40 次请求 ≠ 40 次成功优化**。例如 DeepSeek 种群搜索(I3)每个运行中位数约 8 次请求遇到 HTTP 502(没有回复,也没有 usage),约 7 次编译失败;整个搜索里“比父补丁更好”(`improved_on_parent`)的候选中位数 12 个,其中进入最终补丁谱系的约 5 个,最终补丁的谱系深度中位数 8 层。

### 2.4 源码位置

| 机制 | 位置 |
|---|---|
| 函数选择 `pickRegion` | `src/Search.cpp:1352`(I3);`archive/qwen-experiment/Search.cpp:1061`(I1);`git show d5aa9e7:src/Search.cpp` 第 1321 行(I2) |
| 父补丁 `pickParent` | `src/Search.cpp:1345`;I1:`archive/.../Search.cpp:1055`;I2:`d5aa9e7` 第 1314 行(排序规则下返回记录补丁/原库) |
| 判定规则 `analyzeTimings` / `signFlipPValue` | `src/Search.cpp:384` / `:364` |
| 排序规则(greedy/best-of-N, I2/I3 代码里的 rankMode) | `src/Search.cpp:1600`(`possiblyBetter`、`R = max(ratio_1, ratio_2)`) |
| 确认规则、`improved_on_parent`、种群更新 | `src/Search.cpp:1662`(`needSecond`)、`:1668`(`confirmed`)、`:1671`(`improved`)、`:1712`/`:1715`(入种群/淘汰) |
| 失败重试 | `src/Search.cpp:1381`(`isRepairable`)和 `repair.active` |
| 提示词 | `src/Search.cpp:581`(`systemPrompt`)、`:601`(`userPrompt`) |
| 采样与权重 | `src/Search.cpp:1253`–`1290`(perf 采样、`weighRanges`) |
| 预算与续跑(仅 I3) | `src/Search.cpp` 循环头 `if (calls >= budget)`;`state.json`、`--resume` |

### 2.5 课程要求核对表(“实现了”与“正式实验实际使用了”分开)

| 要求 | 代码里是否实现 | 正式实验里是否实际使用 | 证据 | 状态 |
|---|---|---|---|---|
| 种群:最多 6 个补丁,按 ratio 排序,淘汰最差,每个测到的候选都保留 | I1 有;I3 有;I2 代码里有该模式,但 I2 正式运行用的是排序模式 | 种群搜索(I1、I3)用了;greedy 和所有 best-of-N 没有(单记录/设计上无记忆) | src/Search.cpp population 向量、stable_sort、pop_back;runs/round2/runs/*/state.json | 满足 |
| 父补丁用二选一锦标赛选出;子补丁在父补丁之上(谱系/继承) | I1 有;I3 有;I2 的 greedy 在当前最好补丁上继续(无锦标赛) | 种群搜索用了;greedy 累计但无锦标赛;best-of-N 永远从原库 | src/Search.cpp pickParent;results.jsonl parent、parent_ratio | 满足 |
| 失败(编译、检查)反馈到下一轮提示词(一次修复尝试) | I1 有;I3 有;I2 无 | 种群搜索用了;greedy 没有;best-of-N 没有(C3 要求无反馈) | src/Search.cpp isRepairable / repair.active;results.jsonl repair_attempt | 满足 |
| 第 1 代之前做一次 profile;按样本比例抽函数,10% 均匀 | 所有版本 | 全部 40 个运行:20 s perf 采样,均匀份额 0.1(续跑的运行复用保存的 profile) | runs/*/profile.json、profile_samples.json;run.json sample_seconds、uniform_share | 满足 |
| 收益分支:有最大已记录收益的函数被抽到更多 | I1 有;I3 有(25% 份额,是我们自己的选择);I2 无 | 只有种群搜索用了 | src/Search.cpp pickRegion 收益分支;regions_tried.json best_gain | 部分(机制由我们设定) |
| 搜索前用 CanMehHarness init 做 null_ok 检查 | 所有版本 | 全部 40 个运行 null_ok = true(I3 每一段都检查) | runs/*/run.json null_evidence;segments/*.init.json | 满足 |
| 每个候选在计时前过课程提供的检查(库能载入、4 个文件校验值、profile 查询摘要、自己不开线程、处理器时间) | 课程提供的 harness | 全部 40 个运行;失败计入 runs_all.csv 的 check_fail | results.jsonl stage;runs/*/harness/ | 满足 |
| 判定规则用原始 timings(measure-patch --no-decision)和自己的统计 | 所有版本 | 所有运行;Phase 0 的 680 个有效试验(681 个文件,1 个不可读)重放与已存判定 0 条不一致 | src/Search.cpp analyzeTimings;tables/calibration_checks.json | 满足 |
| 候选只有两次测量都通过规则才算“确认” | I1、I3 是确认规则;I2 用排序规则(R = 两次 ratio 的最大值,无显著性、无 2% 门槛),确认只作诊断标记 | I1、I3 用了;I2 greedy/best-of-N 只用排序;确认值由固定最终补丁的独立复测给出 | results.jsonl confirmed、rule_pass_1/2;tables/runs_all.csv | 部分(I2) |
| credits.csv 恰好是 generation,calls,prompt_tokens,completion_tokens,total_tokens,best_confirmed_speedup,best_retained_speedup,elapsed_s | I1 有;I3 有;I2 无(排序模式列:含 reasoning_tokens、best_ranked_speedup) | I1、I3 满足;I2 不符合(已记录);所以 I2 的课程指标用独立复测值计算 | runs/*/credits.csv 表头 | 部分(I2) |
| 预算 = 40 次模型调用;按调用数比较,不按代数 | I1:40 次调用(可能有隐藏重试);I2/I3:40 个 HTTP 请求 | I1 40 次模型调用;I2 40 个 HTTP 请求(种子 1、3、4、5 在作业时限处停在 39、38、34、34,由重放此前抽取的续跑补足);I3 恰好 40 个请求 | summary.json api_calls / http_attempts;results.jsonl llm.http_attempts | 满足(I1 的请求数不可核实) |
| 每个配置至少 5 个种子;报告中位数和完整范围(C4) | — | 8 个配置全部 5 个种子 | tables/config_summary.csv | 满足 |
| C1 编译器对照:-O2、-O3、-O3 -march=native | — | 在一个节点(xcnd24)上,每个比较 5 次测量;第一个 -march=native 批次无效,已由后一批取代 | tables/controls_summary.csv | 满足 |
| C2 人工对照:一个计时的小时,报告补丁和时间 | — | 测了两个人工补丁;一小时的计时没有记录(只有文件时间);AI 辅助 | runs/human-control/c2-1058781/ | 部分(无计时) |
| C3 同调用预算的独立采样(从原库的 best-of-N,无记忆) | I1、I2、I3 | Qwen:I1 与 I3 两组;DeepSeek:I3 一组(确认规则)和与 greedy 配对的 I2 best-of-N(排序规则) | tables/within_model_tests.csv | 满足 |
| 记录实际回答的模型 id;token 与声称的加速并列 | I1 只有一次探测;I2/I3 逐请求 | DeepSeek:每个响应都是 deepseek-v4.1-flash-1017;Qwen I1:只有一次探测;I3:逐请求;58 个 DeepSeek 请求返回 HTTP 502 且无 usage(消耗未知,不是 0) | results.jsonl llm.model_returned、usage_seen | 满足 |
| 同时最多提交 4 个 LLM 作业 | — | I1:10 个作业,观察到最多 4 个并发;I2:观察到 8 个并发(种子 2–5 的作业按指示同时启动);I3:4 条链 | 各 node.txt 起止时间;runs/deepseek/submission-s2-5.txt;tables/llm_job_concurrency.csv | 部分(I2 超过 4) |
| 只在 xcnc 或 xcnd 计算节点计时,整节点,一作业一节点 | — | 是;xcnc 上原库解码约 358 ms,xcnd 约 480 ms(节点类别在 I1/I2 里与种子不平衡) | runs/*/node.txt;tables/run_baselines_and_parameters.csv | 满足 |
| Phase 0:误报率、检测阈值(各效应的检出率)、偏差;试验数与参数 | — | 校准:主要六对各 100 个试验(两批),sweep 各 20;合成 null 500;SDK 无效补丁 804 | tables/calibration_pairs.csv、fpr_summary.csv | 满足 |
| 在 SDK 里拼接无效补丁并评测 | — | src/fit.cpp 的仅注释补丁;16 个批次共 804 次测量,另有 5 次手工测量 | runs/inert-check/inert.patch | 满足 |

状态:满足 = 已实现且正式运行使用;部分 = 部分满足(括号内是缺口)。


## 3. 我们的测速和判断可信吗?

### 3.1 统计量的含义和当前实际规则

| 量 | 定义(`src/Search.cpp:384` `analyzeTimings`,`:364` `signFlipPValue`) |
|---|---|
| 一次测量 | 10 个独立进程 × 每进程 9 次重复(`--repeat 10 --repetitions 9`);每个进程里原库与候选交替计时,约一半进程先测候选(`swapped`)以抵消顺序效应;每次重复内部迭代到至少 min-time(0.25 s,校准对按工作量缩放)。 |
| 进程比值 | 进程 p 的 `ratio_p = median(候选 9 次耗时) / median(原库 9 次耗时)` |
| ratio、speedup | `ratio = median_p(ratio_p)`;`speedup = 1 / ratio`;下降 % = 1 − ratio;提高 % = speedup − 1 |
| p 值 | 对 `log(ratio_p)` 的 10 个值做**精确符号翻转检验**(2¹⁰ = 1024 种符号组合,双侧);最小可能 p = 2/1024 = 0.00195 |
| “判为更快” | 三个条件同时成立:平均 log 比 < 0(方向);p < α = 0.01(统计);ratio ≤ 0.98(幅度,即至少 2% 下降,`--min-effect 0.02`) |
| 不稳定 | 进程比值的极差(最大 − 最小)> 0.25 视为不稳定:不更新记录,且会触发复测 |
| 推断单位 | 10 个**进程**(独立的 OS 进程,各自重新加载库),不是 90 次重复;所以 9 次重复之间的自相关不直接进入 p 值,只影响各进程中位数的噪声 |

**三个层次不要混淆:**

| 层次 | 做法 |
|---|---|
| ① 搜索中的排序(greedy / best-of-N,I2) | 第一次测量 r1 稳定且 < 记录 → 第二次测量 r2;`R = max(r1, r2)`;`R < 记录` 才更新。**没有 p 值检验、没有 2% 门槛**。作用是挑出“看起来更好”的候选 |
| ② 搜索中的双次确认(种群搜索、匹配 best-of-N,I1/I3) | 第一次测量满足规则(或不稳定)才做第二次;两次都满足规则才记为 `confirmed`;候选的 ratio 取两次中**较差**的那个 |
| ③ 最终独立复测 | 一次运行结束后,把**固定的最终补丁**在单独作业里再完整测 3 次(每次 10×9);报告 3 次 ratio 的中位数对应的 speedup 和通过规则的次数。这是对外报告的数字 |

我们用独立的 Python 实现重放了仓库里**所有**保存了原始 timings 的测量(Phase 0 的 680 个有效试验、全部误报测量、控制、搜索中和复测中的测量),决定与 C++ 保存值的差别:Phase 0 的 681 个文件重放与已存的逐试验结果 **0 条不一致**(其中 1 个文件损坏不可读,已排除并计数)。

### 3.2 A. 已知真实比例的校准实验

校准对由课程提供:原库和候选库做完全相同的事,只是候选的循环次数是原库(20000 单位)的 `候选单位/20000`;**精确真实比例 = 候选单位 / 参考单位**(假设耗时与工作量成正比,由下表偏差检验)。主要六对各做 100 个有效试验(两个批次、同一节点 xcnc2,各 50),4 个 sweep 对各 20 个(只做了批次 1)。一个 null 试验文件损坏,被排除并计数,所以 null 是 100 个有效试验。

| 校准对 | 参考/候选工作量 | 精确真实比 | 真实降幅 | 有效试验 | 判为更快 | 比例 | 95% CP 区间 | 中位报告比 | 绝对偏差 | 相对误差 |
|---|---|---|---|---|---|---|---|---|---|---|
| null | 20000/20000 | 1.00000 | 0.000% | 100 | 0 | 0.0% | [0.000%, 3.622%] | 1.00038 | +0.00038 | +0.038% |
| faster-1-percent | 20000/19801 | 0.99005 | 0.995% | 100 | 1 | 1.0% | [0.025%, 5.446%] | 0.98973 | -0.00032 | -0.032% |
| faster-2-percent | 20000/19607 | 0.98035 | 1.965% | 100 | 42 | 42.0% | [32.199%, 52.288%] | 0.98084 | +0.00049 | +0.050% |
| faster-5-percent | 20000/19047 | 0.95235 | 4.765% | 100 | 99 | 99.0% | [94.554%, 99.975%] | 0.95380 | +0.00145 | +0.152% |
| faster-10-percent | 20000/18181 | 0.90905 | 9.095% | 100 | 100 | 100.0% | [96.378%, 100.000%] | 0.90926 | +0.00021 | +0.023% |
| slower-10-percent | 20000/22000 | 1.10000 | -10.000% | 100 | 0 | 0.0% | [0.000%, 3.622%] | 1.10090 | +0.00090 | +0.082% |

判为更快 = 单次完整测量(10×9)满足三个条件。区间为精确 Clopper–Pearson 双侧 95%。绝对偏差 = 中位报告比 − 精确真实比;相对误差 = 绝对偏差 ÷ 精确真实比。

**四个加速点的检出率:** 1% → 1/100 (1.0%);2% → 42/100 (42.0%);5% → 99/100 (99.0%);10% → 100/100 (100.0%)。**已测点中达到 90% 检出率的最弱效应是 faster-5-percent(真实降幅 4.765%,speedup 1.050)**;分辨率只到已测的四个点。注意 faster-2-percent 的真实降幅是 1.965%,**略小于 2% 的幅度门槛**,所以 52/100 的试验 p 值通过但被幅度门槛挡住(见下表拒绝原因),42% 的检出率是“真实效应刚好在门槛边缘”的结果,不能说成“2% 能可靠检出”。

**拒绝原因(互斥分类;D = 方向通过,P = p<0.01,M = ratio≤0.98):**

| 校准对 | 各类试验数(键 = 通过的门槛;“-”表示该门槛未通过) |
|---|---|
| null | 三项都未通过 56;仅方向通过 44 |
| faster-1-percent | 仅方向通过 63;方向+p 通过,幅度未过 36;三项都通过(判为更快) 1 |
| faster-2-percent | 方向+p 通过,幅度未过 52;三项都通过(判为更快) 42;仅方向通过 6 |
| faster-5-percent | 三项都通过(判为更快) 99;方向+幅度通过,p 未过 1 |
| faster-10-percent | 三项都通过(判为更快) 100 |
| slower-10-percent | p 通过但方向为慢 100 |

**sweep 对**(批次 1,各 20 个试验;候选工作量是原库的 1.05、1.10、2、4 倍;它们都比原库**慢**,正确地全部不被判为更快)。它们的用途是检查**比例估计随工作量缩放是否保持准确**——不是检出率:

| 对 | 工作量 | 精确真实比 | 有效试验 | 判为更快 | 中位报告比 | 绝对偏差 | 相对误差 |
|---|---|---|---|---|---|---|---|
| sweep-105 | 20000/21000 | 1.05000 | 20 | 0 | 1.05200 | +0.00200 | +0.191% |
| sweep-110 | 20000/22000 | 1.10000 | 20 | 0 | 1.10048 | +0.00048 | +0.043% |
| sweep-200 | 20000/40000 | 2.00000 | 20 | 0 | 2.00759 | +0.00759 | +0.379% |
| sweep-400 | 20000/80000 | 4.00000 | 20 | 0 | 4.02555 | +0.02555 | +0.639% |

相对误差在 +0.04% 到 +0.64% 之间,随比例增大略增(估计比真实值略高,即略偏保守)。`sweep-110` 与 `slower-10-percent` 是同一配置的两个独立测量序列(中位报告比 1.10048 与 1.10090)。

**两个故意错误的校准对**(应该被课程自带的检查拒绝,而不是给出一个数字):

| 对 | 期望被拒绝的阶段 | 实际被拒绝的阶段 | 拒绝信息 |
|---|---|---|---|
| broken-digest | correctness | correctness | checksum 0043616c69627232 does not match the reference 0043616c69627231; the decoder produced different values |
| shared-install-name | load | load | both libraries resolved to one image, so CanMehBench would measure one build twice; check that the two librari |

**单次判定 vs 双次确认(离线配对)。** 双次确认**不是**搜索里实际执行的流程,而是对已有单次试验的离线配对:同一批次、同一校准对内,按试验序号连续配对 (t1,t2)、(t3,t4)……,两个都通过才算接受。配对方式在看到任何 Phase 0 数据之前写进分析脚本(`scripts/analyze_phase0.py`),没有按结果挑选;配对数 = 50(每对),所以分母和单次判定(100 个试验)不同,不能混为同一个试验数量:

| 校准对 | 单次判定 | 离线双次确认 | 双次确认 95% CP |
|---|---|---|---|
| null | 0/100 = 0.0% | 0/50 = 0.0% | [0.00%, 7.11%] |
| faster-1-percent | 1/100 = 1.0% | 0/50 = 0.0% | [0.00%, 7.11%] |
| faster-2-percent | 42/100 = 42.0% | 10/50 = 20.0% | [10.03%, 33.72%] |
| faster-5-percent | 99/100 = 99.0% | 49/50 = 98.0% | [89.35%, 99.95%] |
| faster-10-percent | 100/100 = 100.0% | 50/50 = 100.0% | [92.89%, 100.00%] |
| slower-10-percent | 0/100 = 0.0% | 0/50 = 0.0% | [0.00%, 7.11%] |

校准的局限:只在一个节点(xcnc2)、一个时间段做了 100 个试验;sweep 只有 20 个;检出率的分辨率只到 1%、2%、5%、10% 四个点。xcnd 节点的表现靠 §3.3 的 null 与 SDK 测量补充。

### 3.3 B. 合成 null 与真实 SDK 的无效补丁

两类数据**不混成一个误报率**:合成 null 是课程提供的“原库 vs 同一代码”的校准对(没有任何 SDK 因素);SDK inert 是在真实 SDK 里加一行注释的补丁(`runs/inert-check/inert.patch`,只改 `src/fit.cpp` 的一行注释和一个空行),经 `CanMehHarness` 的完整编译链路,等于“真实库、真实编译”下的 null。**机器码核查:** 该无效补丁和 16 个具有代表性的空搜索候选(每个空搜索运行的“最后一次被接受”和“最后一次测量”的候选)构建出的库,`.text` 段与原库逐字节相同,动态符号表也相同(17/17;`runs/round2/fpr/noop-verification-*`)——代码确实没有变化,所以任何“更快”的判定都是误报。288 个空搜索候选里只核查了这 16 个。

| 组 | 有效测量 | 误接受 | 95% CP | p<0.01(任一方向) | 方向、p 通过但被 2% 门槛挡住 | unstable | ratio 中位数 [最小, 最大] | lag-1 自相关 中位数 [最小, 最大] |
|---|---|---|---|---|---|---|---|---|
| 合成 null, 校准批次 (xcnc2, 2 batches) | 100 | 0 | [0.000%, 3.622%] | 0 | 0 | 0 | 1.00038 [0.99252, 1.01056] | -0.093 [-0.37, 0.26] |
| 合成 null, 补充批次, xcnc | 200 | 0 | [0.000%, 1.828%] | 4 | 2 | 0 | 1.00067 [0.99080, 1.01375] | -0.127 [-0.47, 0.13] |
| 合成 null, 补充批次, xcnd | 200 | 0 | [0.000%, 1.828%] | 3 | 1 | 0 | 0.99952 [0.98518, 1.01199] | -0.100 [-0.36, 0.18] |
| 合成 null, 全部 xcnc (calibration + extra) | 300 | 0 | [0.000%, 1.222%] | 4 | 2 | 0 | 1.00065 [0.99080, 1.01375] | -0.120 [-0.47, 0.26] |
| 合成 null, 全部 | 500 | 0 | [0.000%, 0.735%] | 7 | 3 | 0 | 1.00032 [0.98518, 1.01375] | -0.111 [-0.47, 0.26] |
| SDK 无效补丁, 批次组 A, xcnc | 120 | 0 | [0.000%, 3.027%] | 3 | 1 | 0 | 1.00000 [0.99774, 1.00185] | 0.004 [-0.25, 0.26] |
| SDK 无效补丁, 批次组 A, xcnd | 120 | 0 | [0.000%, 3.027%] | 1 | 0 | 0 | 0.99989 [0.99782, 1.00212] | 0.131 [-0.18, 0.44] |
| SDK 无效补丁, 批次组 B, xcnc | 282 | 0 | [0.000%, 1.300%] | 2 | 2 | 0 | 0.99995 [0.99724, 1.00188] | 0.019 [-0.34, 0.37] |
| SDK 无效补丁, 批次组 B, xcnd | 282 | 0 | [0.000%, 1.300%] | 5 | 3 | 0 | 0.99989 [0.99710, 1.00242] | 0.159 [-0.14, 0.45] |
| SDK 无效补丁, 全部批次, xcnc | 402 | 0 | [0.000%, 0.913%] | 5 | 3 | 0 | 0.99997 [0.99724, 1.00188] | 0.013 [-0.34, 0.37] |
| SDK 无效补丁, 全部批次, xcnd | 402 | 0 | [0.000%, 0.913%] | 6 | 3 | 0 | 0.99989 [0.99710, 1.00242] | 0.150 [-0.18, 0.45] |
| SDK 无效补丁, 全部批次, 两类合并 | 804 | 0 | [0.000%, 0.458%] | 11 | 6 | 0 | 0.99994 [0.99710, 1.00242] | 0.082 [-0.34, 0.45] |
| SDK 无效补丁, 控制作业 (5 手工测量, xcnd24) | 5 | 0 | [0.000%, 52.182%] | 0 | 0 | 0 | 0.99988 [0.99924, 1.00144] | 0.319 [0.15, 0.40] |

**这些数字怎么读:**

- 所有分组误接受都是 0。**95% 上界是否低于 1% 要看分组**:合成 null 合并(500)为 0.735%(低于 1%);但 xcnc 单类 300 个为 1.22%、xcnd 单类 200 个为 1.83%、校准批次的 100 个为 3.62%(都不低于 1%)。SDK 无效补丁每个节点类别 402 个为 0.913%(低于 1%);两类合并 804 个为 0.458%。
- p 值单独使用时并非没有误报:500 个合成 null 里有 7 个 p<0.01(与双侧 α = 1% 的期望 5 个相符),其中 3 个方向为快、但 ratio 高于 0.98 而被 **2% 幅度门槛挡住**;804 个 SDK 无效测量里 11 个 p<0.01,其中 6 个被幅度门槛挡住。也就是说**幅度门槛实际挡住了单靠 p 值会产生的假阳性**。
- 无效补丁的 ratio 全部落在 [0.9971, 1.0024](SDK)和 [0.9852, 1.0138](合成 null)之内,远离 0.98;没有 unstable。
- 批次明细(每个批次的节点、作业号、计数)在 `tables/fpr_by_batch.csv`(27 个批次)。

**自相关(lag-1)怎么统计的:** 每个测量有 10 个进程;对每个进程的候选 9 次重复耗时序列算 lag-1 自相关(用序列自己的均值),取 10 个进程的**中位数**得到“这个测量的自相关”;上表是这些测量级数值的中位数与 [最小, 最大]。长度 9 的序列,样本自相关即使完全独立也有约 −1/9 ≈ −0.11 的偏差,合成 null 的 −0.111 正好如此;SDK 在 xcnd 上为 +0.150、在 xcnc 上为 +0.013,可能说明 xcnd 上重复之间有轻微的缓慢漂移(没有进一步调查原因)。搜索中全部 977 次测量的自相关中位数为 0.027,范围 [−0.33, 0.52]。

### 3.4 C. 无实质优化的空搜索

**做法:** 把 I2 的排序规则(记录更新:r1 稳定且 < 记录 → r2 → `R = max(r1,r2) < 记录`)用在“什么都不改”的候选上——模型被替换成往随机函数里插一行注释。**8 个运行**(xcnc 4 个、xcnd 4 个,种子 1–4),每个运行测量 36 个候选。没有任何模型调用。

| 运行 | 节点 | 测量的候选数 | 记录更新次数 | 累计假进步 | 对应 speedup | 最大单步更新 |
|---|---|---|---|---|---|---|
| xcnc-s1-1088417 | xcnc4 | 36 | 3 | 0.0821% | 1.00082 | 0.0487% |
| xcnc-s2-1088418 | xcnc5 | 36 | 3 | 0.0773% | 1.00077 | 0.0507% |
| xcnc-s3-1088419 | xcnc1 | 36 | 3 | 0.0707% | 1.00071 | 0.0371% |
| xcnc-s4-1088420 | xcnc6 | 36 | 4 | 0.0743% | 1.00074 | 0.0390% |
| xcnd-s1-1088421 | xcnd2 | 36 | 3 | 0.0859% | 1.00086 | 0.0437% |
| xcnd-s2-1088422 | xcnd5 | 36 | 2 | 0.1095% | 1.00110 | 0.0567% |
| xcnd-s3-1088423 | xcnd8 | 36 | 4 | 0.0620% | 1.00062 | 0.0398% |
| xcnd-s4-1088424 | xcnd9 | 36 | 2 | 0.0850% | 1.00085 | 0.0629% |

**指标:** 单步更新 = 100 × (1 − R_新 / R_前),单位 %(相对前一个记录);累计假进步 = 100 × (1 − 最终记录),单位 %(ratio 下降的百分点);speedup = 1/最终记录。

**结果:** 8 个运行共 24 次更新(每运行 2–4 次);单步更新中位数 0.024%,最大 0.063%;累计假进步中位数 0.080%,最大 0.109%;没有任何空候选在单次测量中通过完整规则。

**与真实搜索比较(比较的是 DeepSeek greedy 的 5 个运行、40 请求时的全部 51 次记录更新):** 真实更新的中位数为 0.56%,最大 6.93%;其中 4/51 次不大于空搜索观察到的最大单步(0.063%),15/51 次不大于 0.2%,21/51 次不大于 0.5%。也就是说,**真实 greedy 链里相当一部分早期小步(尤其 0.2% 以下)在大小上与纯噪声产生的更新不可区分**;大步(几个百分点)远超噪声。

**不能怎么用这个结果:** 8 个运行里观察到的最大漂移(0.109%)和最大单步(0.063%)**不是通用的噪声上限**——只有 8×36 个候选、4 个种子、两类节点;不能据此断言“超过它的步骤一定是真实改进”,也不能断言“低于它的步骤一定是噪声”。它只说明:排序规则本身在没有 2% 门槛和显著性检验时,会在 36 个候选里“收获”约 0.06–0.11% 的虚假进展。


## 4. 编译器与人工优化能做到什么?

### 4.1 C1:编译器选项

原库和候选都用 `g++ -O2 -std=c++17`。C1 在**同一节点(xcnd24)**上,把整个库分别用 `-O2`、`-O3`、`-O3 -march=native`(解析为 haswell)重新编译,用同样的 `measure-pair` 计时,每个比较重复 5 次测量。“批次”指不同的 Slurm 作业:`-O3` 比 `-O2` 在两个批次里各测了一次;`-march=native` 的第一个批次的初始化失败(`init-O3native.json` 里 ok=false),其 ratio 恒为 1.0 不是比较,已作废并由第二个批次取代。

| 比较 | 批次 | 节点 | 测量次数 | ratio 中位数 | speedup 中位数 | speedup 范围 | 通过规则次数 |
|---|---|---|---|---|---|---|---|
| -O3 vs stock -O2 | batch 1068897 (xcnd24) | xcnd24 | 5 | 0.9165 | 1.0911 | [1.0885, 1.0937] | 5/5 |
| -O3 vs stock -O2 | batch 1071478 (xcnd24) | xcnd24 | 5 | 0.9176 | 1.0898 | [1.0876, 1.0919] | 5/5 |
| -O3 -march=native vs stock -O2 | batch 1071478 (xcnd24) | xcnd24 | 5 | 0.9022 | 1.1084 | [1.1063, 1.1084] | 5/5 |
| -O3 -march=native vs -O3 (native's own increment) | batch 1071478 (xcnd24) | xcnd24 | 5 | 0.9862 | 1.0140 | [1.0138, 1.0157] | 0/5 |

**读法:** `-O3` 给出约 1.09(两个批次 1.0911 与 1.0898,在各自范围内重合),`-O3 -march=native` 给出 1.1084;native 相对 `-O3` 的直接比较为 1.0140(5 次测量都没过 2% 门槛,范围很窄)。同一作业里间接推得 1.1084/1.0898 = 1.0171,与直接测得的 1.0140 相差 0.3 个百分点,说明这些单节点、5 次测量的数字各自有约 ±0.2% 的不确定。注意:所有 C1 比较都来自同一个节点 xcnd24,没有跨节点重复;表里的绝对毫秒数(在 `tables/controls_summary.csv`)来自不同批次/节点,不应直接比较。

### 4.2 C2:人工优化(重新阅读了实际补丁)

两个人工补丁都只改 `src/fit_profile.cpp`(补丁文件:`runs/human-control/c2-1058781/attempt-1.patch`、`attempt-2.patch`):尝试 1 改 1 处(15 行加、5 行减);尝试 2 改 2 处(37 行加、12 行减),包含尝试 1 的全部改动。

**改了什么(以实际补丁为准):**

1. `Profile::GetMesg(num)`(两个补丁都有)。**原来:** 对 `mesgs[]` 数组(共 124 个消息类型)线性扫描,逐个比较 `mesgs[i].num == num`,找到就返回。解码时对每条消息都会调用(它是 profile 里最热的函数,约占样本的 19%)。**修改后:** 第一次调用时建一个 65536 项的指针表 `byNumber[消息号]`(每项指向对应的 `MESG`,没有则为空),之后每次查找是一次数组读。**为什么减少了工作:** 原来最坏要比较 124 次(具体次数取决于消息号在数组中的位置),现在是 1 次内存读取。一个简单例子:找消息号 20(record 消息)——原来从第 0 项开始逐项比较直到命中;现在直接读 `byNumber[20]`。

2. `Profile::GetFieldIndex(mesgNum, fieldNum)`(仅尝试 2)。**原来:** 先 `GetMesg`,再对该消息的字段数组线性扫描找 `fields[i].num == fieldNum`。**修改后:** 建一张 `[消息类型][256]` 的字段号→下标表(124 × 256 × 2 字节),直接查表。

**为什么人工版本与部分模型版本在并发安全性上不同。** 两个人工补丁把表放在函数内的 **`static const LookupTable table;`**——一个带构造函数的静态局部对象。C++11 保证这种静态局部对象的初始化是**线程安全的一次性初始化**,多线程同时第一次调用也只有一个线程执行构造,其余等待。大部分模型补丁写的是 `static bool initialized = false;` 加手写的 `if (!initialized) { 建表; initialized = true; }`:两个线程同时第一次调用会同时建表、同时读写 `initialized`,是数据竞争;另一些补丁(如 greedy 链的 `GetFieldIndex` 缓存 `cachedMesg`)在**后续每次调用**里改写共享的静态变量,即使不是第一次调用也会竞争并可能返回错误的下标(§7 中 4 线程测试里,链上第一次出现并发错误输出的补丁正是新增这类缓存的那一步)。课程自带检查只在单线程里解码、并检查候选自己不开线程,所以不会发现这类问题。

**结果:**

| 人工补丁 | 测量次数 | speedup 中位数 | 范围 | 通过规则 | 节点 |
|---|---|---|---|---|---|
| human patch attempt 1 (fit_profile.cpp: GetMesg table) vs stock -O2 | 5 | 1.0683 | [1.0674, 1.0687] | 5/5 | xcnd24 |
| human patch attempt 2 (GetMesg + GetFieldIndex tables) vs stock -O2 | 5 | 1.0821 | [1.0815, 1.0824] | 5/5 | xcnd24 |

两个补丁都是在一个作业(1068897,xcnd24)里各测 5 次,没有跨节点或跨批次的重复测量。**扩展正确性:** 两个补丁在 §7 的全部测试条件下(与原库差分、ASan/UBSan、4 线程 TSan)都没有发现问题(见 §7 总表;该测试语料不含 SDK 编码器写出的合法文件,只含 4 个原始文件和 400 个变异文件)。

**人工时间证据的实际情况:** 课程要求“一个计时的小时”。仓库里**没有计时器记录**,只有文件时间戳:热点分析文件 `c2-1054632/hotspots.txt` 在 11 月 1 日 16:29;两个补丁文件在 11 月 2 日 10:30 和 10:51(整个人工环节的文件时间约 10:20–11:11,约 51 分钟)。**这不能证明满足“计时一小时”**,所以报告里不陈述已计时。AI 辅助说明:人工补丁是**人工指导、AI 辅助**完成的(代码、脚本由 Claude Code 在作者指导下编写),具体哪几行由谁键入没有记录。

**与搜索结果对照:** 人工补丁(1.068、1.082)与 DeepSeek 的 best-of-N(中位数 1.073)属同一量级;`-O3`(1.090)和 `-O3 -march=native`(1.108)只改编译选项就超过了所有 best-of-N 配置和人工尝试 1;只有 DeepSeek 的种群搜索与 greedy(中位数 1.165–1.176)明显高于编译器选项。编译选项与源码补丁能否叠加没有测试。


## 5. 搜索是否优于独立采样?

### 5.1 每个配置的定义

| 配置 | 模型(实际模型 id) | 代码版本 | 算法 | 关键参数与预算 |
|---|---|---|---|---|
| qwen_pop_I1 | qwen3-coder-next(只有一次探测请求记录了返回的模型 id,同名) | I1(`archive/qwen-experiment/Search.cpp`,sha256 ce80cd7b…) | 种群 ≤ 6、锦标赛、失败重试、25% 收益分支;确认规则;20 s 采样,10% 均匀 | temperature 0.8,max_tokens 4096;预算 40 次模型调用(提供的客户端可能隐藏重试,HTTP 请求数未记录) |
| qwen_bon_I1 | 同上 | I1 | 每次从原库;无反馈;确认规则 | 同上 |
| qwen_pop_I3 | qwen3-coder-next(每个请求都记录,同名) | I3(sha256 9431cd44…) | 同种群搜索;25% 收益分支 | temperature 0.8,max_tokens 4096,HTTP 超时 180 s,1 次尝试;预算恰好 40 个 HTTP 请求 |
| qwen_bon_I3 | 同上 | I3 | 匹配对照:同模型同提示同参数,每次从原库,无历史无反馈,确认规则 | 同上 |
| ds_greedy_I2 | 请求 deepseek-v4.1-flash;每个响应返回 **deepseek-v4.1-flash-1017**(已强制核对) | I2(`d5aa9e7`,sha256 67935a2f…;续跑用 `Search_resume.cpp`) | 单条累计链;排序规则;无失败反馈;不种群 | temperature 0.8,max_tokens 32768,HTTP 超时 600 s;预算 40 个 HTTP 请求(种子 1、3、4、5 在作业时限处停在 39、38、34、34,由续跑补足) |
| ds_bon_I2 | 同上 | I2 | 每次从原库;排序规则(记录最好一次);无反馈 | 同上(种子 1 的作业时限 9600 s) |
| ds_pop_I3 | 同 DeepSeek | I3 | 种群搜索 + 25% 收益分支 + 失败重试;确认规则 | 同 DeepSeek 参数;预算恰好 40 个 HTTP 请求;每个运行 2 段 Slurm 作业(续跑,跨节点时重测种群) |
| ds_bon_I3 | 同 DeepSeek | I3 | 匹配对照:每次从原库,无历史无反馈,确认规则 | 同上(1 段) |

**公共参数:** 全部配置 20 s perf 采样、10% 均匀抽取、`prompt_hints` 关闭(提示词里不加“该找哪类代码”的提示)、规则 α = 0.01 / 2% 门槛 / 10×9 测量;最终补丁独立复测 3 次。同一个种子编号在所有配置里使用同一条随机数流。

### 5.2 逐种子结果

**成本与过程**(每个运行一行;“请求数”在 I1 是模型调用数,其余是实际发出的 HTTP 请求数;total = prompt + completion,**reasoning 是 completion 的子集,没有重复相加**;“无 usage”请求的消耗未知,**不是 0**,也不在 total 里;续跑段的 token 和时间已计入所属运行):

| 运行 | 节点(按运行顺序) | 请求数 | 结束原因 | prompt | completion | 其中 reasoning | total | 无 usage 请求 | 截断回复 | 搜索耗时 s | 复测耗时 s |
|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen_pop_I1_s1 | xcnc18 | 40* | generations exhausted | 23365 | 5501 | 0 | 28866 | 未记录 | 未记录 | 3752 | 338 |
| qwen_bon_I1_s1 | xcnc18 | 40* | generations exhausted | 19189 | 8774 | 0 | 27963 | 未记录 | 未记录 | 3377 | 285 |
| qwen_pop_I3_s1 | xcnc7 | 40 | request budget reached | 20721 | 5067 | 0 | 25788 | 0 | 0 | 5070 | 427 |
| qwen_bon_I3_s1 | xcnc43 | 40 | request budget reached | 18276 | 6925 | 0 | 25201 | 0 | 0 | 2674 | 426 |
| ds_greedy_I2_s1 | xcnc3/xcnd7 | 40 | generations exhausted | 19254 | 602013 | 593825 | 621267 | 1 | 5 | 9723 | 375 |
| ds_bon_I2_s1 | xcnc41 | 40 | generations exhausted | 18461 | 253693 | 244839 | 272154 | 0 | 0 | 5322 | 286 |
| ds_pop_I3_s1 | xcnc30/xcnc4 | 40 | request budget reached | 16531 | 289203 | 281853 | 305734 | 8 | 0 | 11480 | 390 |
| ds_bon_I3_s1 | xcnc14 | 40 | request budget reached | 16010 | 262979 | 256583 | 278989 | 4 | 0 | 8215 | 418 |
| qwen_pop_I1_s2 | xcnc26 | 40* | generations exhausted | 23154 | 6206 | 0 | 29360 | 未记录 | 未记录 | 3706 | 292 |
| qwen_bon_I1_s2 | xcnd3 | 40* | generations exhausted | 18458 | 9698 | 0 | 28156 | 未记录 | 未记录 | 3656 | 363 |
| qwen_pop_I3_s2 | xcnc43 | 40 | request budget reached | 27028 | 9720 | 0 | 36748 | 0 | 0 | 2992 | 482 |
| qwen_bon_I3_s2 | xcnc3 | 40 | request budget reached | 18391 | 6063 | 0 | 24454 | 0 | 0 | 3267 | 425 |
| ds_greedy_I2_s2 | xcnc41 | 40 | generations exhausted | 20899 | 575762 | 564776 | 596661 | 1 | 2 | 9244 | 287 |
| ds_bon_I2_s2 | xcnc2 | 40 | generations exhausted | 19104 | 280388 | 271575 | 299492 | 1 | 1 | 5836 | 287 |
| ds_pop_I3_s2 | xcnc3 | 40 | request budget reached | 18972 | 402994 | 393777 | 421966 | 6 | 0 | 11349 | 422 |
| ds_bon_I3_s2 | xcnc7 | 40 | request budget reached | 19169 | 301228 | 292029 | 320397 | 1 | 0 | 8100 | 421 |
| qwen_pop_I1_s3 | xcnd22 | 40* | generations exhausted | 27658 | 11854 | 0 | 39512 | 未记录 | 未记录 | 5567 | 418 |
| qwen_bon_I1_s3 | xcnd8 | 40* | generations exhausted | 21047 | 8297 | 0 | 29344 | 未记录 | 未记录 | 3488 | 374 |
| qwen_pop_I3_s3 | xcnc42 | 40 | request budget reached | 23834 | 10962 | 0 | 34796 | 0 | 1 | 2417 | 471 |
| qwen_bon_I3_s3 | xcnc3 | 40 | request budget reached | 21026 | 8337 | 0 | 29363 | 0 | 0 | 2723 | 422 |
| ds_greedy_I2_s3 | xcnd1/xcnd2 | 40 | generations exhausted | 19063 | 342170 | 332737 | 361233 | 4 | 0 | 9832 | 427 |
| ds_bon_I2_s3 | xcnd4 | 40 | generations exhausted | 22707 | 347058 | 335064 | 369765 | 0 | 1 | 8105 | 374 |
| ds_pop_I3_s3 | xcnc19/xcnc6 | 40 | request budget reached | 18686 | 348266 | 337769 | 366952 | 5 | 0 | 12398 | 460 |
| ds_bon_I3_s3 | xcnc33 | 40 | request budget reached | 19779 | 247148 | 237608 | 266927 | 3 | 0 | 7334 | 419 |
| qwen_pop_I1_s4 | xcnc36 | 40* | generations exhausted | 19821 | 8731 | 0 | 28552 | 未记录 | 未记录 | 4005 | 297 |
| qwen_bon_I1_s4 | xcnd23 | 40* | generations exhausted | 18061 | 8295 | 0 | 26356 | 未记录 | 未记录 | 3516 | 378 |
| qwen_pop_I3_s4 | xcnc8 | 40 | request budget reached | 22217 | 6197 | 0 | 28414 | 0 | 0 | 2238 | 406 |
| qwen_bon_I3_s4 | xcnc6 | 40 | request budget reached | 18360 | 8530 | 0 | 26890 | 0 | 0 | 2618 | 422 |
| ds_greedy_I2_s4 | xcnd2/xcnd4 | 40 | generations exhausted | 20248 | 544027 | 531390 | 564275 | 1 | 3 | 10801 | 371 |
| ds_bon_I2_s4 | xcnd5 | 40 | generations exhausted | 18970 | 306564 | 296200 | 325534 | 0 | 0 | 7734 | 376 |
| ds_pop_I3_s4 | xcnc1 | 40 | request budget reached | 19324 | 343035 | 333804 | 362359 | 8 | 0 | 11453 | 420 |
| ds_bon_I3_s4 | xcnc6 | 40 | request budget reached | 19422 | 335516 | 322404 | 354938 | 2 | 0 | 8968 | 419 |
| qwen_pop_I1_s5 | xcnc18 | 40* | generations exhausted | 22007 | 7362 | 0 | 29369 | 未记录 | 未记录 | 6128 | 296 |
| qwen_bon_I1_s5 | xcnc26 | 40* | generations exhausted | 19942 | 9644 | 0 | 29586 | 未记录 | 未记录 | 2219 | 290 |
| qwen_pop_I3_s5 | xcnc3 | 40 | request budget reached | 23216 | 11014 | 0 | 34230 | 0 | 1 | 3686 | 435 |
| qwen_bon_I3_s5 | xcnc25 | 40 | request budget reached | 18929 | 6432 | 0 | 25361 | 0 | 0 | 2946 | 423 |
| ds_greedy_I2_s5 | xcnd3/xcnd5 | 40 | generations exhausted | 20794 | 561425 | 551323 | 582219 | 2 | 2 | 10638 | 367 |
| ds_bon_I2_s5 | xcnd6 | 40 | generations exhausted | 20904 | 442985 | 430495 | 463889 | 0 | 0 | 8535 | 378 |
| ds_pop_I3_s5 | xcnc4/xcnc1 | 40 | request budget reached | 18763 | 362190 | 354764 | 380953 | 7 | 1 | 10891 | 415 |
| ds_bon_I3_s5 | xcnc8 | 40 | request budget reached | 18841 | 347370 | 337561 | 366211 | 4 | 1 | 9088 | 419 |

*I1 的“请求数”是模型调用数;I1 没有逐请求的 usage/截断记录,对应格显示“未记录”。搜索耗时是搜索的 wall-clock(续跑为各段之和,不含排队);复测耗时是搜索结束到第 3 次复测结束(I2/I1 由文件时间推得,I3 为作业起止时间;含重新构建)。


**失败类型与结果**(失败类型计数来自 `results.jsonl` 每行的 `stage`;一个请求最多对应一行,重试和“无请求”的行见 `tables/runs_all.csv`):

| 运行 | 编译失败 | 检查失败 | 与原文相同 | HTTP 失败 | 测到的候选 | 确认的候选 | 搜索中最佳确认 | 独立复测 speedup | 复测通过 | 谱系深度 | 累计接受步数 | 最终补丁改动的文件 | 扩展正确性(最终补丁) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen_pop_I1_s1 | 11 | 6 | 4 | 0 | 19 | 12 | 1.0573 | 1.0573 | 3/3 | 4 | 2 | fit_accumulated_field; fit_field_base; fit_profile; fit_segment_lap_mesg.hpp | not tested |
| qwen_bon_I1_s1 | 7 | 2 | 5 | 0 | 25 | 7 | 1.0740 | 1.0744 | 3/3 | 1 | 1 | fit_profile | not tested |
| qwen_pop_I3_s1 | 7 | 5 | 3 | 0 | 25 | 21 | 1.1235 | 1.1237 | 3/3 | 8 | 6 | fit_accumulated_field; fit_crc; fit_field; fit_field_base; fit_mesg_definition; fit_profile | no finding in tested conditions |
| qwen_bon_I3_s1 | 11 | 4 | 4 | 0 | 21 | 3 | 1.0402 | 1.0389 | 3/3 | 1 | 1 | fit_profile | no finding in tested conditions |
| ds_greedy_I2_s1 | 7 | 3 | 4 | 1 | 20 | 8 | 1.1556 | 1.1574 | 3/3 | 9 | 9 |  | wrong output / crash / memory error |
| ds_bon_I2_s1 | 4 | 1 | 6 | 0 | 29 | 4 | 1.0732 | 1.0730 | 3/3 | 1 | 1 | fit_profile | TSan race only |
| ds_pop_I3_s1 | 4 | 3 | 3 | 8 | 22 | 21 | 1.1634 | 1.1648 | 3/3 | 10 | 7 | fit_field; fit_field_base | wrong output / crash / memory error |
| ds_bon_I3_s1 | 4 | 0 | 5 | 4 | 27 | 13 | 1.0729 | 1.0737 | 3/3 | 1 | 1 | fit_profile | TSan race only |
| qwen_pop_I1_s2 | 10 | 4 | 3 | 0 | 23 | 12 | 1.0754 | 1.0753 | 3/3 | 6 | 3 | fit_field; fit_mesg; fit_profile | not tested |
| qwen_bon_I1_s2 | 10 | 1 | 3 | 0 | 25 | 2 | 1.0573 | 1.0578 | 3/3 | 1 | 1 | fit_field_base | not tested |
| qwen_pop_I3_s2 | 11 | 8 | 2 | 0 | 19 | 5 | 1.0582 | 1.0586 | 3/3 | 6 | 3 | fit_decode; fit_field_base; fit_mesg; fit_profile; fit_segment_file_mesg.hpp | no finding in tested conditions |
| qwen_bon_I3_s2 | 7 | 1 | 1 | 0 | 30 | 2 | 1.0404 | 1.0409 | 3/3 | 1 | 1 | fit_profile | TSan race only |
| ds_greedy_I2_s2 | 10 | 3 | 2 | 1 | 21 | 13 | 1.2146 | 1.2155 | 3/3 | 11 | 11 | fit_decode; fit_field; fit_field_base; fit_mesg; fit_profile | TSan race only |
| ds_bon_I2_s2 | 3 | 1 | 4 | 1 | 29 | 2 | 1.0683 | 1.0688 | 3/3 | 1 | 1 | fit_profile | no finding in tested conditions |
| ds_pop_I3_s2 | 7 | 0 | 1 | 6 | 25 | 21 | 1.1364 | 1.1375 | 3/3 | 8 | 5 | fit_field; fit_field_base; fit_mesg; fit_profile | wrong output / crash / memory error |
| ds_bon_I3_s2 | 7 | 1 | 2 | 1 | 28 | 13 | 1.0735 | 1.0731 | 3/3 | 1 | 1 | fit_profile | TSan race only |
| qwen_pop_I1_s3 | 7 | 6 | 2 | 0 | 25 | 11 | 1.0263 | 1.0266 | 3/3 | 8 | 4 | fit_crc; fit_field; fit_field_base; fit_lap_mesg.hpp | not tested |
| qwen_bon_I1_s3 | 11 | 2 | 3 | 0 | 22 | 3 | 1.0840 | 1.0843 | 3/3 | 1 | 1 | fit_profile | not tested |
| qwen_pop_I3_s3 | 6 | 7 | 8 | 0 | 18 | 1 | 1.0801 | 1.0828 | 3/3 | 6 | 1 | fit_field; fit_field_base; fit_lap_mesg.hpp; fit_profile | wrong output / crash / memory error |
| qwen_bon_I3_s3 | 10 | 0 | 5 | 0 | 22 | 3 | 1.0628 | 1.0622 | 3/3 | 1 | 1 | fit_profile | TSan race only |
| ds_greedy_I2_s3 | 9 | 2 | 5 | 4 | 20 | 11 | 1.1766 | 1.1758 | 3/3 | 13 | 13 | fit_crc; fit_decode; fit_field; fit_field_base; fit_mesg; fit_mesg_broadcaster; fit_mesg_definition; fit_profile | not tested |
| ds_bon_I2_s3 | 4 | 0 | 5 | 0 | 30 | 5 | 1.0738 | 1.0740 | 3/3 | 1 | 1 | fit_profile | TSan race only |
| ds_pop_I3_s3 | 3 | 0 | 0 | 5 | 32 | 23 | 1.1829 | 1.1811 | 3/3 | 11 | 5 | fit_field; fit_field_base; fit_lap_mesg.hpp; fit_profile | TSan race only |
| ds_bon_I3_s3 | 7 | 0 | 4 | 3 | 24 | 11 | 1.0735 | 1.0732 | 3/3 | 1 | 1 | fit_profile | TSan race only |
| qwen_pop_I1_s4 | 5 | 1 | 4 | 0 | 29 | 5 | 1.0404 | 1.0397 | 3/3 | 5 | 2 | fit_field; fit_field_base; fit_profile | not tested |
| qwen_bon_I1_s4 | 11 | 4 | 4 | 0 | 21 | 4 | 1.0609 | 1.0613 | 3/3 | 1 | 1 | fit_profile | not tested |
| qwen_pop_I3_s4 | 6 | 11 | 8 | 0 | 15 | 3 | 1.0313 | 1.0307 | 3/3 | 5 | 2 | fit_field; fit_field_base | wrong output / crash / memory error |
| qwen_bon_I3_s4 | 8 | 3 | 7 | 0 | 21 | 3 | 1.0541 | 1.0560 | 2/3 | 1 | 1 | fit_profile | no finding in tested conditions |
| ds_greedy_I2_s4 | 5 | 0 | 0 | 1 | 30 | 13 | 1.1902 | 1.1919 | 3/3 | 11 | 11 |  | differs only on hostile mutants |
| ds_bon_I2_s4 | 4 | 0 | 4 | 0 | 32 | 4 | 1.0721 | 1.0725 | 3/3 | 1 | 1 | fit_profile | TSan race only |
| ds_pop_I3_s4 | 7 | 1 | 0 | 8 | 24 | 24 | 1.1632 | 1.1634 | 3/3 | 6 | 4 | fit_field; fit_field_base; fit_mesg; fit_profile | TSan race only |
| ds_bon_I3_s4 | 5 | 2 | 2 | 2 | 29 | 13 | 1.0726 | 1.0733 | 3/3 | 1 | 1 | fit_profile | TSan race only |
| qwen_pop_I1_s5 | 7 | 0 | 2 | 0 | 31 | 28 | 1.0806 | 1.0804 | 3/3 | 7 | 6 | fit_field; fit_field_base; fit_mesg; fit_profile | not tested |
| qwen_bon_I1_s5 | 14 | 3 | 5 | 0 | 18 | 1 | 1.0375 | 1.0384 | 3/3 | 1 | 1 | fit_profile | not tested |
| qwen_pop_I3_s5 | 7 | 9 | 1 | 0 | 22 | 11 | 1.0739 | 1.0745 | 3/3 | 8 | 5 | fit_decode; fit_field; fit_field_base; fit_mesg; fit_profile | TSan race only |
| qwen_bon_I3_s5 | 8 | 6 | 2 | 0 | 23 | 4 | 1.0713 | 1.0727 | 3/3 | 1 | 1 | fit_profile | TSan race only |
| ds_greedy_I2_s5 | 7 | 0 | 2 | 2 | 27 | 10 | 1.1666 | 1.1661 | 3/3 | 7 | 7 |  | TSan race only |
| ds_bon_I2_s5 | 8 | 1 | 4 | 0 | 27 | 5 | 1.0668 | 1.0667 | 3/3 | 1 | 1 | fit_profile | TSan race only |
| ds_pop_I3_s5 | 9 | 1 | 2 | 7 | 20 | 19 | 1.1697 | 1.1715 | 3/3 | 7 | 5 | fit_field; fit_field_base; fit_profile | TSan race only |
| ds_bon_I3_s5 | 4 | 1 | 3 | 4 | 27 | 11 | 1.0691 | 1.0685 | 3/3 | 1 | 1 | fit_profile | TSan race only |

“搜索中最佳确认”对所有运行用同一个定义:`results.jsonl` 中满足“两次测量都通过规则”的候选里最好的 speedup(取两次中较差的 ratio)。I2 的排序规则本身不产生这个值,所以这一列对 I2 是诊断值。**“独立复测 speedup”才是对外报告的值**(固定最终补丁,3 次测量的中位数)。“累计接受步数”:种群搜索 = 最终补丁谱系中 `improved_on_parent` 的步数;greedy = 记录更新次数;best-of-N = 1(单个函数的一次改写)。“扩展正确性”见 §7:`not tested` 表示该最终补丁没有做过扩展测试(I1 的 10 个补丁;DeepSeek greedy 种子 3 的 40 请求最终补丁,只测过它 38 请求时的状态)。

### 5.3 配置汇总(五个种子的中位数和完整范围)

| 配置 | 独立复测 speedup | 搜索中最佳确认 | total tokens | 搜索耗时 | 复测耗时(中位) | 课程指标 A:(搜索值−1)/tokens | 指标 B:(独立复测值−1)/tokens |
|---|---|---|---|---|---|---|---|
| Qwen 种群搜索 (I1) | 1.057 [1.027, 1.080] | 1.057 [1.026, 1.081] | 29,360 [28,552, 39,512] | 67 min [62, 102] | 4.9 min | 1.984e-06 | 1.984e-06 |
| Qwen best-of-N (I1) | 1.061 [1.038, 1.084] | 1.061 [1.037, 1.084] | 28,156 [26,356, 29,586] | 58 min [37, 61] | 6.0 min | 2.309e-06 | 2.325e-06 |
| Qwen 种群搜索 (I3, README 循环) | 1.074 [1.031, 1.124] | 1.074 [1.031, 1.123] | 34,230 [25,788, 36,748] | 50 min [37, 84] | 7.2 min | 2.159e-06 | 2.175e-06 |
| Qwen best-of-N (I3, 匹配对照) | 1.056 [1.039, 1.073] | 1.054 [1.040, 1.071] | 25,361 [24,454, 29,363] | 45 min [44, 54] | 7.0 min | 2.013e-06 | 2.083e-06 |
| DeepSeek greedy 单链 (I2) | 1.176 [1.157, 1.216] | 1.177 [1.156, 1.215] | 582,219 [361,233, 621,267] | 164 min [154, 180] | 6.2 min | 3.371e-07 | 3.400e-07 |
| DeepSeek best-of-N (I2, 排序规则) | 1.073 [1.067, 1.074] | 1.072 [1.067, 1.074] | 325,534 [272,154, 463,889] | 129 min [89, 142] | 6.2 min | 2.216e-07 | 2.228e-07 |
| DeepSeek 种群搜索 (I3, README 循环) | 1.165 [1.137, 1.181] | 1.163 [1.136, 1.183] | 366,952 [305,734, 421,966] | 191 min [182, 207] | 7.0 min | 4.504e-07 | 4.509e-07 |
| DeepSeek best-of-N (I3, 匹配对照) | 1.073 [1.069, 1.074] | 1.073 [1.069, 1.074] | 320,397 [266,927, 366,211] | 137 min [122, 151] | 7.0 min | 2.295e-07 | 2.283e-07 |

**课程指标(README):`(best_confirmed_speedup − 1) / total_tokens`,读取 `credits.csv` 最后一行。** A 列对 I1、I3 就是这个定义(`credits.csv` 最后一行的 `best_confirmed_speedup`);I2 的 `credits.csv` 没有该列,A 用搜索中的排序最优值代替。B 列把分子换成固定最终补丁的独立复测值,更稳,但**不是**课程规定的定义。分母 total tokens 包含截断回复和失败请求,不包含“无 usage”请求(消耗未知)。

**成本差距很大:** DeepSeek 每个运行的 total 约 27 万–62 万 token,其中 reasoning 占 completion 的绝大部分(各运行 96%–99%,中位数 97%);Qwen 约 2.4 万–4 万 token,没有 reasoning。所以 **Qwen 的课程指标比 DeepSeek 高一个数量级**(约 2×10⁻⁶ 对 2–4.5×10⁻⁷),尽管 DeepSeek 的绝对 speedup 更高。这是模型的成本结构差异,不能归因于搜索算法。

### 5.4 同一模型内的比较:搜索 vs 独立采样

四组比较,单位是**种子**(每个种子是一次独立搜索;同一补丁的三次复测不是三个种子)。检验:两侧各 5 个种子,**不配对**(同编号种子只是同一随机数流,结果并不成对);统计量 = 中位数之差,精确置换检验(C(10,5) = 252 种分组,双侧)和精确 Mann–Whitney 检验(双侧);**没有任何一个检验是预先登记的**,全部是探索性的;4 个主检验(独立复测 speedup)没有因多重比较调整,同时给出 Holm 校正后的 Mann–Whitney p。5 对 5 完全分离时精确 Mann–Whitney 的最小双侧 p = 2/252 = 0.0079。

| 比较(A 对 B,A = 搜索) | 量 | A 中位数 | B 中位数 | A 范围 | B 范围 | 置换 p | Mann–Whitney p | Holm 校正 MW p |
|---|---|---|---|---|---|---|---|---|
| Qwen,I1(种群搜索 对 best-of-N) | 独立复测 speedup(主要) | 1.0573 | 1.0613 | 1.0266..1.08041 | 1.03837..1.08427 | 0.7143 | 0.6905 | 0.690 |
| Qwen,I1(种群搜索 对 best-of-N) | total tokens | 29360 | 28156 | 28552..39512 | 26356..29586 | 0.1190 | 0.2222 |  |
| Qwen,I1(种群搜索 对 best-of-N) | 课程指标 B | 1.9843e-06 | 2.3248e-06 | 6.73106e-07..2.73782e-06 | 1.29687e-06..2.8717e-06 | 0.7143 | 0.5476 |  |
| Qwen,I3(README 循环 对 匹配 best-of-N) | 独立复测 speedup(主要) | 1.0745 | 1.056 | 1.03068..1.12375 | 1.03889..1.07272 | 0.2381 | 0.3095 | 0.619 |
| Qwen,I3(README 循环 对 匹配 best-of-N) | total tokens | 34230 | 25361 | 25788..36748 | 24454..29363 | 0.0476 | 0.0556 |  |
| Qwen,I3(README 循环 对 匹配 best-of-N) | 课程指标 B | 2.175e-06 | 2.0831e-06 | 1.07962e-06..4.79861e-06 | 1.54307e-06..2.86726e-06 | 0.7143 | 0.8413 |  |
| DeepSeek,I2(greedy 单链 对 best-of-N,排序规则) | 独立复测 speedup(主要) | 1.1758 | 1.0725 | 1.15737..1.21555 | 1.06669..1.07397 | 0.0476 | 0.0079 | 0.032 |
| DeepSeek,I2(greedy 单链 对 best-of-N,排序规则) | total tokens | 5.8222e+05 | 3.2553e+05 | 361233..621267 | 272154..463889 | 0.0476 | 0.0317 |  |
| DeepSeek,I2(greedy 单链 对 best-of-N,排序规则) | 课程指标 B | 3.4002e-07 | 2.2281e-07 | 2.53298e-07..4.86683e-07 | 1.43772e-07..2.68245e-07 | 0.0476 | 0.0159 |  |
| DeepSeek,I3(README 循环 对 匹配 best-of-N) | 独立复测 speedup(主要) | 1.1648 | 1.0732 | 1.13749..1.18107 | 1.06852..1.07366 | 0.0476 | 0.0079 | 0.032 |
| DeepSeek,I3(README 循环 对 匹配 best-of-N) | total tokens | 3.6695e+05 | 3.204e+05 | 305734..421966 | 266927..366211 | 0.2381 | 0.0952 |  |
| DeepSeek,I3(README 循环 对 匹配 best-of-N) | 课程指标 B | 4.5094e-07 | 2.2828e-07 | 3.25831e-07..5.39167e-07 | 1.87118e-07..2.74339e-07 | 0.0476 | 0.0079 |  |

**怎么解读(不选最小的 p 值,也不把“没发现显著差异”写成“相同”):**

- **DeepSeek(两个版本都是):搜索明显高于 best-of-N。** I3:1.1648 [1.1375, 1.1811] 对 1.0732 [1.0685, 1.0737];I2:greedy 1.1758 [1.1574, 1.2155] 对 best-of-N 1.0725 [1.0667, 1.0740]。两种比较都是 5 个种子完全分离(搜索的每个种子都高于 best-of-N 的每个种子),精确 Mann–Whitney p = 0.0079,Holm 校正后 0.032;置换检验因为并列值只能到 0.0476。
- **Qwen:两个版本都没有可靠差异。** I1:1.0573 对 1.0613(p = 0.69);I3:1.0745 对 1.0560(p = 0.31)。中位数的方向在两个版本里相反(I1 best-of-N 略高,I3 种群搜索略高),范围大幅重叠。**这不等于“种群搜索与 best-of-N 相同”**——5 个种子只够排除很大的差异。
- **DeepSeek 更高的原因没有被单独证明。** 种群/greedy 比 best-of-N 多了继承、性能反馈、(种群的)失败反馈和函数收益权重,这些因素是一起变化的;本实验没有做逐项消融,所以不能说哪一个起了作用。§6.3 的叠加实验说明继承(把多个函数的赢家叠起来)可以解释很大一部分差距,但不是全部证据。
- **跨模型的比较不能归因于算法:** 例如 DeepSeek 种群搜索 1.165 高于 Qwen 种群搜索 1.074,但两个模型的 token 量相差 10 倍以上、推理能力也不同。
- **同一模型不同代码版本的比较(I2 greedy 1.1758 与 I3 种群搜索 1.1648)只作描述:** 两者范围大幅重叠,而且两版在规则(排序 vs 确认)、反馈、预算、是否收益分支上都不同,没有做检验。

**成本差异:** 同一模型内,种群/greedy 比 best-of-N 多用 token:DeepSeek I3 366,952 对 320,397(置换 p = 0.24);I2 greedy 582,219 对 325,534(p = 0.048);Qwen I3 34,230 对 25,361(p = 0.048)。请求数相同(40),搜索耗时也更长(DeepSeek I3 约 191 分钟对 137 分钟,中位数)。课程指标 B 在 DeepSeek 上仍是搜索更高(I3:4.5×10⁻⁷ 对 2.3×10⁻⁷),在 Qwen 上两者相近(I3:2.17×10⁻⁶ 对 2.08×10⁻⁶,I1:1.98×10⁻⁶ 对 2.32×10⁻⁶)。

**需要同时说的限制:** 5 个种子;节点类别与种子没有平衡(I1/I2 的 xcnc 与 xcnd 混用);DeepSeek I2 的运行有 8 个作业同时访问同一个模型端点,约 9 个 greedy 请求遇到 HTTP 502;DeepSeek I3 有 48 个无 usage 请求(HTTP 502),其 token 消耗未知,总量因此偏低。


## 6. 速度提升主要来自哪些修改和机制?

### 6.1 哪些函数反复成为赢家,各自做了什么(重新阅读了实际补丁)

下表统计**最终补丁**里包含哪些函数的改动(种群搜索:谱系上的全部祖先,因为子补丁继承;greedy:全部被接受的步骤;best-of-N:单个函数)。每个配置 5 个最终补丁:

| 配置 | 最终补丁中最常出现的函数(出现次数/5) |
|---|---|
| Qwen 种群搜索 (I1) | Profile::GetMesg (4/5); Field::GetType (4/5); FieldBase::GetNumValues (2/5); FieldBase::FieldBase (2/5); AccumulatedField::AccumulatedField (1/5); IsAvgNegGradeValid (1/5) |
| Qwen best-of-N (I1) | Profile::GetMesg (4/5); FieldBase::FieldBase (1/5) |
| Qwen 种群搜索 (I3, README 循环) | Profile::GetMesg (4/5); FieldBase::FieldBase (3/5); Field::GetType (3/5); Mesg::GetField (2/5); Decode::Resume (2/5); Field::GetNum (2/5) |
| Qwen best-of-N (I3, 匹配对照) | Profile::GetMesg (5/5) |
| DeepSeek greedy 单链 (I2) | Profile::GetMesg (5/5); FieldBase::FieldBase (5/5); FieldBase::GetValue (4/5); Profile::GetFieldIndex (4/5); Mesg::GetField (3/5); Field::GetNum (2/5) |
| DeepSeek best-of-N (I2, 排序规则) | Profile::GetMesg (5/5) |
| DeepSeek 种群搜索 (I3, README 循环) | FieldBase::FieldBase (5/5); Profile::GetMesg (4/5); FieldBase::GetNumValues (3/5); Field::GetType (2/5); Field::GetNum (2/5); Profile::GetFieldIndex (2/5) |
| DeepSeek best-of-N (I3, 匹配对照) | Profile::GetMesg (5/5) |

**所有 DeepSeek 的 best-of-N 最终补丁(两个版本共 10 个)都只改 `Profile::GetMesg`**(speedup 1.067–1.074);Qwen 的 best-of-N 最终补丁 10 个里 9 个也是 `Profile::GetMesg`,另一个(I1 种子 2)是 `FieldBase::FieldBase`。`GetMesg` 是 profile 里最热的函数(约 19% 的样本),把线性扫描换成查表就是最容易找到的单点赢家。种群搜索和 greedy 的赢家集合更大:`Profile::GetMesg`、`FieldBase::FieldBase`(拷贝构造)、`Profile::GetFieldIndex`、`FieldBase::GetValue`、`Mesg::GetField`/`AddField` 等。

**常见优化各自减少了什么工作**(以 greedy 种子 3 链的实际补丁为例,逐个读了 diff;“消息”表示只读了补丁头部的说明):

| 函数 | 核对方式 | 减少了什么工作 | 搜索时单步收益 |
|---|---|---|---|
| `Profile::GetMesg` | 读 diff(0005、0011) | **查找**:线性扫描 124 项 → 65536 项表(或排序表)一次读取 | 最大的单步,约 6%(搜索时) |
| `Profile::GetFieldIndex` | 读 diff(0003) | **查找**:字段号线性扫描 → 位图+下标表缓存(缓存最近一个消息类型) | 搜索时约 1.5%;引入并发错误(见 §7) |
| `FieldBase::FieldBase`(拷贝构造) | 读 diff(0004) | **分配与复制**:原来先默认构造两个 `vector` 再赋值;现在在成员初始化列表里直接拷贝构造,省掉一次构造+一次赋值(字段在构造消息时被大量拷贝) | 搜索时约 4.4%(1 行改动) |
| `FieldBase::GetValue` | 读 diff(0010) | **逐字节拼装 → 一次 `memcpy`**(按 1/2/4/8 字节分支);假设小端机器 | 搜索时约 0.7% |
| `Mesg::AddField` | 读 diff(0008) | **函数调用**:内联扫描已有字段,省掉对 `GetField` 的调用与返回指针 | 搜索时约 1.4% |
| `CRC::Get16` | 读 diff(0007) | **查表次数减半**:16 项半字节表 → 256 项按字节的 constexpr 表 | 搜索时约 0.25% |
| `Decode::Resume` | 读 diff(0002) | **成员读写 → 局部变量**(可放寄存器),在跳出循环时才写回 | 搜索时约 0.4% |
| `Field::GetType`、`GetNumSubFields`、`MesgDefinition::GetFieldByIndex`、`MesgBroadcaster::RemoveListener` | 消息(0001、0006、0009、0012) | 改写形式或加分支提示,**几乎没有减少工作**;补丁说明自己也承认在噪声内(0.03%–0.16%) | 与 §3.4 的空搜索噪声同量级 |

所以收益的主要来源是**三类**:消灭线性查找(`GetMesg`、`GetFieldIndex`)、减少构造/拷贝(`FieldBase` 拷贝构造)、把逐字节循环换成宽访问(`GetValue`)。其余多为噪声级的小步。

### 6.2 一条有代表性的累计链(DeepSeek greedy,种子 3,中位数种子)

| 步骤 | 请求/代 | 函数 | 搜索时累计 speedup(记录) | 单步收益(相对上一个记录) | 是否独立复测 | 该步骤的扩展正确性(步骤 1–11 和第 12 步(旧最终状态)测过;第 13 步未测) |
|---|---|---|---|---|---|---|
| 1 | 6 | MesgBroadcaster::RemoveListener | 1.0010 | 0.10% | 否 | TSan 0 处;无并发不一致 |
| 2 | 11 | Decode::Resume | 1.0047 | 0.37% | 否 | TSan 0 处;无并发不一致 |
| 3 | 12 | Profile::GetFieldIndex | 1.0200 | 1.50% | 否 | TSan 3 处;4 线程下 36 次与单线程不一致 |
| 4 | 13 | FieldBase::FieldBase | 1.0673 | 4.43% | 否 | TSan 2 处;4 线程下 38 次与单线程不一致 |
| 5 | 17 | Profile::GetMesg | 1.1370 | 6.12% | 否 | TSan 3 处;4 线程运行未完成 |
| 6 | 18 | Field::GetType | 1.1373 | 0.03% | 否 | TSan 3 处;4 线程运行未完成 |
| 7 | 20 | CRC::Get16 | 1.1402 | 0.25% | 否 | TSan 3 处;4 线程运行未完成 |
| 8 | 21 | Mesg::AddField | 1.1561 | 1.38% | 否 | TSan 3 处;4 线程下 39 次与单线程不一致 |
| 9 | 28 | MesgDefinition::GetFieldByIndex | 1.1580 | 0.16% | 否 | TSan 3 处;4 线程下 39 次与单线程不一致 |
| 10 | 31 | FieldBase::GetValue | 1.1661 | 0.69% | 否 | TSan 2 处;4 线程下 38 次与单线程不一致 |
| 11 | 34 | Profile::GetMesg | 1.1675 | 0.12% | 否 | TSan 4 处;4 线程运行未完成 |
| 12 | 37 | Field::GetNumSubFields | 1.1683 | 0.06% | 否 | TSan 4 处;4 线程运行未完成(= 旧最终状态 final-greedy-seed3) |
| 13 | 39 | Mesg::GetField | 1.1766 | 0.71% | 是(仅最终补丁) |  |

**读这张表的规则:** (1) “搜索时累计 speedup”是**整个累计补丁**相对原库的 speedup(1/R),单步收益是记录的相对变化,**不能把各步百分比直接相加**,更不能把后面每一轮“继承了前面的收益”都算成一次新发现;(2) 只有最后一个数(1.1758,40 请求最终补丁的 3 次独立复测)是独立确认的;中间各步只有搜索时的两次测量;(3) 13 步里有 5 步(1、6、9、11、12)小于 0.2%,其中 2 步(6、12)不大于空搜索观察到的最大噪声单步 0.063%——它们在最终补丁里,但很可能没有贡献;(4) 步骤 3 引入 `GetFieldIndex` 缓存的那一步是**最早出现并发错误输出的补丁**(§7)。链上总共 40 个请求里只有 13 个被接受。

### 6.3 best-of-N 候选的组合

**做法(没有新的模型调用):** 取一个 DeepSeek best-of-N(I2)运行已经产生的全部候选;**每个函数**留搜索时 ratio 最低且 < 1 的那个候选;按搜索时 ratio 从好到坏排序;依次把前 K 个叠在一起(一个与已叠补丁冲突、不能干净应用的候选会被跳过并记录——5 个种子里只有种子 5 跳过 1 个);每个叠加状态用冻结的测量程序独立测 3 次(同时跑课程自带检查)。这 5 个种子共构造并测了 56 个叠加状态、168 次独立测量,**新增的模型调用为 0**。

| 种子 | 可用候选函数数 | best-of-N 最终(单函数) | 固定 K=2 | 固定 K=3 | 固定 K=5 | **事后**最佳 K | 最佳 K 的 speedup(事后选择) | 叠到最后一个候选 | 该种子 greedy(40 请求) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 11 | 1.0730 | 1.1304 | 1.1427 | 1.1421 | 9 | 1.1632 | 1.1557 | 1.1574 |
| 2 | 10 | 1.0688 | 1.1217 | 1.1358 | 1.1922 | 6 | 1.1977 | 1.1924 | 1.2155 |
| 3 | 13 | 1.0740 | 1.1272 | 1.1363 | 1.1464 | 10 | 1.1579 | 1.1574 | 1.1758 |
| 4 | 12 | 1.0725 | 1.1310 | 1.1499 | 1.1578 | 7 | 1.1870 | 1.1769 | 1.1919 |
| 5 | 12 | 1.0667 | 1.1167 | 1.1462 | 1.1880 | 6 | 1.2095 | 1.2093 | 1.1661 |
| 中位数 |  | 1.0725 | 1.1272 | 1.1427 | 1.1578 |  | 1.1870 | 1.1769 | 1.1758 |

**汇总:** K=2 的中位数 1.127,K=3 为 1.143,K=5 为 1.158(范围 [1.142, 1.192]);事后最佳 K 为 1.187(范围 [1.158, 1.210])。“填补了 greedy − best-of-N 差距的多大比例”(逐种子计算后取中位数):K=2 50%、K=3 65%、K=5 82%、事后最佳 K 96%。

**这个结果支持什么:** 把独立搜到的多个单函数赢家叠起来(没有失败反馈、没有种群、没有继承搜索),就能还原 greedy 与 best-of-N 之间**相当大一部分**差距(固定 K=5 约八成)。所以“greedy 更好”的很大一部分可以用**“保留并叠加多个函数的赢家”**解释。

**它不支持什么:** (1) 不证明差距的**全部**来自叠加:固定 K 的叠加仍低于 greedy 的中位数 1.176;事后最佳 K 看起来逼近甚至超过,但那是事后选择的最大值,有乐观偏差;(2) 不能分别证明**反馈、选择、继承**各自的贡献——没有逐项消融;(3) 叠加用的候选按搜索时 ratio 排序,而搜索时的 ratio 含噪声(§3.4),排序本身带选择偏差;(4) 叠加的候选与 greedy 链里的赢家来自同一批函数,二者并不独立;(5) 叠加补丁同样含有未同步的静态状态,见 §7:20 个叠加补丁的扩展正确性在 §7 总表中。


## 7. 这些修改仍然正确吗?

### 7.1 原来每轮检查已经做了什么,以及它与扩展测试的区别

**每一个进入测速的候选**都经过课程提供的 `CanMehBench` 检查(README 规定,在计时之前做):(1) 库能载入且六个入口符号都在;(2) **解码校验值**:4 个固定活动文件(907,007 字节、34,251 条消息、428,714 个字段)折出的 64 位校验值必须与原库相同,每个文件解码两次;(3) **profile 查询摘要**:三个 profile 查询函数对**每个消息号 0–65535、每个字段号 0–255**的回答折成摘要,必须与原库相同——所以查表类补丁的**查表本身**在整个定义域上被穷尽核对;(4) **threading**:一次解码的处理器时间若超过墙钟时间的 1.15 倍就拒绝(候选自己开线程会被发现)。这些检查都是**单线程**、**只用这 4 个文件**、**只比较输出摘要**。

**扩展正确性测试是附加的,不是搜索当时的准入规则,也不意味着搜索没有按课程要求做检查。** 它们补上课程检查没覆盖的几类问题:
| 测试 | 做法 | 补上的盲区 |
|---|---|---|
| 与原库的逐文件差分 | 同一个文件分别用原库和候选库解码,比较(返回状态、消息数、字段数、摘要) | 更多输入(其他合法文件、边界值)上输出是否仍相同 |
| ASan + UBSan(单线程) | 用 `-fsanitize=address,undefined -O1` 重编译被补丁改过的翻译单元,在文件子集上运行 | 越界读写、未定义行为 |
| TSan(4 线程) | 4 个线程**同时**解码同一批文件(冷启动:并发阶段在任何单线程解码之前),再逐线程与单线程参考摘要比较 | 并发调用下的数据竞争和错误输出 |
| 逐文件处理方式(plain,一个进程一个文件) | 每个文件单独起一个进程,记录:解码成功 / 抛异常(及文本) / 被信号杀死 | 候选在恶意输入上是否出现崩溃(原库抛异常的地方候选是否崩溃) |

### 7.2 测试语料和真实测试规模

|  | 组成 | 各测试的真实规模 |
|---|---|---|
| 语料 A(较早的对象:DeepSeek greedy/best-of-N 最终补丁、两个人工补丁、greedy 种子 3 的中间步骤) | 4 个标准文件 + 400 个**变异文件**(随机改字节、改定义区字节、截断;**重算了 CRC-16**,所以通过 CRC 检查,但内容不是合法 FIT 文件)= 404 个 | 差分 404 个文件(原库对其中 177 个不能解码,所以 227 个可比);ASan/UBSan 71 个文件;TSan 4 线程 × 12 个文件;不含 SDK 编码器写出的合法文件 |
| 语料 B(当前对象:I3 的 20 个最终补丁、20 个叠加补丁) | 语料 A + 55 个由 **SDK 自带编码器**写出的合法文件(原库对这 55 个全部成功解码)= 459 个 | 差分 459 个文件(282 个可比,含 4 个原始文件和 55 个合法文件);ASan/UBSan 126 个文件(4 原始 + 55 合法 + 每 6 个变异取 1 个);TSan 4 线程 × 24 个文件;逐文件处理方式 459 个 |

**CRC 正确不代表文件格式合法。** 变异文件的 CRC 是重新算的,头部和 CRC 都合法,但字段定义、基础类型、消息定义顺序被随机改动,违反 FIT 规范。它们只能说明“行为是否与原库相同”,而**不是**“正确输出是什么”。判断**解码合法文件时输出是否正确**,靠的是合法文件的差分(原库是行为参考,FIT 规范与 API 约定用来判断行为本身是否合理:合法文件必须解码出与原库相同的消息/字段值)。

### 7.3 原库自己对 177 个文件的处理:最终分类

语料 A 的 404 个文件里,原库解码成功 227 个,**177 个没有成功**。它们不是“SDK 崩溃”这一类,而是下面的分类(一个文件一个进程,原库 `-O1`):

| 原库的结局 | 文件数 |
|---|---|
| decoded | 227 |
| uncaught C++ exception: FIT decode error: Decoder not in correct state after last data byte in file. Check message definitions. (at byte N) | 91 |
| uncaught C++ exception: FIT decode error: Missing FIT message definition for local message number N. (at byte N) | 52 |
| uncaught C++ exception: FIT decode error: Architecture <byte> not supported. (at byte N) | 16 |
| uncaught C++ exception: FIT decode error: Invalid Field Size | 12 |
| uncaught C++ exception: Invalid developer field definition number in FieldDescriptionMesg | 4 |
| uncaught C++ exception: Invalid developer data index in FieldDescriptionMesg | 1 |
| killed by signal N | 1 |

- **176 个是 SDK 的**设计内**拒绝**:解码器遇到格式错误的流时抛出 C++ 异常(截断、缺失消息定义、不支持的字节序、非法字段长度、开发者字段错误),这是 API 约定的报错方式(在驱动里被捕获并记录,不当作崩溃);**没有**返回 `Decode::Read == false` 的文件。
- **1 个(文件 97,`defs` 类变异)被信号 11(段错误)杀死**:原库自己对畸形输入的内存错误,属于原库缺陷,不是候选引入。
- 此外原库对 **13 个**文件触发 ASan 报告、对 **28 个**文件触发 UBSan 报告(都出现在畸形输入上。对 55 个合法文件,原库没有 ASan 报告,但有 19 个文件触发 UBSan 消息——就是上面提到的 `fit_field_base.cpp` 对负数左移;4 个原始文件无报告)。

因此差分表里“两个库都崩溃/抛异常:177”这一列**不是候选的缺陷**,只表示这些文件原库本身就不成功,无法比较。

### 7.4 统一总表(每个已测对象一行)

列说明:“原始 4 / 合法 55 / 变异”给出 可比文件数/其中输出完全相同(合法文件仅语料 B 有);“只有候选崩溃”指原库抛异常或正常、候选崩溃的变异文件数;“ASan”是 ASan 错误数,“UBSan 新”是原库没有的 UBSan 消息数;“TSan 位置”是 4 线程运行报告的不同数据竞争位置数;“并发不一致”是 4 线程里与单线程参考摘要不同的次数/比较次数;“—”表示不适用或该运行没有完成。**没有测试的对象不归入通过。**

| 对象 | 语料 | 原始 4(相同/可比) | 合法 55(相同/可比) | 变异(相同/可比) | 只有候选崩溃 | ASan | UBSan 新 | TSan 位置 | 并发不一致 | 发现 |
|---|---|---|---|---|---|---|---|---|---|---|
| stock(原库) | A/B | — | — | — | — | 0 | 0(原库自带 1 条 UBSan) | 0 | — | 基线 |
| final-bestofn-seed1 | A | 4/4 | — | 223/223 | 0 | 0 | 0 | 2 | 0/48 | TSan race (2 locations) |
| final-bestofn-seed2 | A | 4/4 | — | 223/223 | 0 | 0 | 0 | 0 | 0/48 | 无发现 |
| final-bestofn-seed3 | A | 4/4 | — | 223/223 | 0 | 0 | 0 | 2 | 0/48 | TSan race (2 locations) |
| final-bestofn-seed4 | A | 4/4 | — | 223/223 | 0 | 0 | 0 | 2 | 0/48 | TSan race (2 locations) |
| final-bestofn-seed5 | A | 4/4 | — | 223/223 | 0 | 0 | 0 | 2 | 0/48 | TSan race (2 locations) |
| final-greedy-seed1 | A | 4/4 | — | 212/212 | 11 | 1 (运行中止) | 2 | 3 | 运行未完成 | crashes where stock does not on 11 mutant(s); ASan error; 2 new UBSan message(s); TSan race (3 locations); ASan run aborted; TSan run did not complete |
| final-greedy-seed2 | A | 4/4 | — | 223/223 | 0 | 0 | 0 | 1 | 0/48 | TSan race (1 locations) |
| final-greedy-seed3 | A | 4/4 | — | 223/223 | 0 | 0 | 0 | 4 | 运行未完成 | TSan race (4 locations); TSan run did not complete |
| final-greedy-seed4 | A | 4/4 | — | 219/223 | 0 | 0 | 0 | 2 | 0/48 | output differs on 4 mutant(s); TSan race (2 locations) |
| final-greedy-seed5 | A | 4/4 | — | 223/223 | 0 | 0 | 0 | 3 | 0/48 | TSan race (3 locations) |
| human-attempt-1 | A | 4/4 | — | 223/223 | 0 | 0 | 0 | 0 | 0/48 | 无发现 |
| human-attempt-2 | A | 4/4 | — | 223/223 | 0 | 0 | 0 | 0 | 0/48 | 无发现 |
| s3-step01-gen6 | A | 4/4 | — | 223/223 | 0 | 0 | 0 | 0 | 0/48 | 无发现 |
| s3-step02-gen11 | A | 4/4 | — | 223/223 | 0 | 0 | 0 | 0 | 0/48 | 无发现 |
| s3-step03-gen12 | A | 4/4 | — | 223/223 | 0 | 0 | 0 | 3 | 36/48 | TSan race (3 locations); 36 concurrent digest mismatch(es) |
| s3-step04-gen13 | A | 4/4 | — | 223/223 | 0 | 0 | 0 | 2 | 38/48 | TSan race (2 locations); 38 concurrent digest mismatch(es) |
| s3-step05-gen17 | A | 4/4 | — | 223/223 | 0 | 0 | 0 | 3 | 运行未完成 | TSan race (3 locations); TSan run did not complete |
| s3-step06-gen18 | A | 4/4 | — | 223/223 | 0 | 0 | 0 | 3 | 运行未完成 | TSan race (3 locations); TSan run did not complete |
| s3-step07-gen20 | A | 4/4 | — | 223/223 | 0 | 0 | 0 | 3 | 运行未完成 | TSan race (3 locations); TSan run did not complete |
| s3-step08-gen21 | A | 4/4 | — | 223/223 | 0 | 0 | 0 | 3 | 39/48 | TSan race (3 locations); 39 concurrent digest mismatch(es) |
| s3-step09-gen28 | A | 4/4 | — | 223/223 | 0 | 0 | 0 | 3 | 39/48 | TSan race (3 locations); 39 concurrent digest mismatch(es) |
| s3-step10-gen31 | A | 4/4 | — | 223/223 | 0 | 0 | 0 | 2 | 38/48 | TSan race (2 locations); 38 concurrent digest mismatch(es) |
| s3-step11-gen34 | A | 4/4 | — | 223/223 | 0 | 0 | 0 | 4 | 运行未完成 | TSan race (4 locations); TSan run did not complete |
| r2-ds-bestofn-s1 | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 2 | 0/96 | TSan race (2 locations) |
| r2-ds-bestofn-s2 | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 2 | 0/96 | TSan race (2 locations) |
| r2-ds-bestofn-s3 | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 2 | 0/96 | TSan race (2 locations) |
| r2-ds-bestofn-s4 | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 2 | 0/96 | TSan race (2 locations) |
| r2-ds-bestofn-s5 | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 2 | 0/96 | TSan race (2 locations) |
| r2-ds-population-s1 | B | 4/4 | 55/55 | 212/212 | 11 | 1 (运行中止) | 2 | 4 | 运行未完成 | crashes where stock does not on 11 mutant(s); ASan error; 2 new UBSan message(s); TSan race (4 locations); ASan run aborted; TSan run did not complete |
| r2-ds-population-s2 | B | 4/4 | 54/55 | 223/223 | 0 | 0 | 0 | 2 | 0/96 | output differs on 1 legal encoder file(s); TSan race (2 locations) |
| r2-ds-population-s3 | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 2 | 0/96 | TSan race (2 locations) |
| r2-ds-population-s4 | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 2 | 0/96 | TSan race (2 locations) |
| r2-ds-population-s5 | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 2 | 0/96 | TSan race (2 locations) |
| r2-qwen-bestofn-s1 | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 0 | 0/96 | 无发现 |
| r2-qwen-bestofn-s2 | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 1 | 0/96 | TSan race (1 locations) |
| r2-qwen-bestofn-s3 | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 1 | 0/96 | TSan race (1 locations) |
| r2-qwen-bestofn-s4 | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 0 | 0/96 | 无发现 |
| r2-qwen-bestofn-s5 | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 1 | 0/96 | TSan race (1 locations) |
| r2-qwen-population-s1 | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 0 | 0/96 | 无发现 |
| r2-qwen-population-s2 | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 0 | 0/96 | 无发现 |
| r2-qwen-population-s3 | B | 4/4 | 10/55 | 223/223 | 0 | 0 | 0 | 3 | 运行未完成 | output differs on 45 legal encoder file(s); TSan race (3 locations); TSan run did not complete |
| r2-qwen-population-s4 | B | 4/4 | 51/55 | 223/223 | 0 | 0 | 0 | 0 | 0/96 | output differs on 4 legal encoder file(s) |
| r2-qwen-population-s5 | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 2 | 0/96 | TSan race (2 locations) |
| stack-s1-K2-fixed | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 2 | 0/96 | TSan race (2 locations) |
| stack-s1-K3-fixed | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 3 | 2/96 | TSan race (3 locations); 2 concurrent digest mismatch(es) |
| stack-s1-K5-fixed | B | 4/4 | 55/55 | 212/212 | 11 | 1 (运行中止) | 2 | 4 | 运行未完成 | crashes where stock does not on 11 mutant(s); ASan error; 2 new UBSan message(s); TSan race (4 locations); ASan run aborted; TSan run did not complete |
| stack-s1-bestK9-posthoc | B | 4/4 | 55/55 | 212/212 | 11 | 1 (运行中止) | 2 | 4 | 运行未完成 | crashes where stock does not on 11 mutant(s); ASan error; 2 new UBSan message(s); TSan race (4 locations); ASan run aborted; TSan run did not complete |
| stack-s2-K2-fixed | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 0 | 0/96 | 无发现 |
| stack-s2-K3-fixed | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 4 | 运行未完成 | TSan race (4 locations); TSan run did not complete |
| stack-s2-K5-fixed | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 3 | 运行未完成 | TSan race (3 locations); TSan run did not complete |
| stack-s2-bestK6-posthoc | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 4 | 运行未完成 | TSan race (4 locations); TSan run did not complete |
| stack-s3-K2-fixed | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 2 | 0/96 | TSan race (2 locations) |
| stack-s3-K3-fixed | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 2 | 0/96 | TSan race (2 locations) |
| stack-s3-K5-fixed | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 2 | 0/96 | TSan race (2 locations) |
| stack-s3-bestK10-posthoc | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 2 | 0/96 | TSan race (2 locations) |
| stack-s4-K2-fixed | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 2 | 0/96 | TSan race (2 locations) |
| stack-s4-K3-fixed | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 3 | 3/96 | TSan race (3 locations); 3 concurrent digest mismatch(es) |
| stack-s4-K5-fixed | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 3 | 5/96 | TSan race (3 locations); 5 concurrent digest mismatch(es) |
| stack-s4-bestK7-posthoc | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 3 | 8/96 | TSan race (3 locations); 8 concurrent digest mismatch(es) |
| stack-s5-K2-fixed | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 2 | 0/96 | TSan race (2 locations) |
| stack-s5-K3-fixed | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 3 | 0/96 | TSan race (3 locations) |
| stack-s5-K5-fixed | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 3 | 3/96 | TSan race (3 locations); 3 concurrent digest mismatch(es) |
| stack-s5-bestK6-posthoc | B | 4/4 | 55/55 | 223/223 | 0 | 0 | 0 | 3 | 2/96 | TSan race (3 locations); 2 concurrent digest mismatch(es) |
| stock (SDK 21.201.0) | reference |  |  |  |  |  |  |  |  |  |
| qwen3-coder-next search seed 1 final patch (original implementation I1) | 未测试 |  |  |  |  |  |  |  |  |  |
| qwen3-coder-next bestofn seed 1 final patch (original implementation I1) | 未测试 |  |  |  |  |  |  |  |  |  |
| qwen3-coder-next search seed 2 final patch (original implementation I1) | 未测试 |  |  |  |  |  |  |  |  |  |
| qwen3-coder-next bestofn seed 2 final patch (original implementation I1) | 未测试 |  |  |  |  |  |  |  |  |  |
| qwen3-coder-next search seed 3 final patch (original implementation I1) | 未测试 |  |  |  |  |  |  |  |  |  |
| qwen3-coder-next bestofn seed 3 final patch (original implementation I1) | 未测试 |  |  |  |  |  |  |  |  |  |
| qwen3-coder-next search seed 4 final patch (original implementation I1) | 未测试 |  |  |  |  |  |  |  |  |  |
| qwen3-coder-next bestofn seed 4 final patch (original implementation I1) | 未测试 |  |  |  |  |  |  |  |  |  |
| qwen3-coder-next search seed 5 final patch (original implementation I1) | 未测试 |  |  |  |  |  |  |  |  |  |
| qwen3-coder-next bestofn seed 5 final patch (original implementation I1) | 未测试 |  |  |  |  |  |  |  |  |  |
| ds_greedy_I2 seed 3 final patch at 40 requests (generation 39) | NOT TESTED (the tested 'final-greedy-seed3' is the 38-request state, generation 37) |  |  |  |  |  |  |  |  |  |

(完整列在 `tables/correctness_unified.csv`;图 `fig7_correctness_matrix` 是同一内容的矩阵。)

### 7.5 对各项问题的核实

**① “无新增问题”与“完全没有告警”不是一回事。** 对 ASan/UBSan,表中数字是“**原库没有的**”消息数;原库自己有 1 条 UBSan 消息(`fit_field_base.cpp`:对负数左移),在 **46 个已完成的候选运行里同样出现**,在 13 个运行里消失(这些补丁重写了那段代码),另有 4 个运行因出错中止而无法判断。对 TSan,原库 4 线程运行**零**报告,所以任何报告都是新的。

**② 只有竞争告警 vs 实际出现输出错误或崩溃。**

| 类别 | 对象与证据 |
|---|---|
| 仅 TSan 竞争告警,没观察到错误输出 | DeepSeek I3 的 best-of-N 5 个、种群 3 个(s3、s4、s5);I2 的 best-of-N 4 个(种子 1、3、4、5)、greedy 种子 2 和 5;Qwen I3 的 best-of-N 3 个(s2、s3、s5)、种群 s5;叠加 K=2/K=3/K=5 中的大多数。竞争的位置在 `fit_profile.cpp` 的 `GetMesg`(手写的 `static bool initialized` 惰性建表) |
| 4 线程下输出与单线程不一致(并发错误输出) | greedy 种子 3 链的步骤 3、4、8、9、10(每个 36–39/48 次比较);叠加 s1-K3、s4-K3/K5/bestK、s5-K5/bestK(2–8 次);greedy 链里的不一致与 `GetFieldIndex` 共享缓存的出现吻合(见 ④);叠加补丁里不一致的具体原因没有逐个核对 |
| 在合法文件上输出与原库不同 | **Qwen I3 种群搜索种子 3:55 个合法文件里只有 10 个相同(45 个不同)**;Qwen I3 种群种子 4:4 个不同;DeepSeek I3 种群种子 2:1 个不同。原始 4 个文件在所有补丁上都相同 |
| 只在变异文件上不同 | greedy 种子 4(I2):4 个 `data` 变异文件的输出不同 |
| 候选崩溃而原库不崩溃 | greedy 种子 1(I2)、DeepSeek I3 种群种子 1、叠加 s1-K5 与 s1-bestK9:在 11 个 `defs` 变异文件上只有候选崩溃(差分);语料 B 的逐文件运行里,这三个对象(DeepSeek I3 种群种子 1、叠加 s1-K5、s1-bestK9)各有 21 个文件被信号杀死(SIGFPE 12 个、SIGSEGV 9 个),均为 `defs` 变异文件,原库对其中多数抛异常、对个别(如文件 0048)正常解码;ASan 报告 1 个越界读 |

**③ 越界出现在哪类文件。** ASan/UBSan 的越界读报告(`fit_decode.cpp:819`,`baseTypeSizes[baseType]`,下标 31、数组只有 17 项)出现在 **`defs` 类变异文件**(定义区被改坏的文件)上,代码是**原库自己的 `Decode::ReadByte`**——它在校验 `baseType < FIT_BASE_TYPES` 之前就先读数组。原库在同一批 ASan 文件上没有这条报告;为什么原库没走到这里**没有查明**。另有文件(如 0048)原库正常解码、候选却收到 SIGFPE(整数除零),具体位置也没有定位。**4 个原始文件和 55 个合法文件**在这些补丁上的输出与原库完全相同(差分与逐文件运行都一致),没有出现越界。注意:这几个运行的 ASan 运行在第一个错误处中止,所以该运行里排在后面的文件没有被 ASan 检查(表中标“运行中止”)。

**④ 最早引入缺陷的补丁及已确认的原因。** 逐步测过的只有 greedy 种子 3 链(语料 A):步骤 1–2(`RemoveListener`、`Decode::Resume`)在 TSan 下**零**告警、4 线程输出与单线程一致;**步骤 3(请求 12,`Profile::GetFieldIndex`)是最早出现问题的补丁**:TSan 位置 0 → 3,4 线程输出与单线程不一致 36/48 次;此后各步骤(能完成的)都保持 36–39/48 的不一致。**原因(代码阅读确认):**步骤 3 的补丁新增 `static const MESG *cachedMesg`、`static FIT_UINT16 cachedFieldIndex[256]`、`static FIT_UINT32 cachedFieldMask[8]`——函数每次被另一个消息类型调用时就改写这些共享变量,多线程交替查询不同消息类型时会读到别的消息类型的缓存,返回错误的字段下标。(没有把缓存改成加锁版本重新跑来反证,所以这是由“0→36 出现的位置恰是这个补丁”加代码机理得到的确认,不是干预实验。)对**其它**问题类别(合法文件差异、越界/崩溃),只测了最终补丁,没有逐步测试,**最早引入点和具体原因没有隔离,不能给出已确认的原因**。

**⑤ 哪些结论针对哪组候选(“唯一干净”)。** 早先“人工补丁和 best-of-N 种子 2 是干净的”的说法**不准确**:更完整的对象集里,在各自测试条件下**没有任何发现**的是——人工补丁 1、2(语料 A);I2 best-of-N 种子 2(语料 A);greedy 种子 3 链的步骤 1、2(语料 A);Qwen I3 best-of-N 种子 1、4;Qwen I3 种群搜索种子 1、2;叠加 s2-K2(语料 B)。其中:
- 语料 A 与 B 的测试规模不同(TSan 12 对 24 个文件、ASan 71 对 126 个文件、A 没有合法文件),二者的“无发现”不是同一强度。
- **TSan 只会报告测试里实际发生的竞争。**对补丁加法的静态阅读(`tables/concurrency_patterns_by_patch.csv`)显示:Qwen I3 best-of-N 种子 1 的补丁含手写的 `static bool initialized` 惰性建表(与被 TSan 报告的补丁同一种写法),TSan 却没有报告——它是一次**漏报**,不能算安全。
- 没有发现不等于正确:语料只有 459 个文件,TSan 只跑了 24 个文件。
- 真正“由构造保证线程安全”的写法只有:函数内 `static const` 局部对象或 lambda 初始化的静态变量(C++11 保证一次性线程安全初始化)——两个人工补丁、I2 best-of-N 种子 2、Qwen I3 best-of-N 种子 4 和种群种子 1、2 就是这样写的;Qwen I3 种群种子 4 没有静态状态,但它在 4 个合法文件上输出不同。

### 7.6 每个配置的最终补丁处于什么状态

| 配置(每个 5 个最终补丁) | 无发现 | 仅 TSan 竞争 | 仅变异文件输出不同 | 错误输出/崩溃/内存错误 | 未测试 | 代码阅读:含未同步共享状态 | 代码阅读:无/线程安全 |
|---|---|---|---|---|---|---|---|
| Qwen 种群搜索 (I1) | 0 | 0 | 0 | 0 | 5 | 2 | 3 |
| Qwen best-of-N (I1) | 0 | 0 | 0 | 0 | 5 | 4 | 1 |
| Qwen 种群搜索 (I3, README 循环) | 2 | 1 | 0 | 2 | 0 | 2 | 3 |
| Qwen best-of-N (I3, 匹配对照) | 2 | 3 | 0 | 0 | 0 | 4 | 1 |
| DeepSeek greedy 单链 (I2) | 0 | 2 | 1 | 1 | 1 | 5 |  |
| DeepSeek best-of-N (I2, 排序规则) | 1 | 4 | 0 | 0 | 0 | 4 | 1 |
| DeepSeek 种群搜索 (I3, README 循环) | 0 | 3 | 0 | 2 | 0 | 5 |  |
| DeepSeek best-of-N (I3, 匹配对照) | 0 | 5 | 0 | 0 | 0 | 5 |  |

“错误输出/崩溃/内存错误”包括:合法文件输出不同、4 线程下输出不一致、候选独有崩溃、ASan 错误。I1(Qwen 原始实现)的 10 个最终补丁**没有做过任何扩展测试**;“代码阅读”列只是静态阅读,对 I1 的读数没有逐个人工核对。

**性能数字与正确性状态并列。** 本文件所有 speedup 都是相应基准条件下的测量(4 个固定文件、单线程、`-O2`、同一节点对内的 ratio)。§5.2 逐种子表在每个最终补丁的 speedup 旁给出了扩展正确性状态,图 `fig1_seed_results_with_correctness` 把状态画在每个点上。

## 8. 局限、缺失与未验证

### 8.1 与旧汇总不一致的地方,以及本文件采用的定义

| 项目 | 旧汇总的说法 | 本文件的做法 |
|---|---|---|
| greedy 链的记录更新次数 | 早先的空搜索对比文字写 50 次 | 本文件按 5 个 greedy 运行在 **40 个请求时**的 `rank_updates` 统计,共 51 次(种子 3 在续跑中又多了第 13 步,请求 39)。 |
| DeepSeek greedy 的中位数 | 最初的 Phase 1 统计(3 个种子在 38/34/34 个请求处停止)是 1.1687 | 本文件用 40 个请求的最终状态(种子 1、3、4、5 经续跑补足):1.1758。种子 3 的最终补丁因此多了一步。 |
| “确认”的 speedup | Phase 1 把 `best_confirmed_speedup` 定义为 3 次独立复测的中位数;I3 的 `credits.csv` 最后一行是**搜索时**的确认值 | 两者都给出:“独立复测”(主要,本文件所有比较用它)和“搜索中最佳确认”(例如 DeepSeek I3 种群 1.1648 对 1.1634)。课程指标 A 用后者、B 用前者。 |
| 置换检验的 p | 早先写 0.0476 | 5 对 5 完全分离时,中位数之差的置换 p 因并列值只能到 0.0476;精确 Mann–Whitney 为 0.0079(2/252)。本文件两个都给,不挑小的。 |
| “唯一干净”的补丁 | 早先说人工补丁和 best-of-N 种子 2“干净” | 更完整的对象集和代码阅读后改为 §7.5 ⑤:没有发现的补丁不止这几个,且其中含 TSan 漏报;“没有发现”只针对各自的测试条件。 |
| 正确性测试对象 | greedy 种子 3 的“final-greedy-seed3” | 测过的是 38 个请求时的状态(请求 37),不是 40 个请求的最终补丁(请求 39);表中标出未测。 |

- **样本数:** 每个配置 5 个种子;大部分比较的 p 值是探索性的;5 个种子只能分辨大差异(DeepSeek 搜索 vs best-of-N),不能确认小差异(Qwen)。
- **节点与批次:** 校准只在 xcnc2;C1/C2 只在 xcnd24 且各 5 次测量;I1/I2 的节点类别与种子不平衡;xcnc 与 xcnd 的基线耗时相差约 33%(358 对 480 ms),ratio 理论上抵消,但没有逐类验证加速比是否一致。
- **端点并发:** I2 的 DeepSeek 运行有 8 个作业同时访问同一端点(违反“最多 4 个”的建议),I3 保持 4 个;约 58 个 DeepSeek 请求返回 HTTP 502 且无 usage,token 消耗未知(不是 0)。
- **I1 的请求数:** 老 Qwen 运行记录的是“40 次模型调用”,提供的客户端可能在其中隐藏了重试,HTTP 请求数不可核实。
- **人工对照:** 没有计时记录;AI 辅助。
- **正确性覆盖:** 语料 459 个文件、TSan 24 个文件;I1 的 10 个补丁、greedy 种子 3 的 40 请求最终补丁、人工补丁在合法文件上的差分**未测试**;越界/崩溃和合法文件差异的**具体原因没有隔离**;没有把任何问题补丁修好后重测。
- **组合实验:** 叠加的是 I2 best-of-N 的候选,没有用 I3 的候选重做;没有对反馈、选择、继承做逐项消融。
- **同一种子编号共享随机数流:** 不同配置的函数抽取序列相关(见 §2.3);检验按“不配对的独立种子”处理,这一假设对 best-of-N 配置之间只是近似。
- **C2 一小时计时:** 缺失,无法补成已完成。

