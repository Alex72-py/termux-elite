#!/usr/bin/env sh
# Run every read-only helper script and print one combined report.
# Nothing is modified. Usage: sh scripts/doctor.sh [--list] [--skill NAME]...
set -eu

root=$(cd "$(dirname "$0")/.." && pwd)
only=""
list=0

usage() {
  cat <<'EOF'
Usage: sh scripts/doctor.sh [options]

Runs every read-only helper under skills/*/scripts/ and prints one report,
starting with the environment snapshot. Nothing is modified.

Options:
  --skill NAME   only run this skill's helpers (repeatable)
  --list         list the helpers without running them
  -h, --help     show this help
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --list) list=1 ;;
    --skill)
      [ "$#" -ge 2 ] || { echo "--skill needs a name" >&2; exit 2; }
      shift
      case "$1" in *[!a-z0-9-]*|"") echo "unknown skill: $1" >&2; exit 2 ;; esac
      [ -d "$root/skills/$1" ] || { echo "unknown skill: $1" >&2; exit 2; }
      only="$only $1"
      ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

wanted() {
  [ -z "$only" ] && return 0
  for n in $only; do
    [ "$n" = "$1" ] && return 0
  done
  return 1
}

run_helper() {
  name=$1
  script=$2
  rel=${script#"$root"/}
  if [ "$list" -eq 1 ]; then
    printf '%s: %s\n' "$name" "$rel"
    return 0
  fi
  printf '\n== %s: %s ==\n' "$name" "$rel"
  status=0
  if command -v timeout >/dev/null 2>&1; then
    timeout 20 sh "$script" 2>&1 || status=$?
  else
    sh "$script" 2>&1 || status=$?
  fi
  if [ "$status" -ne 0 ]; then
    printf '(helper exited with status %s)\n' "$status"
  fi
}

run_skill() {
  wanted "$1" || return 0
  for script in "$root"/skills/"$1"/scripts/*.sh; do
    [ -f "$script" ] || continue
    run_helper "$1" "$script"
  done
}

run_skill termux-environment
for dir in "$root"/skills/*/; do
  name=$(basename "$dir")
  [ "$name" = termux-environment ] && continue
  run_skill "$name"
done

if [ "$list" -eq 0 ]; then
  printf '\n%s\n' "Next: open the SKILL.md for the layer that looks wrong (see the symptom table in README.md). Nothing was changed."
fi
