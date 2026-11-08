// Follow-up 4b driver: decode FIT files with the SDK built under a sanitizer, optionally from several threads at once.
//   driver single DIR...        decode every .fit file under the given corpus directories once; print one line per file
//   driver threads T R DIR...   T threads each decode every file R times concurrently; compare each digest with a single-thread reference
// The listener folds decoded values exactly like src/workloads/SdkDecode.cpp (it is a copy of that logic) so the digests are comparable.
// Exceptions thrown by the SDK on hostile input are caught and reported as "exception", not as crashes.
#include <algorithm>
#include <atomic>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

#include "utilities/Portability.hpp"
using utilities::Digest;
#include "fit_decode.hpp"
#include "fit_developer_field.hpp"
#include "fit_mesg.hpp"
#include "fit_mesg_listener.hpp"
#include "fit_profile.hpp"

namespace {
class Listener : public fit::MesgListener {
 public:
  Digest digest;
  uint64_t messages = 0, fields = 0;
  void OnMesg(fit::Mesg& message) override {
    ++messages;
    digest.foldBits(message.GetNum());
    digest.foldBits(static_cast<uint64_t>(message.GetNumFields()));
    for (auto i = FIT_UINT16{0}; i < static_cast<FIT_UINT16>(message.GetNumFields()); ++i) {
      const auto field = message.GetFieldByIndex(i);
      if (field == nullptr) digest.foldByte(0xFE);
      else { ++fields; fold(*field); }
    }
    for (const fit::DeveloperField& f : message.GetDeveloperFields()) { ++fields; fold(f); }
  }
 private:
  void fold(const fit::FieldBase& field) {
    digest.foldBits(field.GetNum());
    digest.foldBits(field.GetType());
    const auto count = FIT_UINT8{field.GetNumValues()};
    digest.foldBits(count);
    if (!field.IsValid()) { digest.foldByte(0xFD); return; }
    for (auto v = FIT_UINT8{0}; v < count; ++v) {
      if (field.GetType() == FIT_BASE_TYPE_STRING) {
        const auto s = FIT_WSTRING{field.GetSTRINGValue(v)};
        for (wchar_t c : s) digest.foldBits(static_cast<uint64_t>(c));
        digest.foldByte(0x00);
      } else {
        digest.foldDouble(field.GetFLOAT64Value(v));
      }
    }
  }
};

struct Outcome { uint64_t digest = 0, messages = 0, fields = 0; int status = 0; std::string what; };  // 0 ok, 1 decode returned false, 2 exception

Outcome decodeOne(const std::string& bytes) {
  Outcome o;
  try {
    Listener listener;
    std::istringstream stream(bytes, std::ios::binary);
    fit::Decode decode;
    if (!decode.Read(stream, listener)) o.status = 1;
    o.digest = listener.digest.hash; o.messages = listener.messages; o.fields = listener.fields;
  } catch (const std::exception& e) { o.status = 2; o.what = e.what(); } catch (...) { o.status = 2; o.what = "non-std exception"; }
  return o;
}

std::vector<std::pair<std::string, std::string>> load(const std::vector<std::string>& dirs) {
  std::vector<std::pair<std::string, std::string>> files;
  for (const auto& d : dirs)
    for (const auto& e : std::filesystem::recursive_directory_iterator(d, std::filesystem::directory_options::follow_directory_symlink))
      if (e.is_regular_file() && e.path().extension() == ".fit") {
        std::ifstream f(e.path(), std::ios::binary); std::ostringstream s; s << f.rdbuf();
        files.emplace_back(e.path().string(), s.str());
      }
  std::sort(files.begin(), files.end());
  return files;
}
}  // namespace

int main(int argc, char** argv) {
  if (argc < 3) { std::cerr << "usage: driver single DIR... | driver threads T R DIR...\n"; return 2; }
  const std::string mode = argv[1];
  if (mode == "classify") {   // one line per file: path, status (0 ok, 1 Decode::Read returned false, 2 exception) and the exception text
    const auto files = load({argv + 2, argv + argc});
    for (const auto& [name, bytes] : files) {
      const auto o = decodeOne(bytes);
      std::cout << name << " " << o.status << " " << o.messages << " " << o.what << "\n";
    }
    return 0;
  }
  if (mode == "single") {
    const auto files = load({argv + 2, argv + argc});
    for (const auto& [name, bytes] : files) {
      const auto o = decodeOne(bytes);
      std::cout << name << " " << o.status << " " << o.digest << " " << o.messages << " " << o.fields << "\n";
    }
    return 0;
  }
  const int T = std::stoi(argv[2]), R = std::stoi(argv[3]);
  const auto files = load({argv + 4, argv + argc});
  // Cold start on purpose: the concurrent phase runs BEFORE any single-thread decode, so lazily built tables and caches inside the SDK are
  // first touched by several threads at once (a race there is exactly what ThreadSanitizer should see). The reference digests are computed afterwards.
  std::vector<std::vector<Outcome>> got(T, std::vector<Outcome>(files.size() * R));
  std::atomic<bool> go{false};
  std::vector<std::thread> pool;
  for (int t = 0; t < T; ++t)
    pool.emplace_back([&, t] {
      while (!go.load()) {}
      for (int r = 0; r < R; ++r)
        for (size_t i = 0; i < files.size(); ++i) got[t][r * files.size() + i] = decodeOne(files[i].second);
    });
  go.store(true);
  for (auto& th : pool) th.join();
  long mismatches = 0;
  for (size_t i = 0; i < files.size(); ++i) {
    const auto expect = decodeOne(files[i].second);
    for (int t = 0; t < T; ++t)
      for (int r = 0; r < R; ++r) {
        const auto& o = got[t][r * files.size() + i];
        if (o.digest != expect.digest || o.status != expect.status || o.messages != expect.messages) ++mismatches;
      }
  }
  std::cout << "threads " << T << " repeats " << R << " files " << files.size() << " digest_mismatches " << mismatches << "\n";
  return 0;
}
