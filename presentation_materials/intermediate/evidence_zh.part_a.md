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
