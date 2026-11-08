// Round 2: legal FIT files written by the ORIGINAL SDK encoder (fit::Encode), for correctness testing of patched libraries.
// Each file starts with a file_id message, then carries messages of up to 12 message types drawn from the SDK profile, each with a random subset of that
// message's fields set through the SDK's own typed setters (all base types, strings, short arrays). Nothing is mutated after encoding, so every file is a
// file the SDK's encoder produced; the generator is deterministic in (seed).
//   gen_valid_fit OUTDIR N [first_seed]     writes OUTDIR/valid_<seed>.fit
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <random>
#include <string>
#include <vector>

#include "fit_encode.hpp"
#include "fit_field.hpp"
#include "fit_file_id_mesg.hpp"
#include "fit_mesg.hpp"
#include "fit_profile.hpp"

namespace {
void setValue(fit::Field& f, std::mt19937& rng, FIT_UINT8 idx) {
  const auto r = static_cast<unsigned>(rng());
  switch (f.GetType() & FIT_BASE_TYPE_NUM_MASK) {
    case 0: f.SetENUMValue(static_cast<FIT_ENUM>(r % 6), idx); break;
    case 1: f.SetSINT8Value(static_cast<FIT_SINT8>(static_cast<int>(r % 200) - 100), idx); break;
    case 2: f.SetUINT8Value(static_cast<FIT_UINT8>(r % 250), idx); break;
    case 3: f.SetSINT16Value(static_cast<FIT_SINT16>(static_cast<int>(r % 60000) - 30000), idx); break;
    case 4: f.SetUINT16Value(static_cast<FIT_UINT16>(r % 65000), idx); break;
    case 5: f.SetSINT32Value(static_cast<FIT_SINT32>(r) / 3, idx); break;
    case 6: f.SetUINT32Value(r % 4000000000u, idx); break;
    case 7: { std::wstring s = L"s" + std::to_wstring(r % 1000); f.SetSTRINGValue(s, idx); break; }
    case 8: f.SetFLOAT32Value(static_cast<FIT_FLOAT32>(r % 10000) / 10.0f, idx); break;
    case 9: f.SetFLOAT64Value(static_cast<FIT_FLOAT64>(r % 100000) / 7.0, idx); break;
    case 10: f.SetUINT8ZValue(static_cast<FIT_UINT8Z>(1 + r % 250), idx); break;
    case 11: f.SetUINT16ZValue(static_cast<FIT_UINT16Z>(1 + r % 65000), idx); break;
    case 12: f.SetUINT32ZValue(1 + r % 4000000000u, idx); break;
    case 13: f.SetBYTEValue(static_cast<FIT_BYTE>(r % 250), idx); break;
    case 14: f.SetSINT64Value(static_cast<FIT_SINT64>(r) * 1000003LL, idx); break;
    case 15: f.SetUINT64Value(static_cast<FIT_UINT64>(r) * 1000003ULL, idx); break;
    case 16: f.SetUINT64ZValue(1 + static_cast<FIT_UINT64Z>(r) * 1000003ULL, idx); break;
    default: break;
  }
}
}  // namespace

int main(int argc, char** argv) {
  if (argc < 3) { std::cerr << "usage: gen_valid_fit OUTDIR N [first_seed]\n"; return 2; }
  const std::string dir = argv[1];
  const int n = std::atoi(argv[2]);
  const unsigned first = argc > 3 ? static_cast<unsigned>(std::atoi(argv[3])) : 1;
  std::vector<int> usable;
  for (int i = 0; i < static_cast<int>(fit::Profile::MESGS); ++i)
    if (fit::Profile::mesgs[i].num != FIT_MESG_NUM_FILE_ID && fit::Profile::mesgs[i].numFields > 0) usable.push_back(i);
  for (int k = 0; k < n; ++k) {
    const unsigned seed = first + static_cast<unsigned>(k);
    std::mt19937 rng(seed * 2654435761u);
    const std::string path = dir + "/valid_" + std::to_string(seed) + ".fit";
    std::fstream file(path, std::ios::in | std::ios::out | std::ios::binary | std::ios::trunc);
    if (!file.is_open()) { std::cerr << "cannot open " << path << "\n"; return 1; }
    fit::Encode encode(fit::ProtocolVersion::V20);
    encode.Open(file);
    fit::FileIdMesg fileId;
    fileId.SetType(FIT_FILE_ACTIVITY);
    fileId.SetManufacturer(FIT_MANUFACTURER_DEVELOPMENT);
    fileId.SetProduct(1 + seed % 100);
    fileId.SetTimeCreated(1000000000u + seed);
    fileId.SetSerialNumber(4000 + seed);
    encode.Write(fileId);
    std::vector<int> chosen;
    const int types = 3 + static_cast<int>(rng() % 10);
    for (int t = 0; t < types; ++t) chosen.push_back(usable[rng() % usable.size()]);
    const int messages = 30 + static_cast<int>(rng() % 120);
    for (int m = 0; m < messages; ++m) {
      const auto& def = fit::Profile::mesgs[chosen[rng() % chosen.size()]];
      fit::Mesg mesg(def.num);
      const int nf = 1 + static_cast<int>(rng() % std::min<unsigned>(def.numFields, 12));
      for (int j = 0; j < nf; ++j) {
        const auto& fd = def.fields[rng() % def.numFields];
        fit::Field field(def.num, fd.num);
        const int len = 1 + static_cast<int>(rng() % 3);
        for (int a = 0; a < len; ++a) setValue(field, rng, static_cast<FIT_UINT8>(a));
        mesg.AddField(field);
      }
      encode.Write(mesg);
    }
    if (!encode.Close()) { std::cerr << "encode.Close failed for seed " << seed << "\n"; return 1; }
    file.close();
  }
  return 0;
}
