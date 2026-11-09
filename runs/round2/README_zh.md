# 第二轮实验说明(已完成)

本目录是第二轮的**新实验**。已提交的 `d5aa9e7`、原始报告、日志和补丁没有被改动(分支 `round2`)。原始数字表在 `RESULTS.md`、`results.json`,逐个运行的可追溯表在 `TRACEABILITY.md`,要求核对表在 `docs/round2/requirements_audit.md`。

## 一、这轮回答什么问题
1. README 把种群、性能采样、`null_ok`、`--out` 下的文件写成对 `CanMehSearch` 的**要求**。第一轮的 DeepSeek "greedy"(种群为 1,不反馈失败)因此不是 README 的搜索循环。这轮按 README 实现种群搜索,并和**同模型、同提示、同参数、每次从原库出发、没有历史和反馈**的 best-of-N 在**相同的 40 次实际 HTTP 请求**下比较。
2. 冻结的统计规则(repeat 10、repetitions 9、α=0.01、相对 stock 至少快 2%)的误报率有多高。
3. 最终补丁在更严格的正确性检查下是否仍然正确。

## 二、做了什么
| 内容 | 位置 |
|---|---|
| 20 个正式运行:DeepSeek、Qwen 各 {种群搜索, 匹配的 best-of-N} × 5 个种子,每个 40 次实际 HTTP 请求(全部 20 个都达到 40,预算停在恰好 40) | `runs/round2/runs/<模型>-<population\|bestofn>-s<种子>/` |
| 每个运行的最终补丁固定后,单独作业再测 3 次 | `runs/round2/runs/*/final/evaluate-best/` |
| 误报率:合成 null 500 次有效试验;真实 SDK 空补丁 xcnc、xcnd 各 402 次 | `runs/round2/fpr/` |
| 空操作候选的机器码核查(17 个候选库) | `runs/round2/fpr/noop-verification-*` |
| 扩展正确性检查:合法 FIT 文件(SDK 编码器写出)、变异文件、与 stock 的逐文件差分、ASan/UBSan、TSan | `runs/round2/correctness/` |

## 三、发现了什么(五个种子的中位数,范围写在方括号里;各模型分开,不混合)
| 配置 | 搜索中的 best_confirmed(credits.csv) | 最终补丁独立复测 | 总 token(中位数) |
|---|---|---|---|
| DeepSeek 种群搜索 | **1.163** [1.136, 1.183] | 1.165 [1.137, 1.181] | 3.67e5 |
| DeepSeek best-of-N | **1.073** [1.069, 1.074] | 1.073 [1.069, 1.074] | 3.20e5 |
| Qwen 种群搜索 | **1.074** [1.031, 1.123] | 1.074 [1.031, 1.124] | 3.4e4 |
| Qwen best-of-N | **1.054** [1.040, 1.071] | 1.056 [1.039, 1.073] | 2.5e4 |

- **DeepSeek 上种群搜索明显好于 best-of-N**:两组范围不重叠(1.136–1.183 对 1.069–1.074)。探索性精确置换检验 p = 0.048(n=5 对 5,事前选定但不是预先登记的主检验)。
- **Qwen 上两者无法区分**(p = 0.24);种群搜索的中位数略高,但范围大幅重叠。
- 搜索时的确认结果能被独立复测重复:20 个最终补丁的复测和搜索值相差在 0.3% 以内,19 个 3/3 通过,只有 Qwen best-of-N s4 为 2/3。
- DeepSeek 的 best-of-N 五个种子几乎相同(1.069–1.074),种群搜索则是沿着父代累积子补丁走到 1.14–1.18。我没有逐个核对这些补丁改了什么,所以不能说各个 best-of-N 种子是否找到了同一个改动。
- DeepSeek 种群搜索的 token 中位数比 best-of-N 多约 15%(3.67e5 对 3.20e5);原因(失败反馈、更长的提示)没有单独验证。

### 误报率(冻结规则:ratio ≤ 0.98、符号翻转 p < 0.01、非 unstable)
| 测量 | 有效试验 | 误接受 | 95% 上界 |
|---|---|---|---|
| 合成 null(全部) | 500 | 0 | 0.74% |
| 合成 null,xcnc / xcnd | 300 / 200 | 0 / 0 | 1.22% / 1.83% |
| 真实 SDK 空补丁,xcnc | 402 | 0 | 0.91% |
| 真实 SDK 空补丁,xcnd | 402 | 0 | 0.91% |

来源:合成 null 的 500 次 = 第 0 阶段的 100 次(xcnc)+ 本轮新增 400 次(xcnc、xcnd 各 200 次);SDK 空补丁的每类 402 次 = 上一轮 120 次 + 本轮新增 282 次。

空补丁的 ratio 中位数 0.99997(xcnc)、0.99989(xcnd),范围 [0.9971, 1.0024],没有 unstable。17 个空操作候选的 `.text` 与 stock 逐字节相同,动态符号也相同,所以这些 null 对确实没有可优化的东西。

### 正确性(这是最需要注意的部分)
检查对象:20 个最终补丁,以及上一轮 best-of-N 叠加的 20 个补丁(K=2、3、5 固定,以及事后选的最佳 K)。语料 459 个文件:55 个由 SDK 编码器写出的**合法**文件、4 个原始文件、400 个变异文件(变异文件不是合法输入,stock 本身对其中 177 个抛异常或崩溃)。

- **best-of-N 的 10 个最终补丁**:合法文件全部与 stock 一致,变异文件无新增崩溃,无 ASan/UBSan 新告警。
- **种群搜索的 10 个最终补丁里有 4 个有问题**:
  - `qwen-population-s3`(复测 1.083,是 Qwen 种群里第二高):55 个合法文件里只有 10 个与 stock 输出一致,**45 个合法文件的解码结果被改变**。
  - `qwen-population-s4`:4 个合法文件输出不同。`ds-population-s2`:1 个合法文件输出不同。
  - `ds-population-s1`:在 21 个变异文件上被信号杀死(12 个 SIGFPE、9 个 SIGSEGV),而 stock 对这些文件抛的是普通异常;ASan 在其中一个文件上报告越界读。合法文件全部一致。
  - 这些补丁都通过了冻结的统计规则和搜索自带的输出摘要检查。**说明这些检查没有覆盖这类错误**。
  - 剩下的种群补丁(`ds-population-s3/s4/s5`,`qwen-population-s1/s2/s5`)在差分和 ASan/UBSan 下都没有发现问题。排除上面 DeepSeek 的 s1、s2 后,DeepSeek 种群剩下三个的中位数是 1.170。
- **TSan(4 线程)**:stock 无告警。20 个最终补丁里 16 个出现告警,位置集中在 `fit_profile.cpp` 的 `GetMesg`(补丁共享了一个惰性建立的查找结构)。这 16 个里有 14 个没有观察到输出摘要不一致(另外 2 个因崩溃没有输出)。上一轮的叠加补丁里 6 个出现并发摘要不一致(最多 8 次)。告警数量不是严重程度。
- 上一轮的叠加(stack)不是从这轮的 best-of-N 候选构造的;这轮没有重新叠加。

## 四、不能说明什么
- **只有 5 个种子、2 个模型、一个服务端点**。DeepSeek 的差异方向一致,但 p=0.048 只是探索性的,不是预先登记的检验。
- **合成 null 本轮新增 400 次(每类 200 次),加第 0 阶段的 100 次才到 500;xcnd 一类只有 200 次**,没有达到每类 400 次的目标。xcnd 的 95% 上界因此是 1.83%,不是 0.9%。如果要求每类 400 次,xcnd 还要补 200 次。
- 0 次误接受说明误报率的**上界**约 0.7–0.9%,不是它等于 0。
- 速度提升是在这套 FIT 解码工作负载、这些节点(E5-2620 v3)上测的,不保证迁移到其他输入或机器。
- 正确性检查是附加验证,不是搜索当时的准入规则;变异文件不是合法输入,所以变异文件上的差异只表示行为不同,不一定是缺陷。合法文件上的差异才是正确性问题。
- 没有发现错误不等于正确:语料只有 459 个文件,TSan 只跑了 24 个文件、4 个线程。
- 旧的 Qwen 运行(`runs/main`)保持原样,作为单独的历史数据,不与这轮混合。旧运行满足 README 的搜索设计,但无法证明"40 次实际 HTTP 请求"(提供的客户端会在内部重试)。
- C2 人工控制的原始一小时计时缺失,无法补成已完成。
- 这轮没有碰报告、PPT 和幻灯片。
- 模型访问作业按要求最多 4 个(4 条任务链);你要求所有节点并行,纯测量作业确实并行了,但模型作业仍限制在 4 个。

## 五、协议要点(提交 527c5d0 起冻结)
- 协议:`runs/round2/protocol.json`;任务链:`runs/round2/chains/`;提交记录:`runs/round2/chains/SUBMISSION.txt`。
- 同一对照内模型、提示模板、temperature、max_tokens 一致;best-of-N 每次从 stock 出发,不接收历史、成绩或失败反馈。
- 预算统计所有实际发出的 HTTP 请求(含 502、截断、失败反馈重试);调用前的失败(选区、show、splice)只记录,不算请求。`qwen-population-s1` 有 56 行记录,其中 16 行是不发请求的步骤。
- 每个运行可能分成多段(Slurm 时限 9300 s),每段结束保存检查点,续跑不重放已计费请求;跨节点时重新测量种群成绩。DeepSeek 的 5 个种群搜索运行都分成了 2 段,其余 15 个运行 1 段。
- 所有 xcnc、xcnd 节点按你的指示视为等价;每段的真实节点和 CPU 都有记录。

## 六、复现命令
```bash
# 重新生成汇总(原始数字表、可追溯表)
python3 scripts/round2/aggregate_round2.py      # -> runs/round2/RESULTS.md, results.json
python3 scripts/round2/traceability.py          # -> runs/round2/TRACEABILITY.md
# 正确性(在计算节点上;每个约 50 分钟、50 分钟、90 分钟)
sbatch --export=ALL,PART=DIFF0 scripts/round2/correctness_round2.sbatch
sbatch --export=ALL,PART=DIFF1 scripts/round2/correctness_round2.sbatch
sbatch --export=ALL,PART=SAN   scripts/round2/correctness_round2.sbatch
sbatch --export=ALL,PART=SAN,CONFIGS=plain scripts/round2/correctness_round2.sbatch   # 只重做逐文件处理方式比较
# 误报率
sbatch scripts/round2/null_trials.sbatch ; sbatch scripts/round2/sdk_inert_fpr.sbatch
```
