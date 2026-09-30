---
name: github-actions
description: Investigate failed GitHub Actions runs from local repositories without exposing credentials.
triggers: github action failed,workflow failed,ci failed
risk: low
---
# GitHub Actions Investigation

## Purpose
Turn a failed workflow into a reproducible local diagnosis without leaking tokens or blindly editing workflow files.

## Preconditions
Confirm the repository with `git remote -v` and current branch/commit. Prefer `gh run list` and `gh run view` when the user is authenticated; otherwise use the run URL and local logs.

## Decision tree
1. Identify the failed job and first failing step, not merely the final summary.
2. Separate runner/permissions failures, dependency resolution, platform mismatch, test failures, and flaky/network failures.
3. Compare workflow OS, Python/Node versions, architecture, and services with the local Termux environment.
4. Reproduce deterministic failures locally when practical; do not claim local success proves runner success.
5. Suggest the smallest workflow change and show the exact file/line before editing.

## Safety
Never print `GITHUB_TOKEN`, cloud credentials, SSH private keys, or full environment dumps. Reading run metadata is safe; pushing workflow changes requires explicit user intent and normal repository review.

## Verification
After a fix, run the relevant local test and explain what still depends on the hosted runner.
