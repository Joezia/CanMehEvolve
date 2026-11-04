# Final patches of each run (cumulative against stock)

Each file is the run's **fixed final patch** as one diff against stock SDK 21.201.0 (apply one of them to stock with `git apply`; never several). Speedups are the median of three independent re-measurements (`runs/<run>/evaluate-best/summary.json`). The submitted, step-by-step explained series is the median-seed greedy chain (`patches/` at the repository root); the other chains are experiment records (`experiments/patches/greedy-s*-unexplained/`, provenance-only messages). The descriptions below were written from reading the diffs; none is verified by profiling.

| run | final patch | speedup (re-measured) | functions changed (accepted search steps) | sha256 of patch |
|---|---|---|---|---|
| bestofn seed 1 | `bestofn-seed1.cumulative-vs-stock.patch` | 1.073 | `Profile::GetMesg` | `ecac84bf885f0ea6` |
| bestofn seed 2 | `bestofn-seed2.cumulative-vs-stock.patch` | 1.069 | `Profile::GetMesg` | `53f139e844bfde3d` |
| bestofn seed 3 | `bestofn-seed3.cumulative-vs-stock.patch` | 1.074 | `Profile::GetMesg` | `676ed55f35c5da40` |
| bestofn seed 4 | `bestofn-seed4.cumulative-vs-stock.patch` | 1.073 | `Profile::GetMesg` | `a1550b3f307baee2` |
| bestofn seed 5 | `bestofn-seed5.cumulative-vs-stock.patch` | 1.067 | `Profile::GetMesg` | `a9427cb7489ea1e7` |
| greedy seed 1 | `greedy-seed1.cumulative-vs-stock.patch` | 1.157 | `Mesg::GetActiveSubFieldIndexByFieldIndex`, `Profile::GetMesg`, `FieldBase::FieldBase`, `Mesg::GetField`, `Field::Field`, `FieldBase::SetUINT64ZValue`, `Field::GetNum`, `FieldBase::GetValue` | `9290ba30cb15b35f` |
| greedy seed 2 | `greedy-seed2.cumulative-vs-stock.patch` | 1.216 | `Profile::GetMesg`, `FieldBase::FieldBase`, `FieldBase::GetValue`, `Mesg::AddField`, `Field::GetNum`, `Profile::GetFieldIndex`, `Decode::Resume`, `FieldBase::GetNumValues` | `4530da515a6d5dcc` |
| greedy seed 3 | `greedy-seed3.cumulative-vs-stock.patch` | 1.169 | `MesgBroadcaster::RemoveListener`, `Decode::Resume`, `Profile::GetFieldIndex`, `FieldBase::FieldBase`, `Profile::GetMesg`, `Field::GetType`, `CRC::Get16`, `Mesg::AddField`, `MesgDefinition::GetFieldByIndex`, `FieldBase::GetValue`, `Field::GetNumSubFields` | `e890e2230c8b23c8` |
| greedy seed 4 | `greedy-seed4.cumulative-vs-stock.patch` | 1.191 | `Profile::GetMesg`, `Mesg::GetField`, `FieldBase::Read`, `Profile::GetFieldIndex`, `FieldBase::FieldBase`, `CRC::Get16`, `FieldDefinition::GetNum` | `6e52bf6bf6d29d3d` |
| greedy seed 5 | `greedy-seed5.cumulative-vs-stock.patch` | 1.165 | `FieldBase::FieldBase`, `Profile::GetFieldIndex`, `Profile::GetMesg`, `FieldBase::GetValue`, `FieldBase::GetFLOAT64Value` | `ed16819b10d897ce` |

## What each changed function does (idea; implementations differ between chains, see the incremental patches)

| function | change | why it might be faster / caveat |
|---|---|---|
| `CRC::Get16` | byte-wise 256-entry table instead of two 16-entry nibble steps | half the table lookups per byte |
| `Decode::Resume` | keeps byte index and offset in locals inside the per-byte loop | avoids reloading and storing members every byte |
| `Field::Field` | constructor from (message number, field number) answers profile lookups from small static caches | avoids repeated profile lookups; unsynchronised statics |
| `Field::GetNum` | loads `profile` and `profileIndex` into locals and reorders the checks | tiny; likely within noise |
| `Field::GetNumSubFields` | branch hints on the null/range checks | probably marginal; within noise |
| `Field::GetType` | single-return form | probably none; within noise |
| `FieldBase::FieldBase` | copy constructor copies `values` and `stringIndexes` in the member-initialiser list instead of default-constructing then assigning | avoids two default constructions and assignments for every copied field |
| `FieldBase::GetFLOAT64Value` | rewrites the type switch to read values directly with invalid checks instead of `ConvertBaseType` (uses `goto`) | skips generic conversion; semantic equivalence beyond the harness checks is unverified |
| `FieldBase::GetNumValues` | divides by the element size with a shift table instead of a division | avoids an integer division per call; assumes power-of-two element sizes |
| `FieldBase::GetValue` | reads 1/2/4/8-byte values with one `memcpy` instead of assembling bytes in a loop | one load instead of several shift/or steps per value; assumes a little-endian host |
| `FieldBase::Read` | restructures the field read (string and numeric cases) with `memcpy` and fewer repeated lookups | less work per byte when decoding field data |
| `FieldBase::SetUINT64ZValue` | adds `__attribute__((flatten))` | compiler hint to inline callees; effect is a guess |
| `FieldDefinition::GetNum` | adds `__attribute__((pure))` | compiler hint; effect is a guess |
| `Mesg::AddField` | scans existing fields directly instead of calling `GetField` | one call and pointer return less per added field |
| `Mesg::GetActiveSubFieldIndexByFieldIndex` | caches referenced-field lookups across sub-fields | avoids repeated `GetField`/`GetFLOAT64Value` for sub-fields sharing a reference field |
| `Mesg::GetField` | scans the field vector four elements at a time through a raw pointer | fewer loop-control steps per lookup |
| `MesgBroadcaster::RemoveListener` | hand-written erase instead of `std::find` + `erase` | not on the decode path; likely noise |
| `MesgDefinition::GetFieldByIndex` | raw data pointer and branch hint | tiny; within noise |
| `Profile::GetFieldIndex` | answers field-number lookups from a cached or precomputed table instead of scanning `mesg->fields` | called per field; the scan becomes a bit test / array read; the cached variant keeps unsynchronised statics |
| `Profile::GetMesg` | replaces the linear scan over all message types by a table indexed by message number (65,536 entries or a smaller guarded table) | it runs for every message and field of the decode, so one array read replaces a scan; the table is built lazily (plain `bool` flag in most winners: not thread-safe) |
