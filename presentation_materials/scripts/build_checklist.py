#!/usr/bin/env python3
"""Course-requirement checklist: 'implemented in code' and 'actually used in the formal runs' are separate columns. Evidence paths are relative to the repository root."""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from pm_lib import *
Y, N, P = "yes", "no", "partly"
rows = [
 ("种群:最多 6 个补丁,按 ratio 排序,淘汰最差,每个测到的候选都保留", "README 术语表 population", "I1 有;I3 有;I2 代码里有该模式,但 I2 正式运行用的是排序模式",
  "种群搜索(I1、I3)用了;greedy 和所有 best-of-N 没有(单记录/设计上无记忆)", "src/Search.cpp population 向量、stable_sort、pop_back;runs/round2/runs/*/state.json", "满足"),
 ("父补丁用二选一锦标赛选出;子补丁在父补丁之上(谱系/继承)", "README 术语表", "I1 有;I3 有;I2 的 greedy 在当前最好补丁上继续(无锦标赛)",
  "种群搜索用了;greedy 累计但无锦标赛;best-of-N 永远从原库", "src/Search.cpp pickParent;results.jsonl parent、parent_ratio", "满足"),
 ("失败(编译、检查)反馈到下一轮提示词(一次修复尝试)", "README Phase 1 循环", "I1 有;I3 有;I2 无",
  "种群搜索用了;greedy 没有;best-of-N 没有(C3 要求无反馈)", "src/Search.cpp isRepairable / repair.active;results.jsonl repair_attempt", "满足"),
 ("第 1 代之前做一次 profile;按样本比例抽函数,10% 均匀", "README --sample-seconds、--uniform-share", "所有版本", "全部 40 个运行:20 s perf 采样,均匀份额 0.1(续跑的运行复用保存的 profile)",
  "runs/*/profile.json、profile_samples.json;run.json sample_seconds、uniform_share", "满足"),
 ("收益分支:有最大已记录收益的函数被抽到更多", "README region credit / improved_on_parent", "I1 有;I3 有(25% 份额,是我们自己的选择);I2 无", "只有种群搜索用了", "src/Search.cpp pickRegion 收益分支;regions_tried.json best_gain", "部分(机制由我们设定)"),
 ("搜索前用 CanMehHarness init 做 null_ok 检查", "README Phase 1", "所有版本", "全部 40 个运行 null_ok = true(I3 每一段都检查)", "runs/*/run.json null_evidence;segments/*.init.json", "满足"),
 ("每个候选在计时前过课程提供的检查(库能载入、4 个文件校验值、profile 查询摘要、自己不开线程、处理器时间)", "README Phase 1 / measure-patch", "课程提供的 harness", "全部 40 个运行;失败计入 runs_all.csv 的 check_fail", "results.jsonl stage;runs/*/harness/", "满足"),
 ("判定规则用原始 timings(measure-patch --no-decision)和自己的统计", "README Phase 1", "所有版本", "所有运行;Phase 0 的 680 个有效试验(681 个文件,1 个不可读)重放与已存判定 0 条不一致", "src/Search.cpp analyzeTimings;tables/calibration_checks.json", "满足"),
 ("候选只有两次测量都通过规则才算“确认”", "README best_confirmed_speedup", "I1、I3 是确认规则;I2 用排序规则(R = 两次 ratio 的最大值,无显著性、无 2% 门槛),确认只作诊断标记",
  "I1、I3 用了;I2 greedy/best-of-N 只用排序;确认值由固定最终补丁的独立复测给出", "results.jsonl confirmed、rule_pass_1/2;tables/runs_all.csv", "部分(I2)"),
 ("credits.csv 恰好是 generation,calls,prompt_tokens,completion_tokens,total_tokens,best_confirmed_speedup,best_retained_speedup,elapsed_s", "README 输出文件", "I1 有;I3 有;I2 无(排序模式列:含 reasoning_tokens、best_ranked_speedup)",
  "I1、I3 满足;I2 不符合(已记录);所以 I2 的课程指标用独立复测值计算", "runs/*/credits.csv 表头", "部分(I2)"),
 ("预算 = 40 次模型调用;按调用数比较,不按代数", "README --generations", "I1:40 次调用(可能有隐藏重试);I2/I3:40 个 HTTP 请求",
  "I1 40 次模型调用;I2 40 个 HTTP 请求(种子 1、3、4、5 在作业时限处停在 39、38、34、34,由重放此前抽取的续跑补足);I3 恰好 40 个请求", "summary.json api_calls / http_attempts;results.jsonl llm.http_attempts", "满足(I1 的请求数不可核实)"),
 ("每个配置至少 5 个种子;报告中位数和完整范围(C4)", "README C4", "—", "8 个配置全部 5 个种子", "tables/config_summary.csv", "满足"),
 ("C1 编译器对照:-O2、-O3、-O3 -march=native", "README C1", "—", "在一个节点(xcnd24)上,每个比较 5 次测量;第一个 -march=native 批次无效,已由后一批取代", "tables/controls_summary.csv", "满足"),
 ("C2 人工对照:一个计时的小时,报告补丁和时间", "README C2", "—", "测了两个人工补丁;一小时的计时没有记录(只有文件时间);AI 辅助", "runs/human-control/c2-1058781/", "部分(无计时)"),
 ("C3 同调用预算的独立采样(从原库的 best-of-N,无记忆)", "README C3", "I1、I2、I3", "Qwen:I1 与 I3 两组;DeepSeek:I3 一组(确认规则)和与 greedy 配对的 I2 best-of-N(排序规则)", "tables/within_model_tests.csv", "满足"),
 ("记录实际回答的模型 id;token 与声称的加速并列", "README Evidence", "I1 只有一次探测;I2/I3 逐请求", "DeepSeek:每个响应都是 deepseek-v4.1-flash-1017;Qwen I1:只有一次探测;I3:逐请求;58 个 DeepSeek 请求返回 HTTP 502 且无 usage(消耗未知,不是 0)", "results.jsonl llm.model_returned、usage_seen", "满足"),
 ("同时最多提交 4 个 LLM 作业", "README Cluster", "—", "I1:10 个作业,观察到最多 4 个并发;I2:观察到 8 个并发(种子 2–5 的作业按指示同时启动);I3:4 条链", "各 node.txt 起止时间;runs/deepseek/submission-s2-5.txt;tables/llm_job_concurrency.csv", "部分(I2 超过 4)"),
 ("只在 xcnc 或 xcnd 计算节点计时,整节点,一作业一节点", "README Cluster", "—", "是;xcnc 上原库解码约 358 ms,xcnd 约 480 ms(节点类别在 I1/I2 里与种子不平衡)", "runs/*/node.txt;tables/run_baselines_and_parameters.csv", "满足"),
 ("Phase 0:误报率、检测阈值(各效应的检出率)、偏差;试验数与参数", "README Phase 0", "—", "校准:主要六对各 100 个试验(两批),sweep 各 20;合成 null 500;SDK 无效补丁 804", "tables/calibration_pairs.csv、fpr_summary.csv", "满足"),
 ("在 SDK 里拼接无效补丁并评测", "README Phase 0 证据", "—", "src/fit.cpp 的仅注释补丁;16 个批次共 804 次测量,另有 5 次手工测量", "runs/inert-check/inert.patch", "满足"),
]
out = [{"requirement": a, "source_in_README": b, "implemented_in_code": c, "used_in_the_formal_runs": d, "evidence": e, "status": f} for a, b, c, d, e, f in rows]
write_csv(PM / "tables/requirements_checklist.csv", out)
print(len(out), "rows")
