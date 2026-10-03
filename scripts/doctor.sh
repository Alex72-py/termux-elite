#!/usr/bin/env sh
# Run every skill helper (all read-only) and print one combined report.
set -eu

root=$(cd "$(dirname "$0")/.." && pwd)
only=""
list=0

usage() {
  cat <<'EOF'
Usage: sh scripts/doctor.sh [--list] [--skill NAME]...

Runs the read-only helper script of every skill and prints one report.
Nothing is changed. Paste the output to your agent, then follow the skill
that matches the layer that looks wrong.

  --list         show which helpers would run, then exit
  --skill NAME   only run this skill's helpers (repeatable)
  -h, --help     show this help
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --list) list=1 ;;
    --skill)
      shift
      [ "$#" -gt 0 ] || { echo "--skill needs a name" >&2; exit 2; }
      case "$1" in
        ""|*/*|.*) echo "unknown skill: $1" >&2; exit 2 ;;
      esac
      [ -d "$root/skills/$1" ] || { echo "unknown skill: $1" >&2; exit 2; }
      only="$only $1"
      ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

wanted() {
  [ -z "$only" ] && return 0
  for s in $only; do
    [ "$s" = "$1" ] && return 0
  done
  return 1
}

run_skill() {
  name=$1
  wanted "$name" || return 0
  for script in "$root/skills/$name"/scripts/*.sh; do
    [ -f "$script" ] || continue
    rel="skills/$name/scripts/$(basename "$script")"
    if [ "$list" -eq 1 ]; then
      printf '%s\n' "$rel"
      continue
    fi
    printf '\n== %s ==\n' "$rel"
    status=0
    if command -v timeout >/dev/null 2>&1; then
      timeout 20 sh "$script" 2>&1 || status=$?
    else
      sh "$script" 2>&1 || status=$?
    fi
    [ "$status" -eq 0 ] || printf 'helper exited with status %s\n' "$status"
  done
}

# The device snapshot comes first; everything else is alphabetical.
run_skill termux-environment
for dir in "$root"/skills/*/; do
  name=$(basename "$dir")
  [ "$name" = "termux-environment" ] && continue
  run_skill "$name"
done

if [ "$list" -eq 0 ]; then
  printf '\nDone. Read the SKILL.md for the layer that looks wrong; the README symptom table maps errors to skills.\n'
fi
