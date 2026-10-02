# OpenCode

## Install

```sh
sh scripts/install.sh opencode              # ~/.config/opencode/skills
sh scripts/install.sh opencode --project    # ./.opencode/skills
```

OpenCode also reads Claude-compatible and generic locations, so an existing install from `sh scripts/install.sh claude` or `sh scripts/install.sh agents` is picked up without a second copy.

## Discovery

Project: `.opencode/skills/`, `.claude/skills/`, `.agents/skills/` (OpenCode walks up from the working directory to the git worktree). Global: `~/.config/opencode/skills/`, `~/.claude/skills/`, `~/.agents/skills/`.

## How it works

Skills load on demand through OpenCode's native `skill` tool, which lists each skill's description to the model. Control access with `permission.skill` in `opencode.json` (allow, ask, or deny, with wildcard patterns on the skill name), or per agent in agent frontmatter. Set `tools: { skill: false }` on an agent to disable skills for it.

## Notes

- A skill is only found if its file is spelled exactly `SKILL.md`.
- Registering an extra skills directory from an OpenCode plugin is possible, but copying with `install.sh` is simpler and needs no plugin.
