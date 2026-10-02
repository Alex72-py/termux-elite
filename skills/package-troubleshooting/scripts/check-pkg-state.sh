#!/usr/bin/env sh
# Read-only package manager state. Prints mirror hosts, not full URLs or credentials.
set -eu
have() { command -v "$1" >/dev/null 2>&1; }
for tool in pkg apt dpkg; do
  if have "$tool"; then printf '%s: %s\n' "$tool" "$(command -v "$tool")"; else printf '%s: unavailable\n' "$tool"; fi
done
printf '%s\n' "dpkg_architecture: $(dpkg --print-architecture 2>/dev/null || printf unknown)"
printf '%s\n' "date_utc: $(date -u '+%Y-%m-%d %H:%M' 2>/dev/null || printf unknown)"
printf '%s\n' "mirror_hosts:"
for f in "${PREFIX:-/nonexistent}/etc/apt/sources.list" "${PREFIX:-/nonexistent}"/etc/apt/sources.list.d/*; do
  [ -f "$f" ] || continue
  sed -n 's#^deb[[:space:]]\{1,\}\(\[[^]]*\][[:space:]]\{1,\}\)\{0,1\}[a-z]*://\([^/@ ]*\).*#  \2#p' "$f"
done | sort -u
broken=$(dpkg --audit 2>/dev/null | wc -l | tr -d ' ' || true)
printf '%s\n' "dpkg_audit_lines: ${broken:-unknown}"
printf '%s\n' "home_free_mib: $(df -P "$HOME" 2>/dev/null | awk 'NR==2 {printf "%d", $4/1024}' || printf unknown)"
