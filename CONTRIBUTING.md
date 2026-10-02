# Contributing

A skill belongs here only if it encodes a repeatable operational decision for agents in Termux or Android: when to inspect, what can fail, what is safe to change, and how to verify.

## The quality bar

1. **The description is the trigger.** Hosts choose a skill from its `description`, so it must say what the skill decides, list real symptoms and error strings after "Use when", and end with "Do NOT use for ..." naming the neighbouring skill. 150 to 1024 characters, no `: ` or ` #` inside it (it must stay valid YAML).
2. **Cheapest read-only check first.** The decision tree is a ladder: first match wins, and diagnostics come before any change.
3. **Facts you can verify.** Mark Android-version-specific behavior as such. If a fix depends on the device, say how to check it.
4. **Safety is explicit.** Say which steps mutate state, what needs confirmation, and what must never be printed.
5. **Verify and report.** End with a command that proves the original failure is gone, and a short report contract.
6. **Hand off, do not sprawl.** Anything that belongs to another skill goes in `## Handoffs`.

## Adding a skill

1. Copy `docs/SKILL_TEMPLATE.md` to `skills/<name>/SKILL.md`. The name is lowercase with hyphens and equals the directory name.
2. Required sections: `## Purpose`, `## When to use`, `## When NOT to use`, `## Decision tree`, `## Safety`, `## Verification`, `## Handoffs`, `## Report`. Medium and high risk skills also need `## Rollback`. Keep the body under 150 lines; move depth into `references/`.
3. Frontmatter holds `name`, `description`, `triggers` (comma separated) and `risk`. Add a matching manifest entry with `required_capabilities`, `platform`, `risk_level`, `related` (the skills listed in Handoffs, same order is not required) and `scripts`.
4. Helper scripts go in `skills/<name>/scripts/`, start with a shebang, use `set -eu`, stay read-only, are executable, exit 0, print `key: value` facts, and pass `shellcheck -S warning`. Reference each one from `SKILL.md` as `scripts/<file>.sh`.
5. Run `python scripts/sync_hosts.py` to refresh the generated host files (`AGENTS.md` and the plugin manifests). Never edit those by hand.
6. Run `python -m pytest -q`.

## Rules

- Read-only diagnostics first; mutating steps are separate and confirmed.
- Never include secrets, tokens, or private keys, and never make a script print them.
- No host-specific wording in skills; adapters carry host details.
