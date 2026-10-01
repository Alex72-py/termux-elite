# Contributing

A skill belongs here only if it encodes a repeatable operational decision for agents in Termux or Android: when to inspect, what can fail, what is safe to change, and how to verify.

## Adding a skill

1. Copy `docs/SKILL_TEMPLATE.md` to `skills/<name>/SKILL.md`.
2. Add a matching entry to `manifest.json`. The frontmatter `name`, `description`, `triggers` (comma-separated), and `risk` must match the manifest exactly.
3. Required sections: `## Purpose`, `## Decision tree`, and at least one of `## Safety`, `## Verification`, `## Rollback`.
4. Helper scripts go in `skills/<name>/scripts/`, must start with a shebang, stay read-only, and pass `shellcheck -S warning`.
5. Run `python -m pytest -q`.

## Rules

- Read-only diagnostics first; mutating steps must be separate and confirmed.
- Never include secrets, tokens, or private keys.
- State facts you can verify; mark Android-version-specific behavior as such.
