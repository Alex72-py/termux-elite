#!/usr/bin/env sh
# Read-only service and boot script state.
set -eu
have() { command -v "$1" >/dev/null 2>&1; }
printf '%s\n' "sv_command: $(have sv && printf present || printf absent)"
printf '%s\n' "tmux: $(have tmux && printf present || printf absent)"
printf '%s\n' "runsvdir_running: $(pgrep runsvdir >/dev/null 2>&1 && printf yes || printf no)"
svc="${PREFIX:-/nonexistent}/var/service"
if [ -d "$svc" ]; then
  printf '%s\n' "services:"
  for d in "$svc"/*; do
    [ -d "$d" ] || continue
    name=$(basename "$d")
    status=unknown
    if have sv; then status=$(sv status "$name" 2>/dev/null | head -n 1 || printf unknown); fi
    printf '  %s: %s\n' "$name" "$status"
  done
else
  printf '%s\n' "services: none (termux-services not installed or never started)"
fi
boot="$HOME/.termux/boot"
if [ -d "$boot" ]; then
  printf '%s\n' "boot_scripts:"
  for f in "$boot"/*; do
    [ -f "$f" ] || continue
    printf '  %s executable=%s\n' "$(basename "$f")" "$([ -x "$f" ] && printf yes || printf no)"
  done
else
  printf '%s\n' "boot_scripts: none"
fi
