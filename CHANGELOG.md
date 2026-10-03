# Changelog

## Unreleased

- README rebuilt around discovery: a one-line `npx skills add Alex72-py/termux-elite` install, a worked example, a symptom-to-skill table, a safety summary, FAQ, and a call for real-world failure reports.
- Issue forms for failure reports and new-skill proposals, a pull request template, and a security policy.
- Tests that keep the README, issue forms, and community files consistent with the skills.

## 0.4.0 - 2026-10-02

- Host support: Claude Code (plugin and marketplace), Antigravity CLI (`plugin.json`), Gemini CLI (extension manifest and `skills install`), OpenCode, Codex, Cursor, Kiro, and any host that reads `AGENTS.md` or skill directories.
- `scripts/sync_hosts.py` generates every host manifest and `AGENTS.md` from `manifest.json`; `--check` fails when they drift.
- `scripts/install.sh` installs skills into a host's skill directory (copy or `--link`, `--project`, `--skill`, `--dry-run`, `--uninstall`) and never touches skills it did not install.
- Adapter docs rewritten with current install commands and discovery paths; OpenCode adapter added.
- README is now host-neutral; removed the section that described a specific separate project.
- Tests for generated files, host identity and versions, and the installer across every host and scope.

## 0.3.0 - 2026-10-02

- Rewrote all nine skills to a stricter standard: trigger-rich descriptions with explicit "Do NOT use" clauses, symptom-driven decision trees, Termux-specific facts, `Handoffs`, and a `Report` contract.
- Added skills: `node-native-build`, `termux-services`, `termux-sshd`, `termux-backup`, `termux-network`.
- Added read-only helper scripts for every skill; manifest entries now carry `related` and `scripts`.
- Removed host-specific wording from `package-troubleshooting` so the skill stays portable.
- Tests: description discoverability, YAML validity, required sections, rollback for medium risk, handoff integrity, script and SKILL.md agreement, credential redaction, hostname rejection, word-boundary read-only check.
- CI installs PyYAML so the frontmatter is validated as real YAML.

## 0.2.0 - 2026-10-01

- Added skills: `termux-api`, `background-processes`, `git-credentials`.
- Added `scripts/check-termux-api.sh` helper.
- Expanded tests: manifest shape, frontmatter parity, required sections, script syntax and read-only checks, secret scan.
- Added GitHub Actions CI (pytest on Python 3.9 and 3.12, shellcheck).
- Added CONTRIBUTING.md and a skill template.
- README: skill table, host integration snippet, verification steps.
