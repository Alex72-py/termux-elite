#!/usr/bin/env sh
# Read-only git auth facts. Redacts credentials in URLs; never reads key contents.
set -eu
have() { command -v "$1" >/dev/null 2>&1; }
printf '%s\n' "remotes:"
if have git; then
  git remote -v 2>/dev/null | sed -E 's#(://)[^/@[:space:]]+@#\1<redacted>@#' | sed 's/^/  /' || true
fi
helper=none
if have git; then helper=$(git config --get credential.helper 2>/dev/null || printf none); fi
printf '%s\n' "credential_helper: $helper"
if [ -f "$HOME/.git-credentials" ]; then printf '%s\n' "plaintext_credentials_file: present"; else printf '%s\n' "plaintext_credentials_file: absent"; fi
if have gh; then
  # gh writes a telemetry device id under $HOME unless told not to; keep this check read-only.
  if env GH_TELEMETRY=false DO_NOT_TRACK=1 GH_NO_UPDATE_NOTIFIER=1 gh auth status >/dev/null 2>&1; then printf '%s\n' "gh_auth: logged in"; else printf '%s\n' "gh_auth: not logged in"; fi
else
  printf '%s\n' "gh_auth: gh not installed"
fi
printf '%s\n' "token_env_vars_set:"
[ -n "${GH_TOKEN:-}" ] && printf '  %s\n' GH_TOKEN
[ -n "${GITHUB_TOKEN:-}" ] && printf '  %s\n' GITHUB_TOKEN
[ -n "${GIT_ASKPASS:-}" ] && printf '  %s\n' GIT_ASKPASS
printf '%s\n' "ssh_dir_mode: $(stat -c '%a' "$HOME/.ssh" 2>/dev/null || printf absent)"
printf '%s\n' "ssh_files:"
if [ -d "$HOME/.ssh" ]; then
  for f in "$HOME"/.ssh/*; do
    [ -f "$f" ] || continue
    printf '  %s %s\n' "$(stat -c '%a' "$f" 2>/dev/null || printf '?')" "$(basename "$f")"
  done
fi
printf '%s\n' "ssh_agent: ${SSH_AUTH_SOCK:+socket set}"
exit 0
