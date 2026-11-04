/// @file
/// CanMehSearch -- the search loop.
///
/// A single-population evolutionary search. Each individual is one patch: a
/// unified diff against the stock FIT SDK holding one region rewrite for each
/// ancestor of that patch. When the model answers and CanMehHarness splices the
/// answer, CanMehSearch adds exactly one region rewrite to the parent's patch;
/// when `show`, the model call or `splice` fails, CanMehSearch adds none.
///
/// In each generation CanMehSearch picks a parent patch and a region of source,
/// asks the model to rewrite that one region, and hands the reply to
/// CanMehHarness, which splices the rewrite into a new patch, builds the patched
/// tree and times the decode. CanMehHarness decides how to build and how to
/// measure; CanMehSearch decides only what to try next.
///
/// CLI11 generates the usage text from the option definitions in main. The
/// --llm-* options overwrite the matching fields of ChatClientConfig, which
/// utilities/ChatClient.hpp documents.
#include <signal.h>
#include <sys/wait.h>
#include <unistd.h>

#include <algorithm>
#include <cctype>
#include <cmath>
#include <csignal>
#include <cstdint>
#include <ctime>
#include <iomanip>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <sstream>
#include <string>
#include <vector>

#include <CLI11.hpp>
#include <nlohmann/json.hpp>

#include "utilities/ChatClient.hpp"
#include "utilities/LineSamples.hpp"
#include "utilities/Process.hpp"

using utilities::ChatClientConfig;
using utilities::ModelReply;
using utilities::requestModelReply;
using utilities::readFile;
using utilities::writeFile;
using utilities::truncate;
using utilities::runForJsonReply;


using nlohmann::json;

namespace {

#ifndef CANMEH_DEFAULT_HARNESS
#define CANMEH_DEFAULT_HARNESS "./CanMehHarness"
#endif
#ifndef CANMEH_DEFAULT_DECODE_FOR_SAMPLER
#define CANMEH_DEFAULT_DECODE_FOR_SAMPLER "./CanMehDecodeForSampler"
#endif

constexpr auto invalidScore = double{1e18};

struct Options {
  std::string work;
  std::string out = "runs/latest";
  std::string harnessPath = CANMEH_DEFAULT_HARNESS;
  std::string decodeForSamplerPath = CANMEH_DEFAULT_DECODE_FOR_SAMPLER;
  /// Zero means CanMehSearch runs no sampler, so the sample-weighted draw
  /// never happens and every draw the bestGain branch does not take is
  /// uniform. Above zero, CanMehSearch builds a library with debug line
  /// tables, samples a decode of it for this long, and draws regions in
  /// proportion to the samples each one took.
  double sampleSeconds = 0.0;
  /// The share of the draws the bestGain branch did not take that CanMehSearch
  /// makes uniformly over every region rather than in proportion to samples.
  /// Not zero by default: a one-line accessor the compiler inlined has no
  /// samples of its own, and rewriting it can still make the decode faster, so
  /// no region is unreachable. At 1.0 CanMehSearch never takes the
  /// sample-weighted draw; the bestGain draw still runs.
  double uniformShare = 0.1;
  /// Adds three sentences to the prompt naming the kinds of work to look
  /// for. Default false: those sentences name kinds of code worth rewriting,
  /// so a run with them answers a different question from a run without them,
  /// and your report has to say which arm produced the result you quote.
  bool promptHints = false;
  int generations = 40;
  int population = 6;
  int maxLines = 250;
  unsigned seed = 1;
  /// Empty means every region CanMehHarness indexes. There is no default list,
  /// because a hand-written one is the experimenter's guess about where the win
  /// is, and a narrowed region set has to come from a measured profile.
  std::string regionFileNames;
  /// "search" keeps a population and feeds failures back; "bestofn" is control
  /// C3: every call starts from the unmodified baseline with no memory.
  std::string mode = "search";
  /// Decision-rule parameters. minEffect is the smallest reduction in the
  /// median ratio the rule accepts; alpha is the two-sided sign-flip level.
  double minEffect = 0.02;
  double alpha = 0.01;
  /// Written by the batch script from `CanMehHarness init`'s stdout.
  std::string initJson;
  /// Stop starting new generations after this many seconds (0 = no limit), so
  /// a Slurm time limit cannot cut a run in the middle of writing its summary.
  double deadlineSeconds = 0.0;
  std::string apiKeyFile;
  std::string baseUrl;
  std::string model;
  double temperature = -1.0;
  /// Evaluation modes that call no model.
  std::vector<std::string> ruleEval;
  std::string evaluatePatch;
  int evaluateCount = 3;
};

struct Region {
  int id = 0;
  std::string file;
  std::string label;
  int lines = 0;
  /// 1-based and inclusive, as `CanMehHarness regions` prints them.
  /// weighRanges compares a profiler's line against these two to decide which
  /// region that line is in.
  int start = 0;
  int end = 0;
  /// Ending many profiler samples name a line inside this region. Zero when
  /// --sample-seconds was zero, so CanMehSearch ran no profiler.
  long long samples = 0;
};

/// One patch the search produced, together with what measuring that patch
/// reported. The patch itself is the diff in the file at patchPath; this struct
/// is what CanMehSearch records about that diff.
struct EvaluatedPatch {
  int id = 0;
  int parent = -1;
  int generation = 0;
  int region = -1;
  std::string patchPath;  // empty means the unmodified baseline
  double score = invalidScore;
  bool valid = false;  std::string note;
  /// Both measure-patch calls reported significant.
  bool significant = false;  /// Both measure-patch calls reported significant and the kept measurement's effect
  /// reached measure-patch's --min-effect. CanMehSearch admits a candidate on this
  /// field and not on significant, because signFlipPValue reads only whether
  /// the processes agree in direction: two candidates were called significant
  /// at 0.32 and 0.34 percent, far below what this instrument can resolve.
  ///
  /// measure-patch computed this from the whole accumulated patch against the
  /// reference, which is the only pair measure-patch measured. A child inherits its
  /// parent's rewrites, so a descendant of a patch that already clears
  /// --min-effect clears it too whatever its own rewrite did: 30 of 40
  /// generations of one cluster run reported true, from one discovery and
  /// 29 inheritors. Read improvedOnParent for the one generation.
  bool significantAtMinEffect = false;
};

struct RegionStats {
  int attempts = 0;
  int accepted = 0;
  // The largest ratio improvement this region produced against the parent the
  // candidate came from, counting only a measurement measure-patch called significant.
  // A difference of two ratios, not a duration.
  double bestGain = 0.0;
};

json runHarnessCommand(const Options& options, std::vector<std::string> args,
                        double timeoutSeconds = 900);

/// The decision: did this candidate decode faster than the patch it was spliced
/// onto?
///
/// Phase 1 of README.md requires you to run measure-patch with --no-decision,
/// and CanMehHarness then sends neither `significant` nor `ratio`, so your
/// version computes the decision from reply["timings"] alone. That computation
/// is the assignment, which is why the rule is one function rather than an
/// expression inside the loop.
bool candidateIsFaster(const json& reply, double minEffect);

struct CodeBlock {
  std::string tag;
  std::string text;
};

std::vector<CodeBlock> codeBlocks(const std::string& reply);

/// Reads the replacement text and the include lines out of one model reply.
///
/// splitReply takes the first fenced block whose info string does not contain
/// "include" as the replacement, and the first block whose info string does
/// contain it as the include lines, which `CanMehHarness splice --includes`
/// merges into the file's include block.
///
/// splitReply clears code when the text contains no brace, because every
/// region is a function body and splice replaces its signature and braces as
/// well, so no usable replacement lacks one. One model reply held the word
/// includes and two #include lines and no function at all; splitReply returned
/// that text, splice wrote it into the tree and the compiler reported
/// "'includes' does not name a type", which CanMehSearch then recorded as
/// stage compile for a model that had written no code.
void splitReply(const std::string& reply, std::string* code, std::string* includes);

std::string systemPrompt();

std::string userPrompt(const Region& region, const std::string& currentText,
                        double parentRatio, double bestRatio, double baselineMs,
                        const std::string& failure, bool hints);

std::vector<std::string> splitCommas(const std::string& s) {
  auto out = std::vector<std::string>{};
  auto cur = std::string{};
  for (char c : s) {
    if (c == ',') {
      if (!cur.empty()) out.push_back(cur);
      cur.clear();
    } else if (c != ' ') {
      cur += c;
    }
  }
  if (!cur.empty()) out.push_back(cur);
  return out;
}


}  // namespace

namespace {

// ---------------------------------------------------------------------------
// Decision rule
// ---------------------------------------------------------------------------
//
// The rule reads reply["timings"] and nothing else. For each benchmark
// process it divides the median of candidate_ns by the median of reference_ns
// (both already per-decode means, so nothing is divided by an iteration
// count). The reported ratio is the MEDIAN over processes of those per-process
// ratios. The p-value is an exact two-sided sign-flip test on the process
// log-ratios whose statistic is the SUM of the log-ratios (so it uses the
// magnitude of each process's effect, not only its sign): all 2^N sign
// assignments are enumerated and p is the fraction whose |sum| is at least
// the observed |sum|. A candidate is "faster" when
//     ratio <= 1 - minEffect   and   p < alpha   and   the mean log-ratio < 0
// and the measurement is well formed (10 processes, equal-length series of at
// least 3 finite positive values, not ragged). The rule assumes independence
// of the PROCESSES (each is a separate OS process with its own library load,
// alternating slot order); it does not assume the repetitions inside one
// process are independent, because it only uses their median.

constexpr int kRequiredProcesses = 10;
constexpr double kUnstableSpread = 0.25;
double gAlpha = 0.01;

volatile sig_atomic_t gStop = 0;

struct Analysis {
  bool valid = false;
  std::string error;
  int processes = 0;
  int repetitions = 0;
  int swapped = 0;
  std::vector<double> processRatios;
  double ratio = 1.0;         // median of per-process ratios of medians
  double geomeanRatio = 1.0;  // reported for reference only
  double pValue = 1.0;
  double spread = 0.0;        // max - min of the per-process ratios
  double candidateMs = 0.0;   // median over processes of candidate medians
  double referenceMs = 0.0;
  double candidateCv = 0.0;   // largest within-process CV of candidate_ns
  double acMedian = 0.0, acMin = 0.0, acMax = 0.0;  // lag-1 autocorrelation, candidate_ns
  int fasterProcesses = 0;
  bool faster = false;
  bool unstable = false;
  std::string reason;
};

std::string dumpJson(const json& value, int indent = -1) {
  return value.dump(indent, ' ', false, json::error_handler_t::replace);
}

double medianOf(std::vector<double> values) {
  if (values.empty()) return 0.0;
  std::sort(values.begin(), values.end());
  const auto n = values.size();
  return n % 2 ? values[n / 2] : 0.5 * (values[n / 2 - 1] + values[n / 2]);
}

double meanOf(const std::vector<double>& values) {
  if (values.empty()) return 0.0;
  auto sum = double{0.0};
  for (double v : values) sum += v;
  return sum / static_cast<double>(values.size());
}

double sampleCv(const std::vector<double>& values) {
  if (values.size() < 2) return 0.0;
  const auto m = meanOf(values);
  auto ss = double{0.0};
  for (double v : values) ss += (v - m) * (v - m);
  return std::sqrt(ss / static_cast<double>(values.size() - 1)) / m;
}

/// Lag-1 sample autocorrelation as the README defines it, using the series'
/// own mean.
double lag1Autocorrelation(const std::vector<double>& x) {
  if (x.size() < 3) return 0.0;
  const auto m = meanOf(x);
  auto num = double{0.0}, den = double{0.0};
  for (std::size_t i = 0; i + 1 < x.size(); ++i) num += (x[i] - m) * (x[i + 1] - m);
  for (double v : x) den += (v - m) * (v - m);
  return den > 0.0 ? num / den : 0.0;
}

bool readSeries(const json& entry, const char* key, std::vector<double>* into) {
  if (!entry.contains(key) || !entry[key].is_array()) return false;
  into->clear();
  for (const auto& v : entry[key]) {
    if (!v.is_number()) return false;
    const auto d = v.get<double>();
    if (!std::isfinite(d) || d <= 0.0) return false;
    into->push_back(d);
  }
  return true;
}

/// Exact two-sided sign-flip p-value for the sum of `logs`.
double signFlipPValue(const std::vector<double>& logs) {
  const auto n = logs.size();
  auto observed = double{0.0};
  auto scale = double{0.0};
  for (double v : logs) {
    observed += v;
    scale += std::fabs(v);
  }
  observed = std::fabs(observed);
  const auto tolerance = double{1e-12 * std::max(scale, 1e-300)};
  auto atLeast = std::uint64_t{0};
  const auto total = std::uint64_t{1} << n;
  for (std::uint64_t mask = 0; mask < total; ++mask) {
    auto sum = double{0.0};
    for (std::size_t i = 0; i < n; ++i) sum += (mask >> i & 1) ? logs[i] : -logs[i];
    if (std::fabs(sum) >= observed - tolerance) ++atLeast;
  }
  return static_cast<double>(atLeast) / static_cast<double>(total);
}

Analysis analyzeTimings(const json& reply, double minEffect) {
  auto a = Analysis{};
  if (!reply.is_object() || !reply.value("ok", false)) {
    a.error = "measurement not ok";
    return a;
  }
  if (!reply.contains("timings") || !reply["timings"].is_object() ||
      !reply["timings"].contains("process") || !reply["timings"]["process"].is_array()) {
    a.error = "no timings.process";
    return a;
  }
  const auto& timings = reply["timings"];
  if (timings.value("ragged", false)) {
    a.error = "timings are ragged";
    return a;
  }
  const auto& processes = timings["process"];
  a.processes = static_cast<int>(processes.size());
  if (a.processes != kRequiredProcesses) {
    a.error = "need exactly " + std::to_string(kRequiredProcesses) + " processes, got " +
              std::to_string(a.processes);
    return a;
  }
  const auto requested = timings.value("repetitions_requested", 0);
  auto candidateMedians = std::vector<double>{};
  auto referenceMedians = std::vector<double>{};
  auto acs = std::vector<double>{};
  for (const auto& process : processes) {
    auto cand = std::vector<double>{};
    auto ref = std::vector<double>{};
    if (!readSeries(process, "candidate_ns", &cand) || !readSeries(process, "reference_ns", &ref)) {
      a.error = "missing or non-positive series in a process";
      return a;
    }
    if (cand.size() != ref.size() || cand.size() < 3 ||
        (requested > 0 && static_cast<int>(cand.size()) != requested)) {
      a.error = "series lengths disagree with repetitions_requested or are below 3";
      return a;
    }
    a.repetitions = static_cast<int>(cand.size());
    if (process.value("swapped", false)) ++a.swapped;
    const auto cm = medianOf(cand);
    const auto rm = medianOf(ref);
    candidateMedians.push_back(cm);
    referenceMedians.push_back(rm);
    a.processRatios.push_back(cm / rm);
    a.candidateCv = std::max(a.candidateCv, sampleCv(cand));
    acs.push_back(lag1Autocorrelation(cand));
  }
  auto logs = std::vector<double>{};
  for (double r : a.processRatios) {
    logs.push_back(std::log(r));
    if (r < 1.0) ++a.fasterProcesses;
  }
  a.ratio = medianOf(a.processRatios);
  a.geomeanRatio = std::exp(meanOf(logs));
  a.pValue = signFlipPValue(logs);
  a.spread = *std::max_element(a.processRatios.begin(), a.processRatios.end()) -
             *std::min_element(a.processRatios.begin(), a.processRatios.end());
  a.candidateMs = medianOf(candidateMedians) / 1e6;
  a.referenceMs = medianOf(referenceMedians) / 1e6;
  a.acMedian = medianOf(acs);
  a.acMin = *std::min_element(acs.begin(), acs.end());
  a.acMax = *std::max_element(acs.begin(), acs.end());
  a.unstable = a.spread > kUnstableSpread;
  a.valid = true;
  const auto meanLog = meanOf(logs);
  if (!(meanLog < 0.0)) a.reason = "mean log-ratio not below zero";
  else if (!(a.pValue < gAlpha)) a.reason = "sign-flip p not below alpha";
  else if (!(a.ratio <= 1.0 - minEffect)) a.reason = "median ratio above 1 - minEffect";
  a.faster = a.reason.empty();
  return a;
}

json analysisJson(const Analysis& a) {
  return json{{"valid", a.valid},
              {"error", a.error},
              {"processes", a.processes},
              {"repetitions", a.repetitions},
              {"swapped_processes", a.swapped},
              {"ratio", a.ratio},
              {"geomean_ratio", a.geomeanRatio},
              {"p_value", a.pValue},
              {"ratio_spread", a.spread},
              {"candidate_ms", a.candidateMs},
              {"reference_ms", a.referenceMs},
              {"candidate_cv", a.candidateCv},
              {"autocorr_lag1_median", a.acMedian},
              {"autocorr_lag1_min", a.acMin},
              {"autocorr_lag1_max", a.acMax},
              {"faster_processes", a.fasterProcesses},
              {"process_ratios", a.processRatios},
              {"faster", a.faster},
              {"unstable", a.unstable},
              {"reason", a.reason}};
}

bool candidateIsFaster(const json& reply, double minEffect) {
  return analyzeTimings(reply, minEffect).faster;
}

// ---------------------------------------------------------------------------
// Harness, reply parsing, prompts
// ---------------------------------------------------------------------------

json runHarnessCommand(const Options& options, std::vector<std::string> args,
                        double timeoutSeconds) {
  static auto counter = int{0};
  const auto directory = std::filesystem::path{options.out} / "harness";
  auto errorCode = std::error_code{};
  std::filesystem::create_directories(directory, errorCode);
  auto stem = std::ostringstream{};
  stem << "cmd" << std::setw(5) << std::setfill('0') << ++counter << "-" << args.front();
  const auto outPath = directory / (stem.str() + ".out");
  const auto errPath = directory / (stem.str() + ".err");
  auto reply = runForJsonReply(options.harnessPath, args, outPath, errPath, timeoutSeconds);
  // Keep the raw streams only for a command that failed; a successful one is
  // logged by the caller in a structured file.
  if (reply.is_object() && reply.value("ok", false)) {
    std::filesystem::remove(outPath, errorCode);
    std::filesystem::remove(errPath, errorCode);
  }
  return reply;
}

std::vector<CodeBlock> codeBlocks(const std::string& reply) {
  auto blocks = std::vector<CodeBlock>{};
  auto lines = std::vector<std::string>{};
  {
    auto stream = std::istringstream{reply};
    auto line = std::string{};
    while (std::getline(stream, line)) {
      if (!line.empty() && line.back() == '\r') line.pop_back();
      lines.push_back(line);
    }
  }
  auto inside = false;
  auto current = CodeBlock{};
  for (const auto& line : lines) {
    const auto first = line.find_first_not_of(" \t");
    const auto fenced = first != std::string::npos && line.compare(first, 3, "```") == 0;
    if (!inside) {
      if (!fenced) continue;
      inside = true;
      current = CodeBlock{};
      auto tag = line.substr(first + 3);
      const auto begin = tag.find_first_not_of(" \t");
      current.tag = begin == std::string::npos ? "" : tag.substr(begin);
    } else if (fenced && line.find_first_not_of(" \t`", first) == std::string::npos) {
      // A bare closing fence. A fence line with an info string inside a block
      // is treated as content.
      blocks.push_back(current);
      inside = false;
    } else {
      current.text += line + "\n";
    }
  }
  // An unterminated block means the reply was cut off (max_tokens), so its
  // code is incomplete and is dropped rather than spliced.
  return blocks;
}

void splitReply(const std::string& reply, std::string* code, std::string* includes) {
  code->clear();
  includes->clear();
  auto haveCode = false, haveIncludes = false;
  for (const auto& block : codeBlocks(reply)) {
    auto tag = block.tag;
    std::transform(tag.begin(), tag.end(), tag.begin(),
                   [](unsigned char c) { return std::tolower(c); });
    const auto isInclude = tag.find("include") != std::string::npos;
    if (isInclude && !haveIncludes) {
      *includes = block.text;
      haveIncludes = true;
    } else if (!isInclude && !haveCode) {
      *code = block.text;
      haveCode = true;
    }
  }
  // splice ignores #include lines inside the replacement, so lift them out.
  if (haveCode) {
    auto stream = std::istringstream{*code};
    auto kept = std::string{};
    auto line = std::string{};
    while (std::getline(stream, line)) {
      const auto first = line.find_first_not_of(" \t");
      if (first != std::string::npos && line.compare(first, 8, "#include") == 0) {
        if (includes->find(line) == std::string::npos) *includes += line + "\n";
      } else {
        kept += line + "\n";
      }
    }
    *code = kept;
  }
  if (code->find('{') == std::string::npos) code->clear();
}

std::string systemPrompt() {
  return "You are an expert C++ performance engineer. You are optimizing the decoder of the "
         "Garmin FIT SDK (release 21.201.0), compiled with g++ -O2 -std=c++17. The program "
         "being timed decodes four activity files completely and folds every decoded field "
         "value into a checksum.\n"
         "You are given ONE function and must return a faster drop-in replacement.\n"
         "Hard rules:\n"
         "- Keep the exact signature, name, class and return type, so that it links unchanged.\n"
         "- Behave identically for every input. The benchmark compares a checksum of all "
         "decoded values and sweeps the profile lookup functions over their whole input "
         "domain, so any behavioural difference makes the candidate be rejected.\n"
         "- Use no threads. Use only symbols visible in that source file plus the standard "
         "library; extra standard headers go in an include block.\n"
         "- Change only this function. Do not edit other functions or add new files.\n"
         "Reply format: first at most two short sentences saying what you changed and why it "
         "is faster, then exactly one ```cpp block holding the COMPLETE replacement function "
         "(signature and braces included). If you need extra headers add one ```include block "
         "with one #include line per line. Write nothing else.";
}

std::string userPrompt(const Region& region, const std::string& currentText, double parentRatio,
                        double bestRatio, double baselineMs, const std::string& failure,
                        bool hints) {
  auto p = std::ostringstream{};
  p << std::fixed << std::setprecision(3);
  p << "File: " << region.file << "\nFunction: " << region.label << " (" << region.lines
    << " lines)\n";
  p << "One full decode of the four files takes about " << std::setprecision(1) << baselineMs
    << " ms in the stock build.\n"
    << std::setprecision(3);
  p << "Time of the current version of the whole library relative to stock: " << parentRatio
    << " (below 1.0 is faster). Best measured so far: " << bestRatio << ".\n";
  if (hints)
    p << "Code worth rewriting in a decoder: repeated linear scans over tables that an index "
         "could answer, heap allocations and copies of containers or structures on a hot path, "
         "and redundant work repeated inside loops.\n";
  if (!failure.empty()) p << "\nYour previous attempt failed:\n" << failure << "\n";
  p << "\nCurrent text of the function:\n```cpp\n" << currentText << "\n```\n"
    << "Return the faster replacement now.";
  return p.str();
}

// ---------------------------------------------------------------------------
// Helpers for the loop
// ---------------------------------------------------------------------------

namespace fs = std::filesystem;

std::string trimmed(std::string s) {
  while (!s.empty() && std::isspace(static_cast<unsigned char>(s.back()))) s.pop_back();
  std::size_t b = 0;
  while (b < s.size() && std::isspace(static_cast<unsigned char>(s[b]))) ++b;
  return s.substr(b);
}

std::string nowIso() {
  const auto t = std::time(nullptr);
  char buffer[32];
  std::strftime(buffer, sizeof buffer, "%Y-%m-%dT%H:%M:%S%z", std::localtime(&t));
  return buffer;
}

void appendLine(const fs::path& path, const std::string& line) {
  auto file = std::ofstream{path, std::ios::app | std::ios::binary};
  file << line << "\n";
  file.flush();
}

std::string firstLineOf(const std::vector<std::string>& argv, const fs::path& scratch) {
  auto errorCode = std::error_code{};
  fs::create_directories(scratch, errorCode);
  const auto ran = utilities::runProcess(argv, scratch / "tmp.out", scratch / "tmp.err", 30);
  auto text = ran.ok() ? readFile(scratch / "tmp.out") : std::string{};
  const auto end = text.find('\n');
  return trimmed(end == std::string::npos ? text : text.substr(0, end));
}

/// One tiny request made directly so the endpoint's own `model` field, which
/// requestModelReply discards, reaches the log. Its tokens are reported
/// separately from credits.csv.
json probeModel(const ChatClientConfig& config) {
  auto handle = utilities::chatClientDetail::EasyHandle{curl_easy_init()};
  if (!handle) return json{{"ok", false}, {"error", "curl_easy_init failed"}};
  const auto payload =
      json{{"model", config.model},
           {"max_tokens", 16},
           {"messages", json::array({{{"role", "user"},
                                      {"content", "reply with the single word ok"}}})}}
          .dump();
  auto headers = utilities::chatClientDetail::HeaderList{
      curl_slist_append(nullptr, "Content-Type: application/json")};
  headers.reset(curl_slist_append(headers.release(), ("Authorization: Bearer " + config.apiKey).c_str()));
  auto response = std::string{};
  const auto url = config.baseUrl + "/chat/completions";
  curl_easy_setopt(handle.get(), CURLOPT_URL, url.c_str());
  curl_easy_setopt(handle.get(), CURLOPT_HTTPHEADER, headers.get());
  curl_easy_setopt(handle.get(), CURLOPT_POSTFIELDS, payload.c_str());
  curl_easy_setopt(handle.get(), CURLOPT_WRITEFUNCTION, utilities::chatClientDetail::appendToString);
  curl_easy_setopt(handle.get(), CURLOPT_WRITEDATA, &response);
  curl_easy_setopt(handle.get(), CURLOPT_TIMEOUT, 60L);
  const auto performed = curl_easy_perform(handle.get());
  auto status = long{0};
  curl_easy_getinfo(handle.get(), CURLINFO_RESPONSE_CODE, &status);
  if (performed != CURLE_OK)
    return json{{"ok", false}, {"error", std::string("transport: ") + curl_easy_strerror(performed)}};
  const auto parsed = json::parse(response, nullptr, false);
  if (parsed.is_discarded() || !parsed.is_object())
    return json{{"ok", false}, {"http_status", status}, {"error", truncate(response, 300)}};
  auto out = json{{"ok", status == 200},
                  {"http_status", status},
                  {"model", parsed.value("model", "")},
                  {"requested_model", config.model}};
  if (parsed.contains("usage")) out["usage"] = parsed["usage"];
  return out;
}

struct Measured {
  bool harnessOk = false;
  std::string stage;
  std::string error;
  Analysis analysis;
};

Measured measureOnce(const Options& options, const std::string& patchPath,
                     const fs::path& rawPath) {
  auto args = std::vector<std::string>{"measure-patch", "--work", options.work, "--no-decision"};
  if (!patchPath.empty()) {
    args.push_back("--patch");
    args.push_back(patchPath);
  }
  const auto reply = runHarnessCommand(options, args, 1800);
  writeFile(rawPath, dumpJson(reply, 1) + "\n");
  auto m = Measured{};
  m.harnessOk = reply.is_object() && reply.value("ok", false);
  if (!m.harnessOk) {
    m.stage = reply.is_object() ? reply.value("stage", std::string{"unknown"}) : "unknown";
    m.error = reply.is_object() ? reply.value("error", std::string{}) : "";
    return m;
  }
  m.analysis = analyzeTimings(reply, options.minEffect);
  if (!m.analysis.valid) {
    m.stage = "timings";
    m.error = m.analysis.error;
  }
  return m;
}

/// Everything main needs to know about the work directory.
struct WorkInfo {
  double baselineMs = 0.0;
  std::string dataDir;
  std::string cxx;
};

}  // namespace

namespace {

void onSignal(int) { gStop = 1; }

std::string zeroPadded(int n) {
  auto s = std::ostringstream{};
  s << std::setw(3) << std::setfill('0') << n;
  return s.str();
}

/// Reads the work directory's self-check evidence. `init`'s own null_ok is the
/// authoritative flag; meta.json keeps only null_ratio and reference_cv, so
/// that is the fallback when the batch script wrote no init.json.
bool checkNullEvidence(const Options& options, const json& meta, json* evidence) {
  *evidence = json::object();
  if (!options.initJson.empty() && fs::exists(options.initJson)) {
    const auto init = utilities::readJson(options.initJson);
    if (!init.is_discarded() && init.is_object() && init.contains("null_ok")) {
      *evidence = {{"source", options.initJson},
                   {"null_ok", init["null_ok"]},
                   {"null_ratio", init.value("null_ratio", 0.0)},
                   {"null_spread", init.value("null_spread", 0.0)},
                   {"reference_cv", init.value("reference_cv", 0.0)},
                   {"baseline_ms", init.value("baseline_ms", 0.0)}};
      return init["null_ok"].get<bool>();
    }
  }
  const auto ratio = meta.value("null_ratio", 0.0);
  const auto ok = std::fabs(ratio - 1.0) < 0.02 && meta.value("reference_cv", 1.0) < 0.25;
  *evidence = {{"source", "meta.json (no init.json found; null_spread unavailable)"},
               {"null_ok", ok},
               {"null_ratio", ratio},
               {"reference_cv", meta.value("reference_cv", 0.0)}};
  return ok;
}

int ruleEvalMode(const Options& options) {
  auto status = 0;
  for (const auto& file : options.ruleEval) {
    const auto reply = utilities::readJson(file);
    auto line = json{{"file", file}};
    if (reply.is_discarded()) {
      line["valid"] = false;
      line["error"] = "unreadable json";
      status = 1;
    } else {
      line.update(analysisJson(analyzeTimings(reply, options.minEffect)));
      if (reply.is_object() && reply.contains("timings"))
        line["min_time"] = reply["timings"].value("min_time", "");
    }
    std::cout << dumpJson(line) << "\n";
  }
  return status;
}

/// Measures one patch `evaluateCount` times, each a full independent
/// measure-patch, and applies the rule to every one. Used for the inert patch
/// and for the human candidate and for re-confirming a search's best patch.
int evaluatePatchMode(const Options& options) {
  const auto name = fs::path{options.evaluatePatch}.stem().string();
  const auto directory = fs::path{options.out} / ("evaluate-" + name);
  fs::create_directories(directory);
  auto measurements = json::array();
  auto ratios = std::vector<double>{};
  auto passes = 0;
  for (auto k = 1; k <= options.evaluateCount && !gStop; ++k) {
    const auto started = std::chrono::steady_clock::now();
    const auto m = measureOnce(options, options.evaluatePatch,
                               directory / ("m" + std::to_string(k) + ".json"));
    auto entry = json{{"index", k},
                      {"harness_ok", m.harnessOk},
                      {"stage", m.stage},
                      {"error", truncate(m.error, 600)},
                      {"seconds", std::chrono::duration<double>(
                                      std::chrono::steady_clock::now() - started).count()},
                      {"analysis", analysisJson(m.analysis)}};
    if (m.analysis.valid) {
      ratios.push_back(m.analysis.ratio);
      if (m.analysis.faster) ++passes;
    }
    measurements.push_back(entry);
    std::cerr << "[evaluate " << name << " #" << k << "] stage='" << m.stage << "' ratio="
              << m.analysis.ratio << " p=" << m.analysis.pValue
              << " faster=" << m.analysis.faster << "\n";
  }
  auto summary = json{{"patch", options.evaluatePatch},
                      {"started_utc", nowIso()},
                      {"min_effect", options.minEffect},
                      {"alpha", options.alpha},
                      {"measurements", measurements},
                      {"valid_measurements", ratios.size()},
                      {"measurements_passing_rule", passes},
                      {"median_ratio_over_measurements", ratios.empty() ? 0.0 : medianOf(ratios)},
                      {"all_pass", !ratios.empty() &&
                                       passes == static_cast<int>(options.evaluateCount)}};
  if (!ratios.empty()) {
    summary["worst_ratio"] = *std::max_element(ratios.begin(), ratios.end());
    summary["best_ratio"] = *std::min_element(ratios.begin(), ratios.end());
    summary["median_speedup"] = 1.0 / medianOf(ratios);
  }
  writeFile(directory / "summary.json", dumpJson(summary, 2) + "\n");
  std::cout << dumpJson(summary, 2) << "\n";
  return 0;
}

}  // namespace

int main(int argc, char** argv) {
  auto options = Options{};
  auto app = CLI::App{"CanMehSearch: LLM-driven patch search (and the best-of-N control)"};
  app.add_option("--work", options.work, "work directory created by CanMehHarness init");
  app.add_option("--out", options.out, "output directory for logs and patches");
  app.add_option("--harness", options.harnessPath, "CanMehHarness binary");
  app.add_option("--decode-for-sampler", options.decodeForSamplerPath, "CanMehDecodeForSampler binary");
  app.add_option("--mode", options.mode, "search | bestofn")
      ->check(CLI::IsMember({"search", "bestofn"}));
  app.add_option("--generations", options.generations, "model calls to make (one per generation)");
  app.add_option("--population", options.population, "population size");
  app.add_option("--max-lines", options.maxLines, "largest region to index");
  app.add_option("--seed", options.seed, "seed for region and parent draws");
  app.add_option("--sample-seconds", options.sampleSeconds, "profile for this long first; 0 = uniform draws");
  app.add_option("--uniform-share", options.uniformShare, "share of draws that ignore the profile");
  app.add_flag("--prompt-hints", options.promptHints, "add three hint sentences to the prompt");
  app.add_option("--region-files", options.regionFileNames, "comma-separated file names to restrict to");
  app.add_option("--min-effect", options.minEffect, "smallest reduction in the median ratio the rule accepts");
  app.add_option("--alpha", options.alpha, "two-sided sign-flip level");
  app.add_option("--init-json", options.initJson, "init's stdout, for the null_ok check");
  app.add_option("--deadline-seconds", options.deadlineSeconds, "start no new generation after this");
  app.add_option("--llm-api-key-file", options.apiKeyFile, "file holding the API key");
  app.add_option("--llm-base-url", options.baseUrl, "endpoint base URL");
  app.add_option("--llm-model", options.model, "model id to request");
  app.add_option("--llm-temperature", options.temperature, "sampling temperature");
  app.add_option("--rule-eval", options.ruleEval,
                 "apply the decision rule to saved measure-pair/measure-patch JSON files and print one line each");
  app.add_option("--evaluate-patch", options.evaluatePatch,
                 "measure this patch --evaluate-count times and apply the rule (no model)");
  app.add_option("--evaluate-count", options.evaluateCount, "measurements for --evaluate-patch");
  CLI11_PARSE(app, argc, argv);

  gAlpha = options.alpha;
  signal(SIGTERM, onSignal);
  signal(SIGINT, onSignal);

  if (!options.ruleEval.empty()) return ruleEvalMode(options);

  if (options.work.empty()) {
    std::cerr << "--work is required\n";
    return 2;
  }
  options.work = fs::absolute(options.work).string();
  options.out = fs::absolute(options.out).string();
  if (!options.evaluatePatch.empty()) options.evaluatePatch = fs::absolute(options.evaluatePatch).string();
  if (!options.initJson.empty()) options.initJson = fs::absolute(options.initJson).string();
  if (fs::path{options.harnessPath}.has_parent_path())
    options.harnessPath = fs::absolute(options.harnessPath).string();
  if (fs::path{options.decodeForSamplerPath}.has_parent_path())
    options.decodeForSamplerPath = fs::absolute(options.decodeForSamplerPath).string();
  fs::create_directories(options.out);

  if (!options.evaluatePatch.empty()) return evaluatePatchMode(options);

  // ---- self-check evidence and configuration ------------------------------
  const auto meta = utilities::readJson(fs::path{options.work} / "meta.json");
  if (meta.is_discarded() || !meta.is_object()) {
    std::cerr << "cannot read " << options.work << "/meta.json\n";
    return 2;
  }
  auto nullEvidence = json{};
  if (!checkNullEvidence(options, meta, &nullEvidence)) {
    std::cerr << "null run is not clean for this work directory; refusing to search: "
              << dumpJson(nullEvidence) << "\n";
    writeFile(fs::path{options.out} / "REFUSED_null_not_ok.json", dumpJson(nullEvidence, 2) + "\n");
    return 3;
  }
  const auto baselineMs = meta.value("baseline_ms", 0.0);
  const auto dataDir = meta.value("data", std::string{});

  auto config = ChatClientConfig{};
  if (!options.baseUrl.empty()) config.baseUrl = options.baseUrl;
  if (!options.model.empty()) config.model = options.model;
  if (options.temperature >= 0.0) config.temperature = options.temperature;
  if (options.apiKeyFile.empty()) {
    std::cerr << "--llm-api-key-file is required\n";
    return 2;
  }
  config.apiKey = trimmed(readFile(options.apiKeyFile));
  if (config.apiKey.empty()) {
    std::cerr << "API key file is empty or unreadable\n";
    return 2;
  }

  const auto out = fs::path{options.out};
  for (const char* sub : {"patches", "measurements", "prompts"}) fs::create_directories(out / sub);
  const auto bestOfN = options.mode == "bestofn";
  const auto started = std::chrono::steady_clock::now();
  const auto elapsed = [&] {
    return std::chrono::duration<double>(std::chrono::steady_clock::now() - started).count();
  };

  char host[256] = {0};
  gethostname(host, sizeof host - 1);
  const auto env = [](const char* name) {
    const auto* v = std::getenv(name);
    return std::string{v ? v : ""};
  };
  const auto probe = probeModel(config);
  auto runInfo = json{
      {"started", nowIso()},
      {"mode", options.mode},
      {"hostname", host},
      {"slurm_job_id", env("SLURM_JOB_ID")},
      {"slurm_nodelist", env("SLURM_JOB_NODELIST")},
      {"git_commit", firstLineOf({"git", "rev-parse", "HEAD"}, out / "scratch")},
      {"git_dirty", !firstLineOf({"git", "status", "--porcelain", "--untracked-files=no"}, out / "scratch").empty()},
      {"compiler", meta.value("cxx", "")},
      {"compiler_version", firstLineOf({meta.value("cxx", std::string{"c++"}), "--version"}, out / "scratch")},
      {"opt", meta.value("opt", "")},
      {"cxxstd", meta.value("cxxstd", "")},
      {"meta", meta},
      {"null_evidence", nullEvidence},
      {"model_requested", config.model},
      {"model_probe", probe},
      {"base_url", config.baseUrl},
      {"temperature", config.temperature},
      {"max_tokens", config.maxTokens},
      {"seed", options.seed},
      {"generations", options.generations},
      {"population", options.population},
      {"max_lines", options.maxLines},
      {"sample_seconds", options.sampleSeconds},
      {"uniform_share", options.uniformShare},
      {"prompt_hints", options.promptHints},
      {"region_files", options.regionFileNames},
      {"rule", {{"min_effect", options.minEffect},
                {"alpha", options.alpha},
                {"required_processes", kRequiredProcesses},
                {"unstable_spread", kUnstableSpread},
                {"statistic", "median over processes of median(candidate_ns)/median(reference_ns); exact two-sided sign-flip test on sum of log process ratios"}}},
      {"deadline_seconds", options.deadlineSeconds}};
  writeFile(out / "run.json", dumpJson(runInfo, 2) + "\n");
  writeFile(out / "system_prompt.txt", systemPrompt() + "\n");
  std::cerr << "[run] mode=" << options.mode << " host=" << host << " model_probe="
            << dumpJson(probe) << "\n";

  // ---- regions ------------------------------------------------------------
  const auto listing = runHarnessCommand(
      options, {"regions", "--work", options.work, "--max-lines", std::to_string(options.maxLines)}, 300);
  if (!listing.value("ok", false) || !listing.contains("regions")) {
    std::cerr << "regions failed: " << dumpJson(listing) << "\n";
    return 4;
  }
  auto regions = std::vector<Region>{};
  const auto allowedFiles = splitCommas(options.regionFileNames);
  for (const auto& r : listing["regions"]) {
    auto region = Region{};
    region.id = r.value("id", 0);
    region.file = r.value("file", "");
    region.label = r.value("label", "");
    region.lines = r.value("lines", 0);
    region.start = r.value("start", 0);
    region.end = r.value("end", 0);
    if (!allowedFiles.empty()) {
      const auto base = fs::path{region.file}.filename().string();
      if (std::find(allowedFiles.begin(), allowedFiles.end(), base) == allowedFiles.end() &&
          std::find(allowedFiles.begin(), allowedFiles.end(), region.file) == allowedFiles.end())
        continue;
    }
    regions.push_back(region);
  }
  if (regions.empty()) {
    std::cerr << "no regions to search\n";
    return 4;
  }

  // ---- profile before the first generation --------------------------------
  auto profileSummary = json{{"ran", false}};
  if (options.sampleSeconds > 0.0) {
    const auto library = runHarnessCommand(options, {"sampling-library", "--work", options.work}, 1800);
    if (!library.value("ok", false)) {
      profileSummary = json{{"ran", true}, {"ok", false}, {"error", truncate(dumpJson(library), 500)}};
    } else {
      auto request = utilities::SamplingRequest{};
      request.command = std::vector<std::string>{
          options.decodeForSamplerPath, "--library",
          library.value("library", (fs::path{options.work} / "libfit_sampling.so").string()),
          "--data", dataDir,
          // Without this the benchmark ends after ~2 decodes, before perf attaches.
          "--benchmark_min_time=" +
              std::to_string(static_cast<int>(options.sampleSeconds) + 40) + "s"};
      request.image = "libfit_sampling";
      request.scratch = out / "sampling";
      request.seconds = options.sampleSeconds;
      const auto profile = utilities::measureLineSamples(request);
      profileSummary = json{{"ran", true}, {"ok", profile.ok}, {"error", profile.error}, {"tool", profile.tool},
                        {"total", profile.total}, {"in_image", profile.inImage}, {"located", profile.located}};
      if (profile.ok) {
        auto ranges = std::vector<utilities::LineRange>{};
        for (const auto& region : regions) ranges.push_back({region.file, region.start, region.end, region.id});
        const auto weights = utilities::weighRanges(
            profile, ranges, [](const std::string& file) { return file.find("/tree/") != std::string::npos; });
        for (auto& region : regions) {
          const auto it = weights.byKey.find(region.id);
          if (it != weights.byKey.end()) region.samples = it->second;
        }
        profileSummary["attributed"] = weights.attributed;
        profileSummary["unattributed"] = weights.unattributed;
        auto top = std::vector<Region>(regions);
        std::sort(top.begin(), top.end(), [](const Region& a, const Region& b) { return a.samples > b.samples; });
        auto topJson = json::array();
        for (std::size_t i = 0; i < std::min<std::size_t>(40, top.size()) && top[i].samples > 0; ++i)
          topJson.push_back({{"id", top[i].id}, {"file", top[i].file}, {"label", top[i].label}, {"samples", top[i].samples}});
        profileSummary["top_regions"] = topJson;
      }
    }
  }
  writeFile(out / "profile.json", dumpJson(profileSummary, 2) + "\n");

  // ---- the loop -----------------------------------------------------------
  auto rng = std::mt19937{options.seed};
  const auto unit = [&] { return std::uniform_real_distribution<double>(0.0, 1.0)(rng); };
  const auto below = [&](std::size_t n) { return std::uniform_int_distribution<std::size_t>(0, n - 1)(rng); };
  constexpr auto exploitShare = double{0.25};

  auto population = std::vector<EvaluatedPatch>{};
  auto regionStats = std::map<int, RegionStats>{};
  auto indexOfRegion = std::map<int, std::size_t>{};
  for (std::size_t i = 0; i < regions.size(); ++i) indexOfRegion[regions[i].id] = i;

  auto calls = 0LL, promptTokens = 0LL, completionTokens = 0LL, totalTokens = 0LL;
  auto bestConfirmedRatio = double{1.0};
  auto bestConfirmedId = 0;
  auto bestRetainedRatio = double{1.0};
  auto stageCounts = std::map<std::string, int>{};
  auto confirmedCount = 0, improvedCount = 0;

  appendLine(out / "credits.csv",
             "generation,calls,prompt_tokens,completion_tokens,total_tokens,"
             "best_confirmed_speedup,best_retained_speedup,elapsed_s");

  struct Repair {
    bool active = false;
    std::size_t regionIndex = 0;
    EvaluatedPatch parent;
    std::string failure;
  } repair;

  const auto pickParent = [&]() -> EvaluatedPatch {
    if (bestOfN || population.empty()) return EvaluatedPatch{0, -1, 0, -1, "", 1.0, true, "baseline"};
    const auto& a = population[below(population.size())];
    const auto& b = population[below(population.size())];
    return a.score <= b.score ? a : b;
  };
  const auto pickRegion = [&]() -> std::size_t {
    if (!bestOfN && unit() < exploitShare) {
      auto best = std::size_t{regions.size()};
      auto gain = double{0.0};
      for (const auto& [id, stats] : regionStats)
        if (stats.bestGain > gain) { gain = stats.bestGain; best = indexOfRegion[id]; }
      if (best < regions.size()) return best;
    }
    auto totalSamples = 0LL;
    for (const auto& r : regions) totalSamples += r.samples;
    if (totalSamples > 0 && unit() >= options.uniformShare) {
      auto target = std::uniform_int_distribution<long long>(0, totalSamples - 1)(rng);
      for (std::size_t i = 0; i < regions.size(); ++i) {
        if (target < regions[i].samples) return i;
        target -= regions[i].samples;
      }
    }
    return below(regions.size());
  };

  const auto writeRegionsTried = [&] {
    auto tried = json::object();
    for (const auto& [id, s] : regionStats) {
      const auto& r = regions[indexOfRegion[id]];
      tried[std::to_string(id)] = {{"file", r.file}, {"label", r.label}, {"attempts", s.attempts},
                                   {"accepted", s.accepted}, {"best_gain", s.bestGain}};
    }
    writeFile(out / "regions_tried.json", dumpJson(tried, 2) + "\n");
  };
  const auto isRepairable = [](const std::string& stage) {
    static const std::set<std::string> repairable{"compile", "link", "correctness", "profile",
                                                  "load", "threading", "crash", "patch", "splice"};
    return repairable.count(stage) > 0;
  };

  auto endedBecause = std::string{"generations exhausted"};
  for (auto gen = 1; gen <= options.generations; ++gen) {
    if (gStop) { endedBecause = "signal"; break; }
    if (options.deadlineSeconds > 0.0 && elapsed() > options.deadlineSeconds) {
      endedBecause = "deadline";
      break;
    }

    auto parent = EvaluatedPatch{};
    auto regionIndex = std::size_t{0};
    auto failure = std::string{};
    const auto isRepair = repair.active;
    if (repair.active) {
      parent = repair.parent;
      regionIndex = repair.regionIndex;
      failure = repair.failure;
      repair.active = false;
    } else {
      parent = pickParent();
      regionIndex = pickRegion();
    }
    const auto& region = regions[regionIndex];
    ++regionStats[region.id].attempts;

    auto record = json{{"generation", gen}, {"id", gen}, {"parent", parent.id}, {"region", region.id},
                       {"file", region.file}, {"label", region.label}, {"mode", options.mode},
                       {"repair_attempt", isRepair}, {"parent_ratio", parent.score},
                       {"started", nowIso()}};
    auto stage = std::string{};
    auto errorText = std::string{};
    auto attemptedCode = std::string{};
    auto finished = false;

    const auto genName = "gen_" + std::to_string(gen);
    const auto patchPath = (out / "patches" / (genName + ".patch")).string();

    do {
      // show: the region's text under the parent patch (best-of-N: baseline).
      auto showArgs = std::vector<std::string>{"show", "--work", options.work, "--region",
                                               std::to_string(region.id), "--max-lines",
                                               std::to_string(options.maxLines)};
      if (!parent.patchPath.empty()) { showArgs.push_back("--patch"); showArgs.push_back(parent.patchPath); }
      const auto shown = runHarnessCommand(options, showArgs, 300);
      if (!shown.value("ok", false)) { stage = "show"; errorText = truncate(shown.value("error", dumpJson(shown)), 600); break; }
      const auto currentText = shown.value("text", std::string{});

      const auto prompt = userPrompt(region, currentText, bestOfN ? 1.0 : parent.score,
                                     bestOfN ? 1.0 : bestRetainedRatio, baselineMs, failure, options.promptHints);
      writeFile(out / "prompts" / (genName + ".user.txt"), prompt);

      const auto reply = requestModelReply(config, systemPrompt(), prompt);
      ++calls;
      promptTokens += reply.promptTokens;
      completionTokens += reply.completionTokens;
      totalTokens += reply.totalTokens;
      record["prompt_tokens"] = reply.promptTokens;
      record["completion_tokens"] = reply.completionTokens;
      writeFile(out / "patches" / (genName + ".repl"), reply.content);
      if (reply.content.empty()) { stage = "llm"; errorText = "model call returned nothing: " + reply.error; break; }

      auto code = std::string{}, includes = std::string{};
      splitReply(reply.content, &code, &includes);
      if (code.empty()) { stage = "llm"; errorText = "reply held no code block with a brace"; break; }
      attemptedCode = code;
      writeFile(out / "patches" / (genName + ".code.cpp"), code);
      writeFile(out / "patches" / (genName + ".inc"), includes);

      auto squash = [](std::string s) {
        s.erase(std::remove_if(s.begin(), s.end(), [](unsigned char c) { return std::isspace(c); }), s.end());
        return s;
      };
      if (squash(code) == squash(currentText)) { stage = "unchanged"; errorText = "replacement equals the current text"; break; }

      auto spliceArgs = std::vector<std::string>{"splice", "--work", options.work, "--region",
                                                 std::to_string(region.id), "--max-lines",
                                                 std::to_string(options.maxLines), "--replacement",
                                                 (out / "patches" / (genName + ".code.cpp")).string(),
                                                 "--out", patchPath};
      if (!parent.patchPath.empty()) { spliceArgs.push_back("--patch"); spliceArgs.push_back(parent.patchPath); }
      if (!includes.empty()) { spliceArgs.push_back("--includes"); spliceArgs.push_back((out / "patches" / (genName + ".inc")).string()); }
      const auto spliced = runHarnessCommand(options, spliceArgs, 300);
      if (!spliced.value("ok", false) || !fs::exists(patchPath)) {
        stage = "splice";
        errorText = truncate(spliced.value("error", dumpJson(spliced)), 600);
        break;
      }
      record["patch"] = patchPath;

      // first measurement, then a second one for anything that passed
      const auto m1 = measureOnce(options, patchPath, out / "measurements" / (genName + ".m1.json"));
      if (!m1.harnessOk || !m1.analysis.valid) { stage = m1.stage.empty() ? "unknown" : m1.stage; errorText = truncate(m1.error, 1500); break; }
      const auto needSecond = m1.analysis.faster || m1.analysis.unstable;
      auto m2 = Measured{};
      if (needSecond) m2 = measureOnce(options, patchPath, out / "measurements" / (genName + ".m2.json"));
      const auto secondOk = needSecond && m2.harnessOk && m2.analysis.valid;
      const auto& a1 = m1.analysis;
      const auto& a2 = m2.analysis;
      const auto confirmed = a1.faster && secondOk && a2.faster;
      const auto& kept = (secondOk && a2.ratio > a1.ratio) ? a2 : a1;  // the less flattering of two
      const auto keptRatio = kept.ratio;
      const auto improved = confirmed && keptRatio < parent.score;
      const auto ratioVsParent = keptRatio / parent.score;

      record["ok"] = true;
      record["stage"] = "";
      record["score_ms"] = kept.candidateMs;
      record["reference_ms"] = kept.referenceMs;
      record["ratio"] = keptRatio;
      record["speedup"] = 1.0 / keptRatio;
      record["p_value"] = a1.pValue;
      record["confirmed_p"] = secondOk ? json(a2.pValue) : json(-1);
      record["ratio_1"] = a1.ratio;
      record["ratio_2"] = secondOk ? json(a2.ratio) : json(nullptr);
      record["significant"] = a1.ratio < 1.0 && a1.pValue < options.alpha && secondOk && a2.ratio < 1.0 && a2.pValue < options.alpha;
      record["significant_at_min_effect"] = confirmed;
      record["confirmed"] = confirmed;
      record["min_effect"] = options.minEffect;
      record["unstable"] = a1.unstable || (secondOk && a2.unstable);
      record["improved_on_parent"] = improved;
      record["ratio_vs_parent"] = ratioVsParent;
      record["incremental_gain_at_min_effect"] = improved && ratioVsParent <= 1.0 - options.minEffect;
      record["ratio_spread"] = kept.spread;
      record["candidate_cv"] = kept.candidateCv;
      record["swapped_processes"] = kept.swapped;
      record["autocorr_lag1_median"] = a1.acMedian;
      record["rule_reason_1"] = a1.reason;
      record["rule_reason_2"] = secondOk ? json(a2.reason) : json(nullptr);
      auto note = std::string{};
      if (needSecond && !secondOk) note = "second measurement failed at stage '" + m2.stage + "': " + truncate(m2.error, 300);
      record["note"] = note;
      if (confirmed) ++confirmedCount;
      if (improved) {
        ++improvedCount;
        ++regionStats[region.id].accepted;
        regionStats[region.id].bestGain = std::max(regionStats[region.id].bestGain, parent.score - keptRatio);
      }

      auto entry = EvaluatedPatch{};
      entry.id = gen; entry.parent = parent.id; entry.generation = gen; entry.region = region.id;
      entry.patchPath = patchPath; entry.score = keptRatio; entry.valid = true;
      entry.significant = record["significant"].get<bool>(); entry.significantAtMinEffect = confirmed;
      population.push_back(entry);
      std::stable_sort(population.begin(), population.end(),
                       [](const EvaluatedPatch& x, const EvaluatedPatch& y) { return x.score < y.score; });
      if (!bestOfN && static_cast<int>(population.size()) > options.population) population.pop_back();
      bestRetainedRatio = std::min(bestRetainedRatio, keptRatio);
      if (confirmed && keptRatio < bestConfirmedRatio) {
        bestConfirmedRatio = keptRatio;
        bestConfirmedId = gen;
        fs::copy_file(patchPath, out / "best.patch", fs::copy_options::overwrite_existing);
      }
      finished = true;
    } while (false);

    if (!finished) {
      record["ok"] = false;
      record["stage"] = stage;
      record["error"] = errorText;
      record["note"] = errorText;
      if (!bestOfN && !isRepair && isRepairable(stage) && !attemptedCode.empty()) {
        repair.active = true;
        repair.regionIndex = regionIndex;
        repair.parent = parent;
        repair.failure = "Stage '" + stage + "' rejected it: " + truncate(errorText, 1500) +
                         "\nThe rejected replacement was:\n```cpp\n" + truncate(attemptedCode, 3000) + "\n```";
      }
    }
    ++stageCounts[finished ? "measured" : stage];
    record["finished"] = nowIso();
    record["elapsed_s"] = elapsed();
    appendLine(out / "results.jsonl", dumpJson(record));
    {
      auto row = std::ostringstream{};
      row << gen << "," << calls << "," << promptTokens << "," << completionTokens << "," << totalTokens
          << "," << std::setprecision(6) << 1.0 / bestConfirmedRatio << "," << 1.0 / bestRetainedRatio
          << "," << std::setprecision(1) << std::fixed << elapsed();
      appendLine(out / "credits.csv", row.str());
    }
    writeRegionsTried();
    std::cerr << "[gen " << gen << "/" << options.generations << "] region " << region.id << " "
              << region.label << " parent=" << parent.id << " "
              << (finished ? "ratio=" + std::to_string(record["ratio"].get<double>()) +
                                 (record["confirmed"].get<bool>() ? " CONFIRMED" : "")
                           : "stage=" + stage)
              << " best_confirmed_speedup=" << 1.0 / bestConfirmedRatio << " tokens=" << totalTokens
              << " t=" << static_cast<int>(elapsed()) << "s\n";
  }

  auto summary = json{{"finished", nowIso()},
                      {"ended_because", endedBecause},
                      {"mode", options.mode},
                      {"seed", options.seed},
                      {"api_calls", calls},
                      {"prompt_tokens", promptTokens},
                      {"completion_tokens", completionTokens},
                      {"total_tokens", totalTokens},
                      {"best_confirmed_speedup", 1.0 / bestConfirmedRatio},
                      {"best_confirmed_generation", bestConfirmedId},
                      {"best_retained_speedup", 1.0 / bestRetainedRatio},
                      {"confirmed_candidates", confirmedCount},
                      {"improved_on_parent_candidates", improvedCount},
                      {"outcomes", stageCounts},
                      {"elapsed_s", elapsed()}};
  writeFile(out / "summary.json", dumpJson(summary, 2) + "\n");
  std::cerr << "[done] " << dumpJson(summary) << "\n";
  return 0;
}
