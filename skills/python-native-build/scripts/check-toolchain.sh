#!/usr/bin/env sh
# Read-only Python and native toolchain facts.
set -eu
have() { command -v "$1" >/dev/null 2>&1; }
printf '%s\n' "python: $(python3 -V 2>&1 || printf unavailable)"
printf '%s\n' "pip: $(python3 -m pip --version 2>&1 || printf unavailable)"
printf '%s\n' "architecture: $(uname -m 2>/dev/null || printf unknown)"
sdk=unknown
if have getprop; then sdk=$(getprop ro.build.version.sdk 2>/dev/null || printf unknown); fi
printf '%s\n' "android_sdk: $sdk"
printf '%s\n' "venv_active: ${VIRTUAL_ENV:-no}"
if [ -n "${VIRTUAL_ENV:-}" ] && [ -f "$VIRTUAL_ENV/pyvenv.cfg" ]; then
  printf '%s\n' "venv_system_site_packages: $(sed -n 's/^include-system-site-packages *= *//p' "$VIRTUAL_ENV/pyvenv.cfg")"
fi
printf '%s\n' "pip_break_system_packages_env: ${PIP_BREAK_SYSTEM_PACKAGES:-unset}"
if have dpkg-query; then
  libs=$(dpkg-query -W -f='${Package}\n' 'python-*' 2>/dev/null | head -n 30 | tr '\n' ' ' || true)
  printf '%s\n' "packaged_python_libs: ${libs:-none}"
fi
printf '%s\n' "android_api_level_env: ${ANDROID_API_LEVEL:-unset}"
for tool in cc clang make cmake pkg-config rustc cargo maturin; do
  if have "$tool"; then printf '%s: %s\n' "$tool" "$(command -v "$tool")"; else printf '%s: unavailable\n' "$tool"; fi
done
managed=no
for f in "${PREFIX:-/nonexistent}"/lib/python3*/EXTERNALLY-MANAGED; do
  if [ -f "$f" ]; then managed=yes; fi
done
printf '%s\n' "externally_managed: $managed"
