# Round 2: traceability per run

Segment = one Slurm job of the self-managing chain (host, start, end). Final = the separate job that re-measured the fixed final patch three times. `Search.cpp` and binary hashes are the ones recorded by the segment jobs.

| run | chain | segment jobs (host, start -> end) | final-evaluation job (host) | code commit(s) | Search.cpp sha256 | binary sha256 | best.patch sha256 | HTTP requests |
|---|---|---|---|---|---|---|---|---|
| ds-population-s1 | A | 1094747 (xcnc30, 11-08T10:09 -> 11-08T12:48); 1095286 (xcnc4, 11-08T12:48 -> 11-08T13:26) | 1095414 (xcnc4) | 4f44902,527c5d0 | 9431cd448765 | 84a432f57b4a | ee5f3d19a473 | 40 |
| ds-bestofn-s2 | A | 1095415 (xcnc7, 11-08T13:26 -> 11-08T15:43) | 1095834 (xcnc7) | 4f44902 | 9431cd448765 | 84a432f57b4a | 33b6869deb96 | 40 |
| qwen-population-s3 | A | 1095835 (xcnc42, 11-08T15:43 -> 11-08T16:26) | 1096027 (xcnc1) | 4f44902 | 9431cd448765 | 84a432f57b4a | f74b4ba6653a | 40 |
| qwen-bestofn-s4 | A | 1096028 (xcnc6, 11-08T16:26 -> 11-08T17:12) | 1096273 (xcnc3) | 4f44902 | 9431cd448765 | 84a432f57b4a | f57567c4d6af | 40 |
| ds-population-s5 | A | 1096274 (xcnc4, 11-08T17:12 -> 11-08T19:50); 1096800 (xcnc1, 11-08T19:50 -> 11-08T20:18) | 1096862 (xcnc1) | 4f44902 | 9431cd448765 | 84a432f57b4a | 2f119535c605 | 40 |
| ds-bestofn-s1 | B | 1094748 (xcnc14, 11-08T10:11 -> 11-08T12:30) | 1095222 (xcnc3) | 527c5d0 | 9431cd448765 | 84a432f57b4a | c1c2cbe15e54 | 40 |
| ds-population-s2 | B | 1095223 (xcnc3, 11-08T12:37 -> 11-08T15:16); 1095766 (xcnc3, 11-08T15:16 -> 11-08T15:51) | 1095869 (xcnc1) | 4f44902 | 9431cd448765 | 84a432f57b4a | 3c44df16e019 | 40 |
| qwen-bestofn-s3 | B | 1095870 (xcnc3, 11-08T15:51 -> 11-08T16:39) | 1096082 (xcnc3) | 4f44902 | 9431cd448765 | 84a432f57b4a | 962a7d816a4d | 40 |
| qwen-population-s4 | B | 1096083 (xcnc8, 11-08T16:39 -> 11-08T17:18) | 1096292 (xcnc6) | 4f44902 | 9431cd448765 | 84a432f57b4a | 74d2b92fc9ed | 40 |
| ds-bestofn-s5 | B | 1096293 (xcnc8, 11-08T17:19 -> 11-08T19:52) | 1096806 (xcnc3) | 4f44902 | 9431cd448765 | 84a432f57b4a | cb353f7842f2 | 40 |
| ds-population-s3 | C | 1094749 (xcnc19, 11-08T10:11 -> 11-08T12:55); 1095306 (xcnc6, 11-08T12:55 -> 11-08T13:42) | 1095479 (xcnc4) | 4f44902,527c5d0 | 9431cd448765 | 84a432f57b4a | 46ce7efd5115 | 40 |
| ds-bestofn-s4 | C | 1095480 (xcnc6, 11-08T13:42 -> 11-08T16:14) | 1095978 (xcnc6) | 4f44902 | 9431cd448765 | 84a432f57b4a | a27da66cca1e | 40 |
| qwen-population-s1 | C | 1095979 (xcnc7, 11-08T16:14 -> 11-08T17:41) | 1096379 (xcnc1) | 4f44902 | 9431cd448765 | 84a432f57b4a | fde6cb2a2dea | 40 |
| qwen-bestofn-s2 | C | 1096380 (xcnc3, 11-08T17:41 -> 11-08T18:38) | 1096601 (xcnc1) | 4f44902 | 9431cd448765 | 84a432f57b4a | 5941a66a60e0 | 40 |
| qwen-population-s5 | C | 1096602 (xcnc3, 11-08T18:38 -> 11-08T19:42) | 1096772 (xcnc1) | 4f44902 | 9431cd448765 | 84a432f57b4a | 0bb70e98933b | 40 |
| ds-bestofn-s3 | D | 1094750 (xcnc33, 11-08T10:16 -> 11-08T12:21) | 1095170 (xcnc1) | b69fdd9 | 9431cd448765 | 84a432f57b4a | 4409f624457e | 40 |
| ds-population-s4 | D | 1095171 (xcnc1, 11-08T12:28 -> 11-08T15:07); 1095753 (xcnc1, 11-08T15:07 -> 11-08T15:43) | 1095837 (xcnc1) | 4f44902 | 9431cd448765 | 84a432f57b4a | ec036dc68873 | 40 |
| qwen-bestofn-s1 | D | 1095838 (xcnc43, 11-08T15:44 -> 11-08T16:30) | 1096057 (xcnc42) | 4f44902 | 9431cd448765 | 84a432f57b4a | c396d81a56e6 | 40 |
| qwen-population-s2 | D | 1096058 (xcnc43, 11-08T16:30 -> 11-08T17:23) | 1096301 (xcnc3) | 4f44902 | 9431cd448765 | 84a432f57b4a | 27e99a2dc4d9 | 40 |
| qwen-bestofn-s5 | D | 1096302 (xcnc25, 11-08T17:23 -> 11-08T18:14) | 1096517 (xcnc19) | 4f44902 | 9431cd448765 | 84a432f57b4a | c285a9cf4b6a | 40 |
