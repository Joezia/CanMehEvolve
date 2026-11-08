#!/usr/bin/env python3
"""One-shot edit of src/Search.cpp for round 2: HTTP-request budget for every mode, `bestofn-confirmed` mode (best-of-N judged by the same
confirmation rule as the population search), checkpoint/resume (state.json), an explicit exploit-share option, segment log, credits_extra.csv.
Kept in the repository so the change is reviewable; run once, then commit the resulting Search.cpp."""
from pathlib import Path
p = Path("src/Search.cpp")
s = p.read_text()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:70], s.count(a))
    s = s.replace(a, b)


# options
rep("  int preflightCount = 4;\n};", """  int preflightCount = 4;
  /// HTTP-request budget (0 = --generations). Every request that is sent counts: 502s, truncated replies, repair attempts.
  /// A failure before any request (show, splice, ...) is recorded but is not a request.
  int requestBudget = 0;
  /// Share of region draws sent to the region with the largest credited improvement (population search only; best-of-N never uses history).
  double exploitShare = 0.25;
  /// Continue from <out>/state.json (population, parent patches, RNG state, pending failure feedback, counters).
  bool resume = false;
  std::string segmentLabel;
};""")
rep('app.add_option("--mode", options.mode, "search | greedy | bestofn | preflight")\n      ->check(CLI::IsMember({"search", "greedy", "bestofn", "preflight"}));',
    'app.add_option("--mode", options.mode, "search | bestofn-confirmed | greedy | bestofn | preflight")\n      ->check(CLI::IsMember({"search", "bestofn-confirmed", "greedy", "bestofn", "preflight"}));')
rep('  app.add_option("--preflight-count", options.preflightCount, "preflight: extra size-quantile functions (max 4)");',
    '''  app.add_option("--preflight-count", options.preflightCount, "preflight: extra size-quantile functions (max 4)");
  app.add_option("--request-budget", options.requestBudget, "HTTP requests to send (0 = --generations); every request sent counts");
  app.add_option("--exploit-share", options.exploitShare, "population search: share of draws sent to the best-credited region");
  app.add_flag("--resume", options.resume, "continue from <out>/state.json");
  app.add_option("--segment-label", options.segmentLabel, "label written to segments.jsonl");''')
rep('  const auto bestOfN = options.mode == "bestofn";\n  const auto rankMode', '  const auto bestOfN = options.mode == "bestofn" || options.mode == "bestofn-confirmed";\n  const auto resuming = options.resume && fs::exists(out / "state.json");\n  const auto rankMode')
rep('  writeFile(out / "run.json", dumpJson(runInfo, 2) + "\\n");',
    '  writeFile(out / (resuming ? "run_resume_" + std::to_string(std::time(nullptr)) + ".json" : std::string{"run.json"}), dumpJson(runInfo, 2) + "\\n");')

# profile: reuse saved samples on resume
rep('  auto profileSummary = json{{"ran", false}};\n  if (options.sampleSeconds > 0.0) {',
    '''  auto profileSummary = json{{"ran", false}};
  if (resuming) {
    // the profile of the first segment is reused as saved: no new profiling, no new draws from a different profile
    const auto saved = json::parse(readFile(out / "profile_samples.json"));
    for (auto& region : regions) region.samples = saved.value(std::to_string(region.id), 0LL);
    profileSummary = json{{"ran", false}, {"resumed", true}};
  } else if (options.sampleSeconds > 0.0) {''')
rep('  writeFile(out / "profile.json", dumpJson(profileSummary, 2) + "\\n");',
    '''  if (!resuming) {
    writeFile(out / "profile.json", dumpJson(profileSummary, 2) + "\\n");
    auto savedSamples = json::object();
    for (const auto& region : regions) savedSamples[std::to_string(region.id)] = region.samples;
    writeFile(out / "profile_samples.json", dumpJson(savedSamples, 1) + "\\n");
  }''')

# exploit share option
rep('  constexpr auto exploitShare = double{0.25};\n', '')
rep('    if (!rankMode && unit() < exploitShare) {', '    if (!rankMode && !bestOfN && options.exploitShare > 0.0 && unit() < options.exploitShare) {')

# credits header only on a fresh run; extra credits file
rep('''  if (rankMode)
    appendLine(out / "credits.csv",
               "generation,calls,prompt_tokens,completion_tokens,reasoning_tokens,total_tokens,"
               "best_ranked_speedup,truncated_replies,llm_seconds,elapsed_s");
  else
    appendLine(out / "credits.csv",
               "generation,calls,prompt_tokens,completion_tokens,total_tokens,"
               "best_confirmed_speedup,best_retained_speedup,elapsed_s");''',
    '''  if (!resuming) {
    if (rankMode)
      appendLine(out / "credits.csv",
                 "generation,calls,prompt_tokens,completion_tokens,reasoning_tokens,total_tokens,"
                 "best_ranked_speedup,truncated_replies,llm_seconds,elapsed_s");
    else {
      // exactly the columns the course README lists; the extra accounting goes to credits_extra.csv
      appendLine(out / "credits.csv",
                 "generation,calls,prompt_tokens,completion_tokens,total_tokens,"
                 "best_confirmed_speedup,best_retained_speedup,elapsed_s");
      appendLine(out / "credits_extra.csv", "generation,segment,http_attempts_total,reasoning_tokens,truncated_replies,llm_seconds");
    }
  }
  if (resuming && rankMode) {
    std::cerr << "--resume is implemented for the search and bestofn-confirmed modes only\\n";
    return 6;
  }''')

# checkpoint / resume block, inserted before the loop
checkpoint = r'''  // ---- checkpoint / resume ------------------------------------------------
  const auto budget = static_cast<long long>(options.requestBudget > 0 ? options.requestBudget : options.generations);
  auto startGen = 1;
  auto segmentIndex = 1;
  auto elapsedBase = double{0.0};
  auto lastHost = std::string{};
  auto lastGenDone = 0;
  const auto patchJson = [](const EvaluatedPatch& q) {
    return json{{"id", q.id}, {"parent", q.parent}, {"generation", q.generation}, {"region", q.region}, {"patch", q.patchPath},
                {"score", q.score}, {"valid", q.valid}, {"note", q.note}, {"significant", q.significant},
                {"significant_at_min_effect", q.significantAtMinEffect}};
  };
  const auto patchFrom = [](const json& j) {
    auto q = EvaluatedPatch{};
    q.id = j.value("id", 0);
    q.parent = j.value("parent", -1);
    q.generation = j.value("generation", 0);
    q.region = j.value("region", -1);
    q.patchPath = j.value("patch", std::string{});
    q.score = j.value("score", invalidScore);
    q.valid = j.value("valid", false);
    q.note = j.value("note", std::string{});
    q.significant = j.value("significant", false);
    q.significantAtMinEffect = j.value("significant_at_min_effect", false);
    return q;
  };
  const auto totalElapsed = [&] { return elapsedBase + elapsed(); };
  const auto saveState = [&](int lastGen, bool complete, const std::string& why) {
    auto st = json{{"version", 1}, {"mode", options.mode}, {"seed", options.seed}, {"last_generation", lastGen}, {"complete", complete}, {"why", why},
                   {"calls", calls}, {"prompt_tokens", promptTokens}, {"completion_tokens", completionTokens}, {"total_tokens", totalTokens},
                   {"reasoning_tokens", reasoningTokens}, {"truncated_replies", truncatedReplies}, {"llm_seconds", llmSeconds},
                   {"best_confirmed_ratio", bestConfirmedRatio}, {"best_confirmed_id", bestConfirmedId}, {"best_retained_ratio", bestRetainedRatio},
                   {"stage_counts", stageCounts}, {"confirmed_count", confirmedCount}, {"improved_count", improvedCount},
                   {"elapsed_total_s", totalElapsed()}, {"host", std::string{host}}, {"slurm_job_id", env("SLURM_JOB_ID")}, {"segment", segmentIndex},
                   {"request_budget", budget}};
    auto rs = std::ostringstream{};
    rs << rng;
    st["rng"] = rs.str();
    auto pop = json::array();
    for (const auto& q : population) pop.push_back(patchJson(q));
    st["population"] = pop;
    auto rg = json::object();
    for (const auto& [id, rstat] : regionStats)
      rg[std::to_string(id)] = {{"attempts", rstat.attempts}, {"accepted", rstat.accepted}, {"best_gain", rstat.bestGain}};
    st["region_stats"] = rg;
    st["repair"] = {{"active", repair.active}, {"region_index", repair.regionIndex}, {"parent", patchJson(repair.parent)}, {"failure", repair.failure}};
    writeFile(out / "state.json.tmp", dumpJson(st, 1) + "\n");
    fs::rename(out / "state.json.tmp", out / "state.json");
  };
  if (resuming) {
    const auto st = json::parse(readFile(out / "state.json"));
    if (st.at("mode").get<std::string>() != options.mode || st.at("seed").get<unsigned>() != options.seed) {
      std::cerr << "state.json belongs to another mode or seed; refusing to resume\n";
      return 6;
    }
    if (st.value("complete", false)) {
      std::cerr << "state.json says the run is complete; nothing to resume\n";
      return 0;
    }
    startGen = st.at("last_generation").get<int>() + 1;
    lastGenDone = startGen - 1;
    segmentIndex = st.value("segment", 1) + 1;
    elapsedBase = st.value("elapsed_total_s", 0.0);
    lastHost = st.value("host", std::string{});
    calls = st.at("calls").get<long long>();
    promptTokens = st.at("prompt_tokens").get<long long>();
    completionTokens = st.at("completion_tokens").get<long long>();
    totalTokens = st.at("total_tokens").get<long long>();
    reasoningTokens = st.value("reasoning_tokens", 0LL);
    truncatedReplies = st.value("truncated_replies", 0LL);
    llmSeconds = st.value("llm_seconds", 0.0);
    bestConfirmedRatio = st.at("best_confirmed_ratio").get<double>();
    bestConfirmedId = st.value("best_confirmed_id", 0);
    bestRetainedRatio = st.at("best_retained_ratio").get<double>();
    stageCounts = st.at("stage_counts").get<std::map<std::string, int>>();
    confirmedCount = st.value("confirmed_count", 0);
    improvedCount = st.value("improved_count", 0);
    {
      auto rs = std::istringstream{st.at("rng").get<std::string>()};
      rs >> rng;
    }
    for (const auto& q : st.at("population")) population.push_back(patchFrom(q));
    for (const auto& [id, v] : st.at("region_stats").items()) {
      auto rstat = RegionStats{};
      rstat.attempts = v.value("attempts", 0);
      rstat.accepted = v.value("accepted", 0);
      rstat.bestGain = v.value("best_gain", 0.0);
      regionStats[std::stoi(id)] = rstat;
    }
    const auto& rp = st.at("repair");
    repair.active = rp.value("active", false);
    repair.regionIndex = rp.value("region_index", std::size_t{0});
    repair.parent = patchFrom(rp.at("parent"));
    repair.failure = rp.value("failure", std::string{});
    // A population member's score came from the node that measured it. On another node it is measured again before it is ranked against anything new.
    if (!lastHost.empty() && lastHost != std::string{host}) {
      for (auto& q : population) {
        const auto m = measureOnce(options, q.patchPath, out / "measurements" / ("reeval_seg" + std::to_string(segmentIndex) + "_id" + std::to_string(q.id) + ".json"));
        const auto okm = m.harnessOk && m.analysis.valid;
        appendLine(out / "reeval.jsonl", dumpJson(json{{"segment", segmentIndex}, {"id", q.id}, {"old_score", q.score}, {"new_score", okm ? json(m.analysis.ratio) : json(nullptr)},
                                                        {"from_host", lastHost}, {"to_host", std::string{host}}}));
        if (okm) q.score = m.analysis.ratio;
      }
      std::stable_sort(population.begin(), population.end(), [](const EvaluatedPatch& x, const EvaluatedPatch& y) { return x.score < y.score; });
      for (const auto& q : population)
        if (repair.active && q.id == repair.parent.id) repair.parent.score = q.score;
    }
    std::cerr << "[resume] segment " << segmentIndex << " continues after generation " << lastGenDone << " with " << calls << " requests already sent\n";
  }
  appendLine(out / "segments.jsonl", dumpJson(json{{"segment", segmentIndex}, {"event", "start"}, {"time", nowIso()}, {"host", std::string{host}},
                                                    {"slurm_job_id", env("SLURM_JOB_ID")}, {"calls_at_start", calls}, {"resumed", resuming},
                                                    {"label", options.segmentLabel}, {"previous_host", lastHost}}));

'''
rep('  auto endedBecause = std::string{"generations exhausted"};\n  for (auto gen = 1; gen <= (rankMode ? 4 * options.generations : options.generations); ++gen) {\n    if (rankMode && calls >= options.generations) break;  // the budget is HTTP requests sent\n',
    checkpoint + '''  auto endedBecause = std::string{"generation cap reached"};
  for (auto gen = startGen; gen <= static_cast<int>(6 * budget); ++gen) {
    if (calls >= budget) { endedBecause = "request budget reached"; break; }  // the budget is HTTP requests sent
''')
# per-record fields and elapsed
rep('    record["elapsed_s"] = elapsed();', '    record["elapsed_s"] = totalElapsed();\n    record["segment"] = segmentIndex;')
rep('<< std::setprecision(1) << std::fixed << llmSeconds << "," << elapsed();', '<< std::setprecision(1) << std::fixed << llmSeconds << "," << totalElapsed();')
rep('<< "," << std::setprecision(1) << std::fixed << elapsed();\n      appendLine(out / "credits.csv", row.str());',
    '<< "," << std::setprecision(1) << std::fixed << totalElapsed();\n      appendLine(out / "credits.csv", row.str());\n      if (!rankMode)\n        appendLine(out / "credits_extra.csv", std::to_string(gen) + "," + std::to_string(segmentIndex) + "," + std::to_string(calls) + "," + std::to_string(reasoningTokens) + "," +\n                                                std::to_string(truncatedReplies) + "," + std::to_string(llmSeconds));')
rep('    writeRegionsTried();\n    std::cerr << "[gen "', '    writeRegionsTried();\n    lastGenDone = gen;\n    saveState(gen, false, "");\n    std::cerr << "[gen "')
# final summary
rep('  auto summary = json{{"finished", nowIso()},\n                      {"ended_because", endedBecause},',
    '''  const auto complete = (endedBecause == "request budget reached" || endedBecause == "generation cap reached");
  auto summary = json{{"finished", nowIso()},
                      {"complete", complete},
                      {"request_budget", budget},
                      {"http_attempts", calls},
                      {"segments", segmentIndex},
                      {"ended_because", endedBecause},''')
rep('                      {"elapsed_s", elapsed()}};\n  writeFile(out / "summary.json", dumpJson(summary, 2) + "\\n");\n  std::cerr << "[done] " << dumpJson(summary) << "\\n";\n  return 0;',
    '''                      {"elapsed_s", totalElapsed()}};
  saveState(lastGenDone, complete, endedBecause);
  appendLine(out / "segments.jsonl", dumpJson(json{{"segment", segmentIndex}, {"event", "end"}, {"time", nowIso()}, {"calls_at_end", calls},
                                                    {"ended_because", endedBecause}, {"complete", complete}}));
  // an unfinished segment (deadline or signal) leaves state.json for --resume and a partial summary; only a finished run writes summary.json
  writeFile(out / (complete ? "summary.json" : "summary_partial.json"), dumpJson(summary, 2) + "\\n");
  std::cerr << "[done] " << dumpJson(summary) << "\\n";
  return complete ? 0 : 75;''')
p.write_text(s)
print("patched")
