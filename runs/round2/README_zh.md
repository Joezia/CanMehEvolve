# 第二轮实验说明(进行中)

本目录是第二轮的**新实验**,已提交的 `d5aa9e7`、原始报告、日志和补丁没有被改动(分支 `round2`)。要求核对表在 `docs/round2/requirements_audit.md`。

## 为什么做第二轮
README 把种群、性能采样、`null_ok` 检查写成了对 `CanMehSearch` 的**要求**,不是参考设计。第一轮的 DeepSeek "greedy"(种群为 1、不反馈失败)和排序规则下的 best-of-N 因此不符合 README 的搜索循环。第二轮按 README 的描述重新实现并运行。

## 这轮做了什么
| 内容 | 位置 | 回答的问题 |
|---|---|---|
| 20 个正式运行:DeepSeek 与 Qwen 各 {种群搜索, 匹配的 best-of-N} × 5 个种子,每个 40 次实际 HTTP 请求 | `runs/round2/runs/<模型>-<population\|bestofn>-s<种子>/` | 符合 README 的种群搜索是否比同预算、同模型、同提示、每次从原库出发的 best-of-N 好,各模型分别看 |
| 每个运行结束后固定最终补丁,单独作业再测 3 次 | `runs/round2/runs/*/final/` | 搜索时的确认结果能否被独立复测重复 |
| 合成 null 对补测到至少 400 次有效试验;真实 SDK 无效补丁在 xcnc、xcnd 各至少 400 次 | `runs/round2/fpr/` | 冻结规则的误报率(0 次误报时 95% 上界约 0.92%)。不同节点类别和合成与真实 SDK 分开报告 |
| 空搜索的"无效改动"机器码核查 | `runs/round2/fpr/noop-verification-*` | 这些候选的 .text 是否与原库逐字节相同,即真的没有可优化的东西 |
| 扩展正确性检查(合法 FIT 文件、失败分类、ASan/UBSan、TSan) | `runs/round2/correctness/` | 新的最终补丁和 best-of-N 叠加补丁在更严格条件下是否正确 |

## 汇总
全部结束后会自动生成 `runs/round2/RESULTS.md` 和 `results.json`(原始数字表)。旧的拓展实验按补丁和测试条件重新整理在 `runs/followup/CORRECTNESS_BY_PATCH.md`。

## 协议要点(已冻结,提交 527c5d0 之后不再改)
- 实验协议:`runs/round2/protocol.json`;任务链:`runs/round2/chains/`。
- 同一对照内模型、提示模板、temperature、max_tokens 一致;best-of-N 每次从 stock 出发,不接收历史、成绩或失败反馈。
- 预算统计所有实际发出的 HTTP 请求(含 502、截断、失败反馈重试);调用前的失败(选区、show、splice)只记录,不算请求。
- 一个运行可能分成多段(Slurm 作业时限),每段结束保存检查点,续跑不重放已计费请求;跨节点时重新测量种群成绩。
- 所有 xcnc、xcnd 节点视为等价(按你的指示),每段的真实节点和 CPU 都有记录。
- 模型访问作业任一时刻最多 4 个(4 条任务链并行);其他纯测量任务另外排队并行。

## 不能说明什么
- C2 人工控制的原始一小时计时缺失,无法补成已完成。
- 扩展正确性检查是附加验证,不是这些搜索当时的准入规则;0 条 TSan 告警只表示本次没有检出。
- 不同模型、协议和版本的结果分开汇总,不混合计算总体中位数。
