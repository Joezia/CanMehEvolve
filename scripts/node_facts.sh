#!/bin/bash
# Records CPU/OS facts of the node it runs on (post-hoc: the experiment runs themselves logged only core count and MHz).
echo "host=$(hostname)"; echo "date=$(date -Is)"
lscpu | grep -E "^(Model name|Socket|Core|Thread|CPU\(s\)|CPU max MHz|CPU min MHz|L3 cache|NUMA node\(s\))"
echo "mem_total_kB=$(grep MemTotal /proc/meminfo | awk '{print $2}')"
echo "governor=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo unknown)"
echo "kernel=$(uname -sr)"; echo "cxx=$(c++ --version | head -1)"
