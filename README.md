# termux-elite

[![ci](https://github.com/Alex72-py/termux-elite/actions/workflows/ci.yml/badge.svg)](https://github.com/Alex72-py/termux-elite/actions/workflows/ci.yml)
[![license: MIT](https://img.shields.io/github/license/Alex72-py/termux-elite)](LICENSE)
![skills: 15](https://img.shields.io/badge/skills-15-blue)

**Termux is not a normal Linux box, and your AI agent keeps forgetting that.** `termux-elite` gives coding agents 15 short, tested playbooks for the things that actually break on a phone: glibc wheels that will not import, `node-gyp` looking for an NDK, processes Android kills with signal 9, `/sdcard` permissions, proot versus native, and more.

Each skill tells the agent what to inspect first, which layer is failing, what is safe to change, how to prove the fix worked, and when to hand off to a neighbouring skill.

```sh
npx skills add Alex72-py/termux-elite
```

Works with Claude Code, Codex, Gemini CLI, Cursor, OpenCode, Antigravity and the other agents the [skills CLI](https://skills.sh) supports. Host-specific options are [below](#install).

## What changes for your agent

Without a playbook, an agent that sees `pip install cryptography` fail on a phone tends to retry, reach for `sudo`, or install a toolchain it did not need. With `python-native-build` loaded it is guided to:

1. Establish native Termux versus proot.
2. Capture Python version, pip location, architecture, and the first real compiler error.
3. Check whether a compatible wheel or a Termux-packaged library exists before building anything.
4. Explain and confirm any package or toolchain change.
5. Re-run the install and import a minimal module.
6. Report what changed and what is still unsupported on Android.

The skill is a procedure, not a command to run blindly. See [examples/](examples/python-install-failure.md).

## Find the skill by symptom

| If you see... | Skill |
| --- | --- |
| `pip install` fails: `failed building wheel`, `externally-managed-environment`, no wheel for this platform | [`python-native-build`](skills/python-native-build/SKILL.md) |
| `npm install` fails with `node-gyp`, `android_ndk_path`, or `unsupported platform android` | [`node-native-build`](skills/node-native-build/SKILL.md) |
| `pkg` or `apt`: `unable to locate package`, hash mismatch, `cannot link executable` | [`package-troubleshooting`](skills/package-troubleshooting/SKILL.md) |
| A process disappears: `signal 9`, exit code `137`, build dies when the screen locks | [`background-processes`](skills/background-processes/SKILL.md) |
| A server must survive crashes, reboots, or a closed terminal | [`termux-services`](skills/termux-services/SKILL.md) |
| `Permission denied` on `/sdcard` or shared storage | [`storage-permissions`](skills/storage-permissions/SKILL.md) |
| `termux-battery-status` and other `termux-*` commands hang or print nothing | [`termux-api`](skills/termux-api/SKILL.md) |
| `curl`, `pip`, or `git` cannot connect; `certificate verify failed`; cannot bind a port | [`termux-network`](skills/termux-network/SKILL.md) |
| `git push`: `Permission denied (publickey)`, HTTP 403, authentication failed | [`git-credentials`](skills/git-credentials/SKILL.md) |
| Passes locally, fails on GitHub Actions | [`github-actions`](skills/github-actions/SKILL.md) |
| Unsure whether to use native Termux or proot, or a glibc binary will not run | [`proot-boundaries`](skills/proot-boundaries/SKILL.md) |
| You want to SSH into the phone (port 8022) and get `connection refused` | [`termux-sshd`](skills/termux-sshd/SKILL.md) |
| `adb pair` / `adb connect` from Termux, or `adb devices` says `unauthorized` | [`termux-adb`](skills/termux-adb/SKILL.md) |
| You are about to upgrade or migrate and want a restore point | [`termux-backup`](skills/termux-backup/SKILL.md) |
| What device, architecture, and toolchain is this, anyway? | [`termux-environment`](skills/termux-environment/SKILL.md) |

Agents do not need this table: each skill's `description` lists the same symptoms, and [`AGENTS.md`](AGENTS.md) and [`manifest.json`](manifest.json) carry a routing index with a risk level per skill.

## Triage in one command

```sh
sh scripts/doctor.sh                       # run every read-only helper, print one report
sh scripts/doctor.sh --list                # show what it would run
sh scripts/doctor.sh --skill termux-network
```

It prints facts only and changes nothing. Paste the report to your agent, then follow the skill for whichever layer looks wrong (device and install source, package manager, toolchain, network, storage, git auth).

## Safe by design

- **Inspect before mutating.** The first step of every skill is a cheap read-only check, and each skill ships a small helper script that only prints `key: value` facts.
- **Mutations are confirmed.** Package installs, permission changes, config edits, and service changes are named explicitly and need confirmation. Medium-risk skills include a rollback.
- **No secrets.** Helpers redact credentials in URLs, never dump the environment, and the tests scan for committed tokens and keys.
- **Verified.** CI runs the test suite on Python 3.9 and 3.12, runs shellcheck on every script, and fails when generated host files drift from `manifest.json`.

## Install

The one-liner above installs every skill. Variations:

```sh
npx skills add Alex72-py/termux-elite --list                          # see what is inside
npx skills add Alex72-py/termux-elite --skill python-native-build     # just one
npx skills add Alex72-py/termux-elite -g                              # all projects, not just this one
```

Inside Termux itself, `npx` needs Node: `pkg install nodejs`.

Native installs for each host:

| Host | Install |
| --- | --- |
| Claude Code | `/plugin marketplace add Alex72-py/termux-elite`, then `/plugin install termux-elite@termux-elite` |
| Antigravity CLI (`agy`) | `agy plugin install https://github.com/Alex72-py/termux-elite.git` |
| Gemini CLI | `gemini skills install https://github.com/Alex72-py/termux-elite.git --path skills` (or `gemini extensions install https://github.com/Alex72-py/termux-elite`) |
| OpenCode | `sh scripts/install.sh opencode` |
| Codex | `codex plugin marketplace add https://github.com/Alex72-py/termux-elite`, then `codex plugin add termux-elite@termux-elite` |
| Cursor | `/add-plugin Alex72-py/termux-elite` |
| Kiro and others | `sh scripts/install.sh kiro` or `sh scripts/install.sh agents` |

No Node needed from a clone. The installer works on any host that reads skill directories, including inside Termux:

```sh
git clone https://github.com/Alex72-py/termux-elite.git
cd termux-elite
sh scripts/install.sh claude --dry-run    # see what would change
sh scripts/install.sh claude              # install (managed copy)
sh scripts/install.sh claude --uninstall  # remove only what it installed
```

It copies by default (`--link` symlinks), supports `--project` and `--skill NAME`, and never overwrites or removes a skill it did not install. Per-host paths and caveats are in [adapters/](adapters/).

## FAQ

**Is this a shell or a framework?** No. It is a knowledge and procedure layer. The agent still owns confirmation and execution.

**Does it run commands on my phone?** Only the agent does, through its normal tool permissions. The bundled helper scripts are read-only and print facts.

**Will it work on a normal Linux machine?** It is written for Termux, Android, and proot, and says so when a fact is Android-specific. A few skills (`github-actions`, `git-credentials`) are useful anywhere, but the focus is the phone.

**Can I route from my own agent?** Yes. Anything that can read files can route from `manifest.json`. See [adapters/generic](adapters/generic/README.md).

## Help it cover more failures

The most useful contribution is a real failure that no skill handled, or one where a skill gave the wrong advice. Open a **failure report** issue with your Android and Termux versions and the first error line (redact secrets). If the failure is a repeatable decision, it may become a new skill: see [CONTRIBUTING.md](CONTRIBUTING.md) for the quality bar and [docs/SKILL_TEMPLATE.md](docs/SKILL_TEMPLATE.md) to start one.

## Repository layout

```text
skills/<name>/SKILL.md         the procedure (Agent Skills frontmatter: name, description, license, compatibility, metadata)
skills/<name>/scripts/         small read-only helpers that print key: value facts
manifest.json                  discovery index (name, triggers, capabilities, risk, related, scripts)
AGENTS.md                      generated routing index and rules, for hosts that load context files
scripts/install.sh             installer for hosts that read skill directories
scripts/sync_hosts.py          generates host manifests and AGENTS.md from manifest.json
adapters/<host>/               notes for each host
docs/SKILL_TEMPLATE.md         starting point for a new skill
tests/                         manifest, frontmatter, section, handoff, script, host and installer checks
```

The plugin manifests (`.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.agents/plugins/`, `plugin.json`, `gemini-extension.json`) are generated; do not edit them by hand.

## Develop

```sh
python -m pip install pytest pyyaml
python scripts/sync_hosts.py --check
python -m pytest -q
```

## Design rules

1. Inspect before mutating.
2. Never assume native Termux, Android, Linux, or proot are interchangeable.
3. Treat package installs, permission changes, config edits, and service changes as mutating actions that need confirmation.
4. Never print secrets or broad environment dumps.
5. Verify the original failure after a change and record how to roll back.
6. Mark version-specific claims; keep helper scripts auditable and dependency-light.

[MIT](LICENSE)
