# termux-elite

Operational skills for agents working in Termux and Android. Load the single skill whose triggers match the request; do not load them all.

## Skills

| Skill | Use when the request mentions | Risk |
| --- | --- | --- |
| `termux-environment` | termux environment, android environment, what is installed, which architecture | low |
| `python-native-build` | pip failed, python package install, wheel unavailable, build error | medium |
| `package-troubleshooting` | pkg failed, apt failed, package not found, repository error | medium |
| `storage-permissions` | storage permission, permission denied android, shared storage, sdcard | low |
| `proot-boundaries` | proot, proot-distro, ubuntu in termux, native termux | medium |
| `github-actions` | github action failed, workflow failed, ci failed, passes locally fails on ci | low |
| `termux-api` | termux-api, termux api, termux-battery-status, termux command hangs | low |
| `background-processes` | process killed, signal 9, exit code 137, background process | medium |
| `git-credentials` | git push failed, permission denied publickey, authentication failed, ssh key | medium |
| `node-native-build` | npm install failed, node-gyp, android_ndk_path, unsupported platform android | medium |
| `termux-services` | termux-services, termux boot, run on boot, autostart | medium |
| `termux-sshd` | termux sshd, ssh into phone, port 8022, connection refused termux | medium |
| `termux-backup` | backup termux, restore termux, migrate termux, snapshot termux | medium |
| `termux-network` | termux no internet, dns failure, certificate verify failed, ifconfig empty | low |
| `termux-adb` | adb pair, adb connect, wireless debugging, adb devices | medium |

## Rules

1. Inspect before mutating. Each skill names a read-only helper in `scripts/`; run it first.
2. Native Termux, proot, and Android are not interchangeable. Establish the side with `termux-environment` when unsure.
3. Package installs, permission changes, config edits, and service changes mutate state: state the exact change and get confirmation.
4. Never print tokens, private keys, or full environment dumps.
5. After a change, re-run the original failing command. Report root cause, the change, the verification result, and any remaining limit.

## Layout

`skills/<name>/SKILL.md` is the procedure, `skills/<name>/scripts/` holds read-only helpers, and `manifest.json` is the machine-readable index.

## Working on this repository

Read `CONTRIBUTING.md`. After changing a skill or `manifest.json`, run `python scripts/sync_hosts.py` and `python -m pytest -q`.
