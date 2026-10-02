#!/usr/bin/env sh
# Read-only sshd readiness. Reports modes and config lines, never key contents.
set -eu
have() { command -v "$1" >/dev/null 2>&1; }
printf '%s\n' "openssh_server: $(have sshd && printf present || printf absent)"
printf '%s\n' "sshd_running: $(pgrep -x sshd >/dev/null 2>&1 && printf yes || printf no)"
printf '%s\n' "whoami: $(whoami 2>/dev/null || printf unknown)"
printf '%s\n' "home_mode: $(stat -c '%a' "$HOME" 2>/dev/null || printf unknown)"
printf '%s\n' "ssh_dir_mode: $(stat -c '%a' "$HOME/.ssh" 2>/dev/null || printf absent)"
if [ -f "$HOME/.ssh/authorized_keys" ]; then
  printf '%s\n' "authorized_keys_mode: $(stat -c '%a' "$HOME/.ssh/authorized_keys" 2>/dev/null || printf unknown)"
  printf '%s\n' "authorized_keys_lines: $(grep -c . "$HOME/.ssh/authorized_keys" 2>/dev/null || printf 0)"
else
  printf '%s\n' "authorized_keys: absent"
fi
cfg="${PREFIX:-/nonexistent}/etc/ssh/sshd_config"
if [ -f "$cfg" ]; then
  printf '%s\n' "config_lines:"
  grep -E '^[[:space:]]*(Port|PasswordAuthentication|PubkeyAuthentication|PermitRootLogin|PermitEmptyPasswords)[[:space:]]' "$cfg" 2>/dev/null | sed 's/^/  /' || true
else
  printf '%s\n' "config: not found"
fi
exit 0
