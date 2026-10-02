# Claude Code

## Install

Plugin (recommended):

```text
/plugin marketplace add Alex72-py/termux-elite
/plugin install termux-elite@termux-elite
```

Plain skills, without the plugin system:

```sh
sh scripts/install.sh claude              # ~/.claude/skills
sh scripts/install.sh claude --project    # ./.claude/skills
```

## How it works

Claude Code loads each skill's `name` and `description` and reads the full `SKILL.md` only when a task matches, so the symptom-rich descriptions are what route the work. Helper scripts run through the normal Bash tool and its permission prompts.

The plugin is declared in `.claude-plugin/plugin.json`. The marketplace entry in `.claude-plugin/marketplace.json` points at the repository root, where Claude Code finds `skills/`.

## Notes

- Start a new session after installing so the skills are rescanned.
- OpenCode also reads `~/.claude/skills`, so this install covers both.
- The manifests are generated from `manifest.json` by `python scripts/sync_hosts.py`; do not edit them by hand.
