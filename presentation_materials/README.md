# presentation_materials

汇报资料包:整理、核对、重新计算已有数据;没有启动任何新实验,没有修改任何原始日志。

| 文件 | 内容 |
|---|---|
| `overview_zh.md` | 项目整体逻辑、主要结果表、三个“核心发现”候选 |
| `evidence_zh.md` | 按研究问题组织的完整解释、结果表和统计(0 术语 → 1 做了什么 → 2 搜索方法 → 3 测量可信度 → 4 编译器与人工 → 5 搜索 vs 独立采样 → 6 收益来源 → 7 正确性 → 8 局限) |
| `qa_zh.md` | 关键问答资料(α、p 值、CP 区间、2% 门槛、种子、函数选择、种群与 greedy、best-of-N 公平性、正确性覆盖、局限) |
| `tables/` | 全部 CSV:`runs_all.csv`(40 个运行逐一)、校准、误报、空搜索、控制、配置汇总与检验、组合、正确性、成本等 |
| `sources.csv` | 每个重要数字/结论 → 原始文件、字段、计算方式、脚本 |
| `figures/` | 静态图(PNG + 矢量 PDF)`fig1`–`fig10`;绘图数据在 `figure_data/`,脚本是 `scripts/make_figures.py` |
| `scripts/` | 重建一切的脚本;`bash presentation_materials/scripts/run_all.sh`(约半分钟,从仓库根目录运行) |
| `intermediate/` | 拼成 `evidence_zh.md` 的分段文件(生成物) |

## 三个代码版本(实验条件,不是时间线)
I1 = 原始种群搜索实现(Qwen,40 次模型调用);I2 = DeepSeek 的 greedy / best-of-N(排序规则,40 个 HTTP 请求);I3 = README 完整循环及匹配 best-of-N(两个模型,恰好 40 个 HTTP 请求)。各配置的代码哈希见 `evidence_zh.md` §0。

## 定义
`ratio = 候选/原库`(<1 更快);`speedup = 1/ratio`;对外的加速值 = 固定最终补丁的 3 次独立复测的中位数。检验一律是探索性的,单位是种子(不配对)。**未测试的对象在正确性表中写“未测试”,不归入通过。**
