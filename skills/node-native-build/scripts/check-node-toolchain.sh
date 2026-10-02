#!/usr/bin/env sh
# Read-only Node and native addon toolchain facts.
set -eu
have() { command -v "$1" >/dev/null 2>&1; }
if have node; then
  printf '%s\n' "node: $(node -v 2>/dev/null || printf unknown)"
  printf '%s\n' "node_platform_arch: $(node -p 'process.platform + " " + process.arch' 2>/dev/null || printf unknown)"
else
  printf '%s\n' "node: unavailable"
fi
if have npm; then
  printf '%s\n' "npm: $(npm -v 2>/dev/null || printf unknown)"
  printf '%s\n' "npm_prefix: $(npm config get prefix 2>/dev/null || printf unknown)"
else
  printf '%s\n' "npm: unavailable"
fi
for tool in python3 make clang cc pkg-config; do
  if have "$tool"; then printf '%s: %s\n' "$tool" "$(command -v "$tool")"; else printf '%s: unavailable\n' "$tool"; fi
done
if [ -f "$HOME/.gyp/include.gypi" ]; then printf '%s\n' "gyp_include: present"; else printf '%s\n' "gyp_include: absent"; fi
printf '%s\n' "tmpdir: ${TMPDIR:-unset}"
printf '%s\n' "node_options_set: $([ -n "${NODE_OPTIONS:-}" ] && printf yes || printf no)"
