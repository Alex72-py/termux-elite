# Changelog

## 0.3.0 - 2026-10-02

- Rewrote all nine skills to a stricter standard: trigger-rich descriptions with explicit "Do NOT use" clauses, symptom-driven decision trees, Termux-specific facts, `Handoffs`, and a `Report` contract.
- Added skills: `node-native-build`, `termux-services`, `termux-sshd`, `termux-backup`, `termux-network`.
- Added read-only helper scripts for every skill; manifest entries now carry `related` and `scripts`.
- Removed a host-specific phrase ("Guardian confirmation") from `package-troubleshooting`.
- Tests: description discoverability, YAML validity, required sections, rollback for medium risk, handoff integrity, script and SKILL.md agreement, credential redaction, hostname rejection, word-boundary read-only check.
- CI installs PyYAML so the frontmatter is validated as real YAML.

## 0.2.0 - 2026-10-01

- Added skills: `termux-api`, `background-processes`, `git-credentials`.
- Added `scripts/check-termux-api.sh` helper.
- Expanded tests: manifest shape, frontmatter parity, required sections, script syntax and read-only checks, secret scan.
- Added GitHub Actions CI (pytest on Python 3.9 and 3.12, shellcheck).
- Added CONTRIBUTING.md and a skill template.
- README: skill table, host integration snippet, verification steps.
