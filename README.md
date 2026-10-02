# termux-elite

![ci](https://github.com/Alex72-py/termux-elite/actions/workflows/ci.yml/badge.svg)

Operational skills for AI coding agents working inside Termux and Android. Each skill is a short, verified procedure: what to inspect first, which layer is failing, what is safe to change, how to confirm the fix, and what to hand off.

This repository is a knowledge and procedure layer, not a shell or framework. The agent still owns confirmation and execution.

## Skills

| Skill | What it decides | Risk |
| --- | --- | --- |
| `termux-environment` | Take a small read-only snapshot of a Termux or Android shell (native or proot, Android and Termux version, CPU architecture, installed toolchains, free storage and memory) before choosing a package manager, path, or fix. | low |
| `python-native-build` | Diagnose a failed Python install on Termux or Android (compiler or header errors, Rust or maturin builds, no wheel for this platform, glibc wheels that fail at import, externally-managed-environment) and pick the smallest fix, preferring Termux-packaged libraries over source builds. | medium |
| `package-troubleshooting` | Diagnose pkg and apt failures on Termux (unable to locate package, stale or wrong mirrors, clock skew, hash mismatch, interrupted dpkg, libraries that fail to link after a partial upgrade) and separate them from build failures. | medium |
| `storage-permissions` | Explain why a path is unreadable or unwritable on Termux (missing storage link, revoked Android permission, scoped storage, a filesystem without Unix modes or symlinks, a proot bind that was never made) and choose where files should live. | low |
| `proot-boundaries` | Decide whether a failure belongs to native Termux or a proot distro and which side should own the package, interpreter, and project path. | medium |
| `github-actions` | Investigate a failed GitHub Actions run from Termux without exposing credentials or guessing at the workflow. | low |
| `termux-api` | Attribute a hanging, empty, or failing termux-* command to the right layer (Termux:API app, termux-api package, or an Android runtime permission) before relying on it. | low |
| `background-processes` | Decide whether a long-running Termux process exited, was suspended, or was killed by Android, and apply the smallest mitigation (lower parallelism, wake lock, battery settings, tmux, or the phantom process limit as a last resort). | medium |
| `git-credentials` | Diagnose git clone, fetch, and push authentication failures from Termux without exposing tokens or private keys (HTTPS tokens, SSH keys, host key prompts, wrong account, missing scopes). | medium |
| `node-native-build` | Diagnose npm and Node installs that fail on Termux (node-gyp errors such as android_ndk_path, missing compilers, packages with no android binary, optional platform dependencies, out-of-memory builds) and pick the smallest fix, including WASM fallbacks. | medium |
| `termux-services` | Choose how to keep a program running on Termux (tmux or nohup, Termux:Boot, or termux-services with runit) and set it up with supervision and logs. | medium |
| `termux-sshd` | Set up, harden, and debug the OpenSSH server on Termux (port 8022, key authentication, connection refused, permission denied, host key warnings). | medium |
| `termux-backup` | Create and verify a restorable snapshot of Termux home and prefix before risky changes, and restore it safely. | medium |
| `termux-network` | Diagnose network problems inside Termux (DNS, TLS certificate errors, clock skew, proxies, binding ports, reaching a Termux server from the phone or LAN) given Android's restrictions on interfaces and low ports. | low |

Every skill follows one standard (see [CONTRIBUTING.md](CONTRIBUTING.md)): a description written to trigger on real symptoms, a decision tree that starts with the cheapest read-only check, explicit safety and rollback, a verification command, handoffs to sibling skills, and a short report contract.

## Install

| Host | Install |
| --- | --- |
| Claude Code | `/plugin marketplace add Alex72-py/termux-elite`, then `/plugin install termux-elite@termux-elite` |
| Antigravity CLI (`agy`) | `agy plugin install https://github.com/Alex72-py/termux-elite.git` |
| Gemini CLI | `gemini skills install https://github.com/Alex72-py/termux-elite.git --path skills` (or `gemini extensions install https://github.com/Alex72-py/termux-elite`) |
| OpenCode | `sh scripts/install.sh opencode` |
| Codex | `codex plugin marketplace add https://github.com/Alex72-py/termux-elite`, then `codex plugin add termux-elite@termux-elite` |
| Cursor | `/add-plugin Alex72-py/termux-elite` |
| Kiro and others | `sh scripts/install.sh kiro` or `sh scripts/install.sh agents` |

From a clone, the installer works on any host that reads skill directories, including inside Termux itself:

```sh
git clone https://github.com/Alex72-py/termux-elite.git
cd termux-elite
sh scripts/install.sh claude --dry-run    # see what would change
sh scripts/install.sh claude              # install (managed copy)
sh scripts/install.sh claude --uninstall  # remove only what it installed
```

The installer copies by default (use `--link` to symlink), supports `--project` and `--skill NAME`, and never overwrites or removes a skill it did not install. Per-host details, discovery paths, and caveats are in [adapters/](adapters/).

## Layout

```text
manifest.json                  discovery index (name, triggers, capabilities, risk, related, scripts)
skills/<name>/SKILL.md         the procedure (Agent Skills layout: name + description frontmatter)
skills/<name>/scripts/         small read-only helpers that print key: value facts
AGENTS.md                      generated routing index and rules, for hosts that load context files
scripts/install.sh             installer for hosts that read skill directories
scripts/sync_hosts.py          generates host manifests and AGENTS.md from manifest.json
.claude-plugin/ plugin.json gemini-extension.json .codex-plugin/ .cursor-plugin/ .agents/plugins/
                               generated host manifests (do not edit by hand)
adapters/<host>/               notes for each host
docs/SKILL_TEMPLATE.md         starting point for a new skill
tests/                         manifest, frontmatter, section, handoff, script, host and installer checks
```

## Use it from your own agent

Any agent that can read files can route from `manifest.json`. See [adapters/generic](adapters/generic/README.md) for a short example.

## Verify the repository

```sh
python -m pip install pytest pyyaml
python scripts/sync_hosts.py --check
python -m pytest -q
```

The tests check that every skill is consistent with its manifest entry, that descriptions are discoverable and valid YAML, that handoffs point at real skills, that helper scripts are executable, read-only, and agree with `SKILL.md`, that generated host files are current, that the installer behaves safely for every host, and that no secrets are committed.

## Design rules

1. Inspect before mutating.
2. Never assume native Termux, Android, Linux, or proot are interchangeable.
3. Treat package installs, permission changes, config edits, and service changes as mutating actions that need confirmation.
4. Never print secrets or broad environment dumps.
5. Verify the original failure after a change and record how to roll back.
6. Mark version-specific claims; keep helper scripts auditable and dependency-light.
