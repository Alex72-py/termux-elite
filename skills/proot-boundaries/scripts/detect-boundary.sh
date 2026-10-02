#!/usr/bin/env sh
# Read-only evidence for native Termux versus proot. Hints, not proof.
set -eu
tracer=$(awk '/^TracerPid:/ {print $2}' /proc/self/status 2>/dev/null || true)
os_id=
if [ -r /etc/os-release ]; then os_id=$(. /etc/os-release && printf '%s' "${ID:-}"); fi
printf '%s\n' "prefix: ${PREFIX:-unset}"
printf '%s\n' "tracer_pid: ${tracer:-unknown}"
printf '%s\n' "proot_tmp_dir: ${PROOT_TMP_DIR:-unset}"
printf '%s\n' "os_release_id: ${os_id:-none}"
printf '%s\n' "uname_o: $(uname -o 2>/dev/null || printf unknown)"
side=unknown
case "${PREFIX:-}" in
  /data/data/*/files/usr) side=native ;;
  *) if [ -n "${PROOT_TMP_DIR:-}" ] || { [ -n "$tracer" ] && [ "$tracer" != 0 ]; }; then side=proot; fi ;;
esac
printf '%s\n' "likely_side: $side"
root="${PREFIX:-}/var/lib/proot-distro/installed-rootfs"
if [ -d "$root" ]; then
  printf '%s\n' "installed_distros:"
  for d in "$root"/*; do
    [ -d "$d" ] && printf '  %s\n' "$(basename "$d")"
  done
else
  printf '%s\n' "installed_distros: none visible from here"
fi
