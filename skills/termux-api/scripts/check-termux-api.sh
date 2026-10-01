#!/usr/bin/env sh
# Read-only, bounded check of Termux:API availability.
set -eu
if command -v termux-battery-status >/dev/null 2>&1; then
  printf '%s\n' "termux_api_binaries: present"
else
  printf '%s\n' "termux_api_binaries: absent"
  exit 0
fi
if command -v timeout >/dev/null 2>&1; then
  if timeout 10 termux-battery-status >/dev/null 2>&1; then
    printf '%s\n' "termux_api_app: responding"
  else
    printf '%s\n' "termux_api_app: not responding (app missing, stopped, restricted, or source mismatch)"
  fi
else
  printf '%s\n' "termux_api_app: unchecked (timeout unavailable)"
fi
