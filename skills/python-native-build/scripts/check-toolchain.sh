#!/usr/bin/env sh
set -eu
printf '%s\n' "python: $(python3 -V 2>&1 || printf unavailable)"
printf '%s\n' "pip: $(python3 -m pip --version 2>&1 || printf unavailable)"
printf '%s\n' "architecture: $(uname -m 2>/dev/null || printf unknown)"
for tool in cc clang make cmake pkg-config rustc cargo; do
  if command -v "$tool" >/dev/null 2>&1; then printf '%s: %s\n' "$tool" "$(command -v "$tool")"; else printf '%s: unavailable\n' "$tool"; fi
done
