# Changelog

## Unreleased

- Frontmatter now follows the open Agent Skills format. `triggers` and `risk` moved under `metadata`, and every skill gains `license` and `compatibility`, so strict validators and every host that reads `SKILL.md` accept the files. `manifest.json` stays the routing source of truth and a test keeps the two in sync.
- Every skill gains a three-line `## Example` (situation, without the skill, with the skill), checked by tests.
- New skill `termux-adb`: pair and connect Wireless debugging from Termux to the same phone, read `unauthorized` and `offline` states, and record and roll back any adb-only setting. Read-only helper `check-adb.sh` never starts the adb server. `background-processes` now hands off to it.
- Tests: spec-key check, hand-written and PyYAML parsers must agree, example shape.

## 0.5.0 - 2026-10-03

- Discoverability: README rebuilt around a one-line `npx skills add Alex72-py/termux-elite` install, a symptom-to-skill table, a worked example, a safety summary and an FAQ. Failure-report and new-skill issue forms, a pull request template and a security policy added.
- `scripts/doctor.sh`: one read-only command that runs every skill helper and prints a single report (`--list`, `--skill NAME`).
- Accuracy, checked against Termux and Android sources: the phantom-process note now says the 32-process cap is system-wide and that the Android 14 toggle resets when Developer options is turned off; `node-native-build` documents the `GYP_DEFINES` alternative and the cause of the `android_ndk_path` error; `package-troubleshooting` checks the install source, because the Google Play build of Termux is deprecated, and the environment helper now prints `termux_apk_release`.
- Fix: two helpers that are documented as read-only were writing under `$HOME`: the Node helper (npm logs and cache) and the git helper (the GitHub CLI's telemetry device id). Both fixed, and every helper now has a test that it leaves `$HOME` untouched. Found by running the helpers, and by CI on a machine with `gh` installed.
- Routing: plain-language triggers added to seven skills. `evals/` adds scenario sets, `route.py` and a regression test. Measured with a lexical proxy: 28/28 on direct error strings, 11/14 on paraphrased phrasing (7/14 before the new triggers) and 8/14 on held-out phrasing. Agent-behaviour results are not measured yet; the protocol is in `evals/README.md`.
- Tests for the README, issue forms and community files: README links and skill count, issue-form YAML, changelog head.

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
