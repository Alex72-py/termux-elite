---
name: termux-environment
description: Detect native Termux, Android, architecture, tools, storage and resource constraints.
triggers: termux environment,android environment,what is installed
risk: low
---
# Termux Environment

## Purpose
Build a small factual snapshot before choosing a package manager, filesystem path, or Android integration strategy.

## When to use
Use when a request depends on Android, Termux, architecture, available binaries, storage, RAM, or whether the shell is native or inside another environment.

## When NOT to use
Do not run a full inventory for an ordinary text question or before every command. Cache the result and refresh after an environment change.

## Preconditions
Only read-only shell access is required. Do not require root, Termux:API, or network access.

## Detect environment
Run `scripts/detect-environment.sh`. Record `uname -srm`, `PREFIX`, `TERMUX_VERSION`, package-manager availability, Python version, and whether `$HOME/storage/shared` exists. Check `/proc/1/root` and `PROOT_TMP_DIR` as hints, not proof.

## Decision tree
1. If `PREFIX` points under `/data/data/com.termux`, treat the shell as native Termux.
2. If `proot-distro` or proot markers are present, identify the distro separately; do not mix its packages with native Termux packages.
3. Choose architecture from `uname -m`, not an assumed phone model.
4. If shared storage is absent, treat Android storage permission as unresolved rather than as a generic Unix permission error.

## Verification
Report only facts relevant to the requested operation. Keep the raw snapshot available for later tools.

## Safety
All checks are read-only. Never modify storage, install packages, or request permissions from this skill.
