---
name: package-troubleshooting
description: Choose pkg versus apt, repair repository metadata and separate package from build failures.
triggers: pkg failed,apt failed,package not found,repository error
risk: medium
---
# Package Troubleshooting

## Purpose
Diagnose package-manager failures without treating every error as a reason to reset repositories or run broad upgrades.

## When to use
Use for `pkg`/`apt` resolution failures, repository errors, broken package state, missing packages, or native dependency lookup.

## When NOT to use
Do not run `pkg upgrade`, change mirrors, or remove package metadata before capturing the exact error and environment.

## Preconditions
Identify whether the shell is native Termux or proot. Record `command -v pkg apt`, `pkg --version` or `apt --version`, and the requested package name.

## Decision tree
1. Native Termux normally uses `pkg`; a proot distro normally uses its own `apt`.
2. If the package is not found, distinguish stale indexes, wrong repository/component, architecture availability, and an actually absent package.
3. If resolution succeeds but compilation fails, hand off to `python-native-build` or a native-toolchain skill.
4. If repository metadata is corrupt, preserve the error and repair the smallest affected state; avoid destructive cache deletion as a first step.

## Procedure
Run read-only status and search commands first. Present any mirror, upgrade, or package installation as a separate confirmed action. Verify with the original package query and a version/path check.

## Safety
Package installation and upgrades mutate the environment and may consume substantial storage or break pinned dependencies. Guardian confirmation is required.
