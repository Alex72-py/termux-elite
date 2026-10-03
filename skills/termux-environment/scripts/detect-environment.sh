#!/usr/bin/env sh
# Read-only environment snapshot. Prints facts only; never dumps the environment.
set -eu

have() { command -v "$1" >/dev/null 2>&1; }
show() { printf '%s: %s\n' "$1" "${2:-unknown}"; }
prop() { if have getprop; then getprop "$1" 2>/dev/null || true; fi; }

show platform "$(uname -s 2>/dev/null || true)"
show kernel "$(uname -r 2>/dev/null || true)"
show architecture "$(uname -m 2>/dev/null || true)"
show android_release "$(prop ro.build.version.release)"
show android_sdk "$(prop ro.build.version.sdk)"
show prefix "${PREFIX:-unset}"
show termux_version "${TERMUX_VERSION:-unset}"
show termux_apk_release "${TERMUX_APK_RELEASE:-unset}"
show tmpdir "${TMPDIR:-unset}"

tracer=$(awk '/^TracerPid:/ {print $2}' /proc/self/status 2>/dev/null || true)
show tracer_pid "$tracer"
show proot_tmp_dir "${PROOT_TMP_DIR:-unset}"
os_id=
if [ -r /etc/os-release ]; then os_id=$(. /etc/os-release && printf '%s' "${ID:-}"); fi
show os_release_id "$os_id"

printf '%s\n' "package_managers:"
for tool in pkg apt dpkg; do
  if have "$tool"; then printf '  %s: %s\n' "$tool" "$(command -v "$tool")"; fi
done

printf '%s\n' "storage_shared:"
if [ -e "$HOME/storage/shared" ]; then printf '%s\n' "  present"; else printf '%s\n' "  absent"; fi

mem=$(awk '/^MemAvailable:/ {printf "%d MiB", $2/1024}' /proc/meminfo 2>/dev/null || true)
disk=$(df -P "$HOME" 2>/dev/null | awk 'NR==2 {printf "%d MiB", $4/1024}' || true)
show memory_available "$mem"
show home_free "$disk"

printf '%s\n' "tools:"
for tool in python python3 pip git gh clang make cmake pkg-config rustc cargo go node npm adb tmux proot-distro termux-api termux-wake-lock; do
  if have "$tool"; then printf '  %s: %s\n' "$tool" "$(command -v "$tool")"; fi
done
