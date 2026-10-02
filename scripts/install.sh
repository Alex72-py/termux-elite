#!/usr/bin/env sh
# Install termux-elite skills for a host agent that reads skill directories.
# Default is a managed copy (works everywhere). --link symlinks and follows git pull.
# Existing skills this script did not install are never overwritten or removed.
set -eu

usage() {
  cat <<'EOF'
Usage: sh scripts/install.sh <host> [options]

Hosts:  claude  opencode  gemini  agy  agents  kiro

Options:
  --project      install into the current project instead of your user directory
  --link         symlink instead of copy (the host must follow symlinks)
  --skill NAME   install only this skill (repeatable)
  --dry-run      show what would happen and change nothing
  --uninstall    remove only skills this script installed
  -h, --help     show this help
EOF
}

host=""
scope=user
mode=copy
dry=0
action=install
only=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --project) scope=project ;;
    --link) mode="link" ;;
    --dry-run) dry=1 ;;
    --uninstall) action=uninstall ;;
    --skill)
      shift
      if [ "$#" -eq 0 ]; then echo "--skill needs a name" >&2; exit 2; fi
      only="$only $1"
      ;;
    -*) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
    *)
      if [ -n "$host" ]; then echo "unexpected argument: $1" >&2; exit 2; fi
      host="$1"
      ;;
  esac
  shift
done

if [ -z "$host" ]; then usage >&2; exit 2; fi

root=$(cd "$(dirname "$0")/.." && pwd)
marker=".termux-elite-managed"

case "$host:$scope" in
  claude:user) dest="$HOME/.claude/skills" ;;
  claude:project) dest="$PWD/.claude/skills" ;;
  opencode:user) dest="${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills" ;;
  opencode:project) dest="$PWD/.opencode/skills" ;;
  gemini:user) dest="$HOME/.gemini/skills" ;;
  gemini:project) dest="$PWD/.gemini/skills" ;;
  agy:user) dest="$HOME/.gemini/config/skills" ;;
  agy:project) dest="$PWD/.agents/skills" ;;
  agents:user) dest="$HOME/.agents/skills" ;;
  agents:project) dest="$PWD/.agents/skills" ;;
  kiro:user) dest="$HOME/.kiro/skills" ;;
  kiro:project) dest="$PWD/.kiro/skills" ;;
  *) echo "unknown host: $host" >&2; usage >&2; exit 2 ;;
esac

for name in $only; do
  if [ ! -f "$root/skills/$name/SKILL.md" ]; then echo "unknown skill: $name" >&2; exit 2; fi
done

wanted() {
  if [ -z "$only" ]; then return 0; fi
  for s in $only; do
    if [ "$s" = "$1" ]; then return 0; fi
  done
  return 1
}

run() {
  if [ "$dry" -eq 1 ]; then printf 'would: %s\n' "$*"; else "$@"; fi
}

is_ours() {
  if [ -L "$1" ]; then
    case "$(readlink "$1")" in
      "$root"/skills/*) return 0 ;;
    esac
    return 1
  fi
  [ -f "$1/$marker" ]
}

done_count=0
skipped=0

if [ "$action" = install ]; then run mkdir -p "$dest"; fi

for dir in "$root"/skills/*/; do
  name=$(basename "$dir")
  if [ ! -f "$dir/SKILL.md" ]; then continue; fi
  if ! wanted "$name"; then continue; fi
  src="$root/skills/$name"
  target="$dest/$name"
  exists=0
  if [ -e "$target" ] || [ -L "$target" ]; then exists=1; fi

  if [ "$action" = uninstall ]; then
    if [ "$exists" -eq 0 ]; then continue; fi
    if is_ours "$target"; then
      run rm -rf "$target"
      done_count=$((done_count + 1))
    else
      echo "skip $name: $target is not managed by termux-elite"
      skipped=$((skipped + 1))
    fi
    continue
  fi

  if [ "$exists" -eq 1 ]; then
    if is_ours "$target"; then
      run rm -rf "$target"
    else
      echo "skip $name: $target exists and is not managed by termux-elite"
      skipped=$((skipped + 1))
      continue
    fi
  fi

  if [ "$mode" = link ]; then
    run ln -s "$src" "$target"
  else
    run cp -R "$src" "$target"
    if [ "$dry" -eq 0 ]; then printf '%s\n' "$src" > "$target/$marker"; fi
  fi
  done_count=$((done_count + 1))
done

printf '%s: %s skill(s) %s at %s (%s skipped)\n' "$host" "$done_count" "$action" "$dest" "$skipped"
if [ "$dry" -eq 0 ] && [ "$done_count" -gt 0 ]; then echo "Restart your agent so it rescans skills."; fi
exit 0
