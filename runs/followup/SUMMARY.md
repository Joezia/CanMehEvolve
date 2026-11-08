# Follow-up experiments (raw results; interpretation pending)

## 1. Greedy seeds 3-5 completed to 40 HTTP requests

| seed | original requests | extra requests | tokens added | updates in continuation | original final speedup | final speedup after continuation (3 re-measurements) | node (orig -> cont.) | state |
|---|---|---|---|---|---|---|---|---|
| 3 | 38 | 2 | 10114 | 1 | 1.1687 | 1.1758 (pass 3/3) | xcnd1 -> xcnd2 | finished |
| 4 | 34 | 6 | 111963 | 0 | 1.1910 | 1.1919 (pass 3/3) | xcnd2 -> xcnd4 | finished |
| 5 | 34 | 6 | 100736 | 0 | 1.1652 | 1.1661 (pass 3/3) | xcnd3 -> xcnd5 | finished |

## 2. False-accept rate of the frozen rule on the real SDK decode (inert patch)

| family | jobs | measurements | judged faster | 95% CI of rate | median ratio [min, max] | unstable | median p |
|---|---|---|---|---|---|---|---|
| xcnc | 2 | 120 | 0 | 0.0% (0.0%-3.0%) | 1.00000 [0.99774, 1.00185] | 0 | 0.561 |
| xcnd | 2 | 120 | 0 | 0.0% (0.0%-3.0%) | 0.99989 [0.99782, 1.00212] | 0 | 0.538 |

## 3. Null search: the greedy rank rule on no-op candidates (true ratio 1.000)

| family | seed | steps | updates | final record (speedup) | updates at steps | first-measurement rule 'faster' | state |
|---|---|---|---|---|---|---|---|
| xcnc | 1 | 36 | 3 | 0.99918 (1.0008) | [2, 21, 23] | 0 | finished |
| xcnc | 2 | 36 | 3 | 0.99923 (1.0008) | [1, 9, 31] | 0 | finished |
| xcnc | 3 | 36 | 3 | 0.99929 (1.0007) | [1, 5, 18] | 0 | finished |
| xcnc | 4 | 36 | 4 | 0.99926 (1.0007) | [5, 11, 17, 19] | 0 | finished |
| xcnd | 1 | 36 | 3 | 0.99914 (1.0009) | [2, 8, 16] | 0 | finished |
| xcnd | 2 | 36 | 2 | 0.99891 (1.0011) | [2, 18] | 0 | finished |
| xcnd | 3 | 36 | 4 | 0.99938 (1.0006) | [5, 11, 30, 31] | 0 | finished |
| xcnd | 4 | 36 | 2 | 0.99915 (1.0009) | [2, 8] | 0 | finished |

xcnc: updates per run median 3.0 (range 3-4); final record speedup median 1.0008 (range 1.0007-1.0008).

xcnd: updates per run median 2.5 (range 2-4); final record speedup median 1.0009 (range 1.0006-1.0011).

## 6. Stacking best-of-N's own single-function candidates (cumulative patches, 3 independent re-measurements each)

**seed 1** (best-of-N final 1.0730; greedy final 1.1574): K=1 +Profile::GetMesg: 1.0728; K=2 +FieldBase::FieldBase: 1.1304; K=3 +Profile::GetFieldIndex: 1.1427; K=4 +FieldBase::GetValue: 1.1467; K=5 +Field::Field: 1.1421; K=6 +Mesg::GetField: 1.1481; K=7 +Field::GetNum: 1.1523; K=8 +Field::GetOffset: 1.1496; K=9 +FieldBase::GetFLOAT64Value: 1.1632; K=10 +MesgBroadcaster::RemoveListener: 1.1588; K=11 +Mesg::GetNum: 1.1557
**seed 2** (best-of-N final 1.0688; greedy final 1.2155): K=1 +Profile::GetMesg: 1.0692; K=2 +FieldBase::FieldBase: 1.1217; K=3 +Profile::GetFieldIndex: 1.1358; K=4 +FieldBase::GetNumValues: 1.1778; K=5 +FieldBase::GetValue: 1.1922; K=6 +Field::GetNum: 1.1977; K=7 +Mesg::GetFieldByIndex: 1.1961; K=8 +Mesg::GetActiveSubFieldIndexByFieldIndex: 1.1965; K=9 +Field::GetNumSubFields: 1.1966; K=10 +Field::GetScale: 1.1924
**seed 3** (best-of-N final 1.0740; greedy final 1.1687): K=1 +Profile::GetMesg: 1.0740; K=2 +FieldBase::FieldBase: 1.1272; K=3 +FieldBase::GetValue: 1.1363; K=4 +Mesg::GetField: 1.1467; K=5 +Mesg::AddField: 1.1464; K=6 +Decode::Resume: 1.1517; K=7 +FieldBase::GetFLOAT64Value: 1.1491; K=8 +Field::Field: 1.1539; K=9 +MesgBroadcaster::RemoveListener: 1.1576; K=10 +IsTimestampValid: 1.1579; K=11 +IsFavoriteValid: 1.1566; K=12 +Field::GetNumSubFields: 1.1574
**seed 4** (best-of-N final 1.0725; greedy final 1.1910): K=1 +Profile::GetMesg: 1.0735; K=2 +FieldBase::FieldBase: 1.1310; K=3 +Profile::GetFieldIndex: 1.1499; K=4 +FieldBase::Read: 1.1642; K=5 +Mesg::GetActiveSubFieldIndex: 1.1578; K=6 +Mesg::GetField: 1.1759; K=7 +Field::Field: 1.1870; K=8 +Field::GetNum: 1.1771; K=9 +DeveloperFieldDefinition::IsDefined: 1.1759; K=10 +Field::GetComponent: 1.1776; K=11 +IsIdValid: 1.1753; K=12 +Field::GetScale: 1.1769
**seed 5** (best-of-N final 1.0667; greedy final 1.1652): K=1 +Profile::GetMesg: 1.0671; K=2 +FieldBase::FieldBase: 1.1167; K=3 +Profile::GetFieldIndex: 1.1462; K=4 +Mesg::AddField: 1.1547; K=5 +FieldBase::GetNumValues: 1.1880; K=6 +FieldBase::Read: 1.2095; K=7 +Field::GetNum: 1.2073; K=8 +Decode::Resume: 1.2086; K=9 +DeveloperFieldDefinition::IsDefined: 1.2080; K=10 +Field::IsValid: 1.2091; K=11 +Field::GetNumSubFields: 1.2093

## 4. Correctness

### 4a. Differential test vs stock on mutated FIT files

| variant | compared | identical | differences | crash in both (same hostile input) | crash only in candidate | crash only in stock |
|---|---|---|---|---|---|---|
| final-bestofn-seed1 | 227 | 227 | 0 | 177 | 0 | 0 |
| final-bestofn-seed2 | 227 | 227 | 0 | 177 | 0 | 0 |
| final-bestofn-seed3 | 227 | 227 | 0 | 177 | 0 | 0 |
| final-bestofn-seed4 | 227 | 227 | 0 | 177 | 0 | 0 |
| final-bestofn-seed5 | 227 | 227 | 0 | 177 | 0 | 0 |
| final-greedy-seed1 | 216 | 216 | 0 | 177 | 11 | 0 |
| final-greedy-seed2 | 227 | 227 | 0 | 177 | 0 | 0 |
| final-greedy-seed3 | 227 | 227 | 0 | 177 | 0 | 0 |
| final-greedy-seed4 | 227 | 223 | 4 | 177 | 0 | 0 |
| final-greedy-seed5 | 227 | 227 | 0 | 177 | 0 | 0 |
| human-attempt-1 | 227 | 227 | 0 | 177 | 0 | 0 |
| human-attempt-2 | 227 | 227 | 0 | 177 | 0 | 0 |
| s3-step01-gen6 | 227 | 227 | 0 | 177 | 0 | 0 |
| s3-step02-gen11 | 227 | 227 | 0 | 177 | 0 | 0 |
| s3-step03-gen12 | 227 | 227 | 0 | 177 | 0 | 0 |
| s3-step04-gen13 | 227 | 227 | 0 | 177 | 0 | 0 |
| s3-step05-gen17 | 227 | 227 | 0 | 177 | 0 | 0 |
| s3-step06-gen18 | 227 | 227 | 0 | 177 | 0 | 0 |
| s3-step07-gen20 | 227 | 227 | 0 | 177 | 0 | 0 |
| s3-step08-gen21 | 227 | 227 | 0 | 177 | 0 | 0 |
| s3-step09-gen28 | 227 | 227 | 0 | 177 | 0 | 0 |
| s3-step10-gen31 | 227 | 227 | 0 | 177 | 0 | 0 |
| s3-step11-gen34 | 227 | 227 | 0 | 177 | 0 | 0 |

### 4b. Sanitizers

| variant | config | result |
|---|---|---|
| final-bestofn-seed1 | asan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 1, "tsan_warnings": 0, "files": 71, "digest_differences_vs_stock": 0} |
| final-bestofn-seed1 | tsan | {"returncode": 66, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 2, "output": "threads 4 repeats 1 files 12 digest_mismatches 0"} |
| final-bestofn-seed2 | asan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 1, "tsan_warnings": 0, "files": 71, "digest_differences_vs_stock": 0} |
| final-bestofn-seed2 | tsan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 0, "output": "threads 4 repeats 1 files 12 digest_mismatches 0"} |
| final-bestofn-seed3 | asan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 1, "tsan_warnings": 0, "files": 71, "digest_differences_vs_stock": 0} |
| final-bestofn-seed3 | tsan | {"returncode": 66, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 2, "output": "threads 4 repeats 1 files 12 digest_mismatches 0"} |
| final-bestofn-seed4 | asan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 1, "tsan_warnings": 0, "files": 71, "digest_differences_vs_stock": 0} |
| final-bestofn-seed4 | tsan | {"returncode": 66, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 2, "output": "threads 4 repeats 1 files 12 digest_mismatches 0"} |
| final-bestofn-seed5 | asan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 1, "tsan_warnings": 0, "files": 71, "digest_differences_vs_stock": 0} |
| final-bestofn-seed5 | tsan | {"returncode": 66, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 2, "output": "threads 4 repeats 1 files 12 digest_mismatches 0"} |
| final-greedy-seed1 | asan | {"returncode": 1, "asan_errors": 1, "ubsan_runtime_errors": 2, "tsan_warnings": 0, "files": 0, "digest_differences_vs_stock": 0} |
| final-greedy-seed1 | tsan | {"returncode": 66, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 14, "output": ""} |
| final-greedy-seed2 | asan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 0, "files": 71, "digest_differences_vs_stock": 0} |
| final-greedy-seed2 | tsan | {"returncode": 66, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 7, "output": "threads 4 repeats 1 files 12 digest_mismatches 0"} |
| final-greedy-seed3 | asan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 0, "files": 71, "digest_differences_vs_stock": 0} |
| final-greedy-seed3 | tsan | {"returncode": 66, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 32, "output": ""} |
| final-greedy-seed4 | asan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 1, "tsan_warnings": 0, "files": 71, "digest_differences_vs_stock": 1} |
| final-greedy-seed4 | tsan | {"returncode": 66, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 6, "output": "threads 4 repeats 1 files 12 digest_mismatches 0"} |
| final-greedy-seed5 | asan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 0, "files": 71, "digest_differences_vs_stock": 0} |
| final-greedy-seed5 | tsan | {"returncode": 66, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 11, "output": "threads 4 repeats 1 files 12 digest_mismatches 0"} |
| human-attempt-1 | asan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 1, "tsan_warnings": 0, "files": 71, "digest_differences_vs_stock": 0} |
| human-attempt-1 | tsan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 0, "output": "threads 4 repeats 1 files 12 digest_mismatches 0"} |
| human-attempt-2 | asan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 1, "tsan_warnings": 0, "files": 71, "digest_differences_vs_stock": 0} |
| human-attempt-2 | tsan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 0, "output": "threads 4 repeats 1 files 12 digest_mismatches 0"} |
| s3-step01-gen6 | asan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 1, "tsan_warnings": 0, "files": 71, "digest_differences_vs_stock": 0} |
| s3-step01-gen6 | tsan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 0, "output": "threads 4 repeats 1 files 12 digest_mismatches 0"} |
| s3-step02-gen11 | asan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 1, "tsan_warnings": 0, "files": 71, "digest_differences_vs_stock": 0} |
| s3-step02-gen11 | tsan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 0, "output": "threads 4 repeats 1 files 12 digest_mismatches 0"} |
| s3-step03-gen12 | asan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 1, "tsan_warnings": 0, "files": 71, "digest_differences_vs_stock": 0} |
| s3-step03-gen12 | tsan | {"returncode": 66, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 37, "output": "threads 4 repeats 1 files 12 digest_mismatches 36"} |
| s3-step04-gen13 | asan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 1, "tsan_warnings": 0, "files": 71, "digest_differences_vs_stock": 0} |
| s3-step04-gen13 | tsan | {"returncode": 66, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 36, "output": "threads 4 repeats 1 files 12 digest_mismatches 38"} |
| s3-step05-gen17 | asan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 1, "tsan_warnings": 0, "files": 71, "digest_differences_vs_stock": 0} |
| s3-step05-gen17 | tsan | {"returncode": 66, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 39, "output": ""} |
| s3-step06-gen18 | asan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 1, "tsan_warnings": 0, "files": 71, "digest_differences_vs_stock": 0} |
| s3-step06-gen18 | tsan | {"returncode": 66, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 34, "output": ""} |
| s3-step07-gen20 | asan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 1, "tsan_warnings": 0, "files": 71, "digest_differences_vs_stock": 0} |
| s3-step07-gen20 | tsan | {"returncode": 66, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 39, "output": ""} |
| s3-step08-gen21 | asan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 1, "tsan_warnings": 0, "files": 71, "digest_differences_vs_stock": 0} |
| s3-step08-gen21 | tsan | {"returncode": 66, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 41, "output": "threads 4 repeats 1 files 12 digest_mismatches 39"} |
| s3-step09-gen28 | asan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 1, "tsan_warnings": 0, "files": 71, "digest_differences_vs_stock": 0} |
| s3-step09-gen28 | tsan | {"returncode": 66, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 38, "output": "threads 4 repeats 1 files 12 digest_mismatches 39"} |
| s3-step10-gen31 | asan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 0, "files": 71, "digest_differences_vs_stock": 0} |
| s3-step10-gen31 | tsan | {"returncode": 66, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 43, "output": "threads 4 repeats 1 files 12 digest_mismatches 38"} |
| s3-step11-gen34 | asan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 0, "files": 71, "digest_differences_vs_stock": 0} |
| s3-step11-gen34 | tsan | {"returncode": 66, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 34, "output": ""} |
| stock | asan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 1, "tsan_warnings": 0} |
| stock | tsan | {"returncode": 0, "asan_errors": 0, "ubsan_runtime_errors": 0, "tsan_warnings": 0} |
