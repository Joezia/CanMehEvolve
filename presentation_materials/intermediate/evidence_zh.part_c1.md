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
