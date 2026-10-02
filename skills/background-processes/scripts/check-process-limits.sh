#!/usr/bin/env sh
# Read-only facts about limits that make Android kill processes. Suggests a job count.
set -eu
have() { command -v "$1" >/dev/null 2>&1; }
sdk=unknown
if have getprop; then sdk=$(getprop ro.build.version.sdk 2>/dev/null || printf unknown); fi
cpus=$(nproc 2>/dev/null || printf 1)
mem_mib=$(awk '/^MemAvailable:/ {printf "%d", $2/1024}' /proc/meminfo 2>/dev/null || printf 0)
mine=$(ps -e 2>/dev/null | wc -l | tr -d ' ' || printf unknown)
jobs=$(awk -v c="$cpus" -v m="${mem_mib:-0}" 'BEGIN {j=int(m/1024); if (j>c) j=c; if (j<1) j=1; print j}')
printf '%s\n' "android_sdk: $sdk"
printf '%s\n' "cpus: $cpus"
printf '%s\n' "memory_available_mib: ${mem_mib:-unknown}"
printf '%s\n' "visible_processes: ${mine:-unknown}"
printf '%s\n' "suggested_build_jobs: $jobs"
printf '%s\n' "wake_lock_command: $(have termux-wake-lock && printf present || printf absent)"
printf '%s\n' "tmux: $(have tmux && printf present || printf absent)"
printf '%s\n' "adb: $(have adb && printf present || printf absent)"
