---
name: termux-api
description: Determine whether Termux:API is installed, matched, and permitted before relying on termux-* commands.
triggers: termux-api,termux api,termux-battery-status,termux command hangs
risk: low
---
# Termux:API

## Purpose
Separate three independent requirements — the Termux:API Android app, the `termux-api` package, and Android runtime permissions — so a hanging or failing `termux-*` command is attributed to the right layer.

## When to use
Use when a `termux-*` command (for example `termux-battery-status`, `termux-clipboard-get`, `termux-notification`) hangs, prints nothing, or reports a permission error.

## When NOT to use
Do not use for ordinary shell, package, or storage failures. Storage links belong to `storage-permissions`; processes running inside proot belong to `proot-boundaries`.

## Preconditions
Native Termux only; `termux-*` commands are usually not usable from inside a proot distro. Run `sh scripts/check-termux-api.sh` for a bounded, read-only check.

## Decision tree
1. No `termux-*` binaries on `PATH`: the `termux-api` package is missing in this environment.
2. Binaries exist but calls time out or hang: the Termux:API Android app is probably not installed, was stopped, or is restricted by battery optimization.
3. App and package are both present but calls fail: Termux and its plugin apps should come from the same distribution source; mixed signing sources commonly break plugin communication.
4. One command reports a permission error: the matching Android runtime permission (location, SMS, camera, contacts, and similar) is not granted to Termux:API. Fix it in Android settings, not by changing Unix file modes.
5. Always wrap API calls in `timeout` so a missing app cannot block the agent.

## Safety
Many commands expose sensitive data (location, SMS, contacts, clipboard, call log). Request only the one capability the task needs, do not echo results beyond what the task requires, and ask before any command that sends, calls, writes, or notifies.

## Verification
Run one harmless read such as `timeout 10 termux-battery-status` and confirm it returns structured output.
