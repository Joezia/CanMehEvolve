# max-lines 600 单次实验(独立记录,不与第二轮混合)

## 目的
默认 `--max-lines 250` 会把约 540 行的 `Decode::ReadByte`(fit_decode.cpp 第 431–970 行)挡在搜索范围外。这里把上限调到 600,让 DeepSeek 在起点补丁上只改它一次,看结果。

## 设置(作业 1107035,节点 xcnc7,E5-2620 v3)
- 起点补丁:`runs/round2/runs/ds-population-s3/best.patch`(第二轮正式运行里 DeepSeek 最好的一个,sha256 46ce7efd…)。没有选上一轮 greedy 种子 2(复测约 1.2155×),因为它不在第二轮正式运行里。
- 目标函数:固定为 `Decode::ReadByte`(region id 56,540 行,`--max-lines 600`)。这是我替你定的;按采样权重随机抽的话多半又会抽到 `Profile::GetMesg`。
- 模型与参数同第二轮正式运行:`deepseek-v4.1-flash`(实际应答 `deepseek-v4.1-flash-1017`)、max_tokens 32768、单次请求超时 600 s、不自动重试、population 模式(失败带反馈重试)。
- 停止条件:第一个"编译成功并测完速"的候选;编译等失败不计这一次修改。请求上限 8 次(实际只用了 1 次)。
- 程序:`scripts/maxlines600/Search_maxlines600.cpp` = `src/Search.cpp` + 三个选项(`--seed-patch`、`--force-label`、`--stop-after-measured`);`src/Search.cpp` 没有改动。编译 `scripts/maxlines600/build.sbatch`,运行 `scripts/maxlines600/run.sbatch`。
- 节点上的原始记录:`run-1107035/node.txt`(git 提交、二进制 sha 等)。

## 结果
| 项目 | 数值 |
|---|---|
| 起点补丁,本节点搜索前测 1 次 | 1.184× |
| 新补丁,搜索内两次测量 | ratio 0.4301 / 0.4306(2.32×),均通过冻结规则(p=0.00195) |
| 起点补丁,独立复测 3 次(同节点) | 中位 1.183×,3/3 通过(候选 ≈ 302.7 ms,原版 ≈ 358.5 ms) |
| 新补丁,独立复测 3 次(同节点) | 中位 **2.318×**,范围 2.315–2.321×,3/3 通过(候选 ≈ 154.7 ms,原版 ≈ 358.9 ms) |
| 请求 | 1 次 HTTP;输入 4,736、输出 25,579(其中推理 21,186)token;模型耗时 236 s |

比较对象都是原版 SDK 的 -O2 构建。新补丁 = 起点补丁 + `ReadByte` 的一次改写。

## 模型改了什么(见 `run-1107035/search/patches/gen_1.code.cpp`,与原函数对比)
- 去掉 `MesgDefinition defn = localMesgDefs[localMesgIndex];`(每解完一个字段拷贝一次带 vector 的对象,热路径上大量 malloc),改成引用 `localDef`。
- 把重复调用的 getter、循环上限缓存为局部变量。
- 我读代码的判断是行为不变,但**没有验证**。

## 能说和不能说
- 能说:放宽到能覆盖 `ReadByte` 之后,在一个第二轮最佳补丁上只改一次就得到 2.32×;改动机制与"拷贝 MesgDefinition"一致。
- 这说明 250 行限制确实挡住了一个高收益函数。`ReadByte` 自身采样只占约 4%,但它引起的分配开销记在 libc(malloc)名下,所以采样占比低估了它的收益。
- 不能说:
  - **只有一次抽样**,不代表模型每次都能做到,也不是搜索算法的比较。
  - **没有做扩展正确性测试**(459 个文件的差分、ASan/UBSan、TSan);只通过了搜索自带的检查(4 个固定文件的校验值等)。第二轮里种群搜索的几个补丁通过同样的检查后在扩展测试里出了问题,所以这个 2.32× 在测完之前不能当作"正确的优化"。
  - 起点补丁自带的问题(如 TSan 数据竞争报告)这次没有重新检查。
  - 第二轮的所有结果仍然是在 `--max-lines 250` 下得到的,不能因为这一次实验而改写。
