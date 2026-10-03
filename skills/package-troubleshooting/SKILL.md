---
name: package-troubleshooting
description: Diagnose pkg and apt failures on Termux (unable to locate package, stale or wrong mirrors, clock skew, hash mismatch, interrupted dpkg, libraries that fail to link after a partial upgrade) and separate them from build failures. Use when pkg or apt prints an error, when a Debian or Ubuntu package name is missing, or when a command dies with CANNOT LINK EXECUTABLE. Do NOT use to run broad upgrades, change mirrors, or clear caches before capturing the exact error, and do not use for compile errors (see python-native-build).
triggers: pkg failed,apt failed,package not found,repository error,unable to locate package,cannot link executable,hash sum mismatch,dpkg interrupted
risk: medium
---
# Package Troubleshooting

## Purpose
Diagnose package-manager failures without treating every error as a reason to reset repositories or run a broad upgrade.

## When to use
- `pkg` or `apt` fails to resolve, download, verify, or configure a package.
- A package name from Debian or Ubuntu does not exist.
- A binary fails with `CANNOT LINK EXECUTABLE` or a missing `.so` after an upgrade.

## When NOT to use
- Compile or wheel failures after the package manager succeeded: use `python-native-build` or `node-native-build`.
- Inside proot: that side has its own `apt`; use `proot-boundaries` first.
- Do not run `pkg upgrade`, change mirrors, or clear package state before capturing the exact error.

## Preconditions
Capture, read-only: the full error, the requested package, `dpkg --print-architecture`, the current date, and free space. `sh scripts/check-pkg-state.sh` collects these without secrets.

## Decision tree
1. Native Termux uses `pkg` (a wrapper around `apt`). A proot distro uses its own `apt`.
2. `Release file ... is not valid yet` or TLS date errors: the device clock is wrong. Fix the date (automatic time in Android settings) before touching repositories.
3. Many unrelated `pkg` failures on an old install: check the install source. The Google Play build of Termux is deprecated and no longer updated, so its repositories and packages fall behind. `TERMUX_APK_RELEASE` (printed as `termux_apk_release` by the `termux-environment` helper) is `F_DROID`, `GITHUB`, `GOOGLE_PLAY_STORE`, or `UNKNOWN`. Moving to another source generally means uninstalling and reinstalling, because builds from different sources are signed with different keys, so it destroys app data. Recommend `termux-backup` first and never do it without confirmation.
4. `Unable to locate package`: stale indexes, a Debian-style name, or an absent package. Termux package names differ from Debian. Examples: `python3-dev` has no equivalent (headers ship with `python`); `libssl-dev` is `openssl`; `build-essential` is `clang make`; `libffi-dev` is `libffi`. Search with `pkg search <word>` before concluding it is absent.
5. `Hash Sum mismatch` or a 404 or timeout from a mirror: the mirror is out of sync or down. Retry once, then consider a different mirror (a confirmed, separate action).
6. `dpkg was interrupted`, `Sub-process dpkg returned an error`: preserve the output, then the repair is `dpkg --configure -a`, a mutating step that needs confirmation.
7. `CANNOT LINK EXECUTABLE ... library "lib....so" not found`: usually a partial upgrade. Termux does not support partial upgrades; the fix is a complete `pkg update` followed by `pkg upgrade`, confirmed by the user.
8. `No space left on device`: check free space; `pkg clean` removes downloaded archives only.
9. Never copy Debian or Ubuntu `sources.list` entries into Termux. Different libc, different paths: it breaks the installation.
10. Resolution succeeds but compilation fails: hand off.

## Safety
`pkg install`, `pkg upgrade`, `pkg update`, mirror changes (`termux-change-repo`), and dpkg repair all mutate local state and can use large storage or break pinned dependencies. Run read-only status and search first, present each change separately, and get confirmation.

## Verification
Re-run the original package query, then check version and path (`pkg show <name>`, `command -v <tool>`).

## Rollback
Note package versions before changing them (`pkg list-installed <name>`). Metadata-only changes such as an index refresh need no rollback. For a mirror change, keep the previous `sources.list` content in the report so it can be restored.

## Handoffs
- `termux-environment` when architecture or side is unknown.
- `proot-boundaries` when the shell may be a proot distro.
- `python-native-build` when the package installed but the build failed.
- `termux-network` when downloads fail for DNS or TLS reasons.
- `termux-backup` before a large upgrade on a device that holds irreplaceable state.

## Report
The first real error, the layer it belongs to (clock, index, mirror, dpkg state, partial upgrade, space), the change applied, and the verification result.
