#!/usr/bin/env sh
# Read-only storage link and permission facts. Never lists shared-storage contents.
set -eu
printf '%s\n' "home: $HOME"
printf '%s\n' "home_writable: $([ -w "$HOME" ] && printf yes || printf no)"
if [ -d "$HOME/storage" ]; then
  printf '%s\n' "storage_dir: present"
  for link in "$HOME"/storage/*; do
    [ -e "$link" ] || [ -L "$link" ] || continue
    target=$(readlink "$link" 2>/dev/null || printf '-')
    state=broken
    if [ -d "$link" ]; then state=reachable; fi
    printf '  %s -> %s (%s)\n' "$(basename "$link")" "$target" "$state"
  done
else
  printf '%s\n' "storage_dir: absent"
fi
for dir in "$HOME/storage/shared" "$HOME/storage/downloads"; do
  if [ -d "$dir" ]; then
    printf '%s\n' "$(basename "$dir")_writable: $([ -w "$dir" ] && printf yes || printf no)"
  fi
done
printf '%s\n' "home_free_mib: $(df -P "$HOME" 2>/dev/null | awk 'NR==2 {printf "%d", $4/1024}' || printf unknown)"
