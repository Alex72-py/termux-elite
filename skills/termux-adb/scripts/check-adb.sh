#!/usr/bin/env sh
# Read-only adb state. Never starts the adb server, pairs, or connects.
set -eu
have() { command -v "$1" >/dev/null 2>&1; }
if ! have adb; then
  printf '%s\n' "adb: absent"
  printf '%s\n' "hint: android-tools provides adb (installing it needs confirmation)"
  exit 0
fi
printf '%s\n' "adb: present"
printf '%s\n' "adb_version: $(adb version 2>/dev/null | head -n 1 || true)"
printf '%s\n' "android_sdk: $(getprop ro.build.version.sdk 2>/dev/null || printf unknown)"
if have pgrep && pgrep -x adb >/dev/null 2>&1; then
  printf '%s\n' "adb_server: running"
  if have timeout; then
    timeout 10 adb devices 2>/dev/null | sed '1d' | awk 'NF { printf "device_%d: %s\n", NR, $2 }' || true
  fi
else
  printf '%s\n' "adb_server: not running (not started by this check)"
fi
