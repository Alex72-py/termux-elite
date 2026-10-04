#!/usr/bin/env sh
# Read-only environment snapshot. Prints facts only; never dumps the environment.
# TERMUX_ELITE_PROC_STATUS and TERMUX_ELITE_OS_RELEASE exist only so tests can simulate other systems.
set -eu

have() { command -v "$1" >/dev/null 2>&1; }
show() { printf '%s: %s\n' "$1" "${2:-unknown}"; }
prop() { if have getprop; then getprop "$1" 2>/dev/null || true; fi; }

status_file=${TERMUX_ELITE_PROC_STATUS:-/proc/self/status}
os_release=${TERMUX_ELITE_OS_RELEASE:-/etc/os-release}
uname_s=$(uname -s 2>/dev/null || true)
android_release=$(prop ro.build.version.release)
tracer=$(awk '/^TracerPid:/ {print $2}' "$status_file" 2>/dev/null || true)
os_id=
if [ -r "$os_release" ]; then
  # shellcheck source=/dev/null
  os_id=$(. "$os_release" && printf '%s' "${ID:-}")
fi

android_prefix=no
case "${PREFIX:-}" in
  /data/data/*/files/usr) android_prefix=yes ;;
esac
tracing=no
if [ -n "${PROOT_TMP_DIR:-}" ] || { [ -n "$tracer" ] && [ "$tracer" != 0 ]; }; then tracing=yes; fi

class=unknown
evidence="no rule matched"
case "$uname_s" in
  Darwin)
    class=macos
    evidence="uname -s is Darwin"
    ;;
  Linux)
    if [ "$android_prefix" = yes ] && [ "$tracing" = yes ] && [ -n "$os_id" ]; then
      class=proot
      evidence="Termux PREFIX inherited into a traced shell that sees a distro os-release"
    elif [ "$android_prefix" = yes ]; then
      class=termux-native
      evidence="PREFIX is an Android app prefix"
    elif [ "$tracing" = yes ]; then
      class=proot
      evidence="ptrace tracer or PROOT_TMP_DIR present, PREFIX is not an Android app prefix (a debugger can look the same)"
    elif [ -n "$android_release" ]; then
      class=android-other
      evidence="Android properties are readable but PREFIX is not a Termux prefix"
    elif grep -qi microsoft /proc/version 2>/dev/null; then
      class=wsl
      evidence="/proc/version mentions Microsoft"
    elif [ -e /.dockerenv ] || [ -e /run/.containerenv ]; then
      class=container
      evidence="container marker file present"
    else
      class=linux
      evidence="Linux without Android, proot, WSL, or container markers"
    fi
    ;;
esac

libc=unknown
case "$class" in
  termux-native|android-other) libc=bionic ;;
  macos) libc=libsystem ;;
  *)
    for f in /lib/ld-musl-* /usr/lib/ld-musl-*; do
      if [ -e "$f" ]; then libc=musl; fi
    done
    if [ "$libc" = unknown ] && have getconf && getconf GNU_LIBC_VERSION >/dev/null 2>&1; then libc=glibc; fi
    ;;
esac

sys_pm=unknown
case "$class" in
  termux-native) sys_pm=pkg ;;
  macos) sys_pm=brew ;;
  *)
    case "$os_id" in
      debian|ubuntu|kali|raspbian) sys_pm=apt ;;
      alpine) sys_pm=apk ;;
      arch|manjaro) sys_pm=pacman ;;
      fedora|rhel|centos|rocky|almalinux) sys_pm=dnf ;;
    esac
    ;;
esac

managed=no
for f in "${PREFIX:-/nonexistent}"/lib/python3*/EXTERNALLY-MANAGED /usr/lib/python3*/EXTERNALLY-MANAGED; do
  if [ -f "$f" ]; then managed=yes; fi
done

show environment_class "$class"
show environment_evidence "$evidence"
show libc "$libc"
show system_package_manager "$sys_pm"
show python_externally_managed "$managed"
if [ "$class" = termux-native ] || [ -d "${PREFIX:-/nonexistent}/etc/apt/sources.list.d" ]; then
  tur=not-enabled
  x11=not-enabled
  rootrepo=not-enabled
  for f in "$PREFIX"/etc/apt/sources.list.d/*; do
    [ -f "$f" ] || continue
    case "$(basename "$f")" in
      *tur*) tur=enabled ;;
      *x11*) x11=enabled ;;
      *root*) rootrepo=enabled ;;
    esac
  done
  show tur_repo "$tur"
  show x11_repo "$x11"
  show root_repo "$rootrepo"
fi
case "$class" in
  termux-native) show hint "use pkg and Termux package names; for Python libraries try the Termux package first, then tur-repo with consent, then a venv with --system-site-packages, and compile last" ;;
  proot) show hint "use the distro package manager and its libc; termux-* commands and Termux package names belong to the native side" ;;
  android-other) show hint "not a Termux prefix; do not assume pkg or Termux paths, ask which shell or app this is" ;;
  linux|wsl|container|macos) show hint "not Android; the Termux-specific steps in these skills do not apply" ;;
  *) show hint "could not classify; ask the user instead of assuming" ;;
esac

show platform "$uname_s"
show kernel "$(uname -r 2>/dev/null || true)"
show architecture "$(uname -m 2>/dev/null || true)"
show android_release "$android_release"
show android_sdk "$(prop ro.build.version.sdk)"
show prefix "${PREFIX:-unset}"
show termux_version "${TERMUX_VERSION:-unset}"
show termux_apk_release "${TERMUX_APK_RELEASE:-unset}"
show tmpdir "${TMPDIR:-unset}"
show tracer_pid "$tracer"
show proot_tmp_dir "${PROOT_TMP_DIR:-unset}"
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
