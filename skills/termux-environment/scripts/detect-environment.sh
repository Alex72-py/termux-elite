#!/usr/bin/env sh
set -eu
printf '%s\n' "platform: $(uname -s 2>/dev/null || printf unknown)"
printf '%s\n' "kernel: $(uname -r 2>/dev/null || printf unknown)"
printf '%s\n' "architecture: $(uname -m 2>/dev/null || printf unknown)"
printf '%s\n' "prefix: ${PREFIX:-unset}"
printf '%s\n' "termux_version: ${TERMUX_VERSION:-unset}"
printf '%s\n' "package_managers:"
for tool in pkg apt; do
  if command -v "$tool" >/dev/null 2>&1; then printf '  %s: %s\n' "$tool" "$(command -v "$tool")"; fi
done
printf '%s\n' "storage_shared:"
if [ -e "$HOME/storage/shared" ]; then printf '%s\n' "  present"; else printf '%s\n' "  absent"; fi
printf '%s\n' "tools:"
for tool in python python3 pip git gh clang make cmake rustc cargo go node adb termux-api proot-distro rish; do
  if command -v "$tool" >/dev/null 2>&1; then printf '  %s: %s\n' "$tool" "$(command -v "$tool")"; fi
done
