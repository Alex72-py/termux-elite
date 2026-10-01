---
name: background-processes
description: Diagnose long-running processes that Android suspends or kills and choose the smallest mitigation.
triggers: process killed,signal 9,background process,wake lock,phantom process
risk: medium
---
# Background Processes

## Purpose
Decide whether a long-running Termux process exited, was suspended, or was killed by Android, and choose the smallest mitigation that fixes it.

## When to use
Use when a server, build, download, or script dies while the screen is off, after Termux leaves the foreground, or with `signal 9` / `Process completed (signal 9)`.

## When NOT to use
Do not tune Android settings for a process that simply exited with its own error. Read its log and exit status first.

## Preconditions
Capture the exit status or last log lines, how long the process ran before dying, whether the screen was off, the Android version, and roughly how many child processes the task spawns.

## Decision tree
1. Confirm the process was killed rather than finished: check exit status, logs, and whether Termux itself was stopped.
2. Dies shortly after the screen turns off: Android suspended the CPU. `termux-wake-lock` (or the wake lock action in the Termux notification) keeps it awake at a battery cost.
3. Dies after Termux is swiped away or restricted: check Android battery optimization and any vendor background restrictions for Termux. Changing them is a user-level setting; guide the user rather than acting.
4. `signal 9` while many child processes run on Android 12 or later: suspect the phantom process killer. First reduce parallelism (fewer jobs, no wide `make -j`). Newer Android releases expose a developer option to disable child process restrictions; older ones need an `adb` change to a system-wide setting.
5. `tmux`, `screen`, and `nohup` survive a closed terminal session, not Android killing the Termux app.

## Safety
Wake locks and battery exemptions cost battery. Any `adb` setting change is system-wide: read and record the current value first, state the exact change and how to revert it, and get explicit confirmation. Never suggest root-only workarounds as a default.

## Verification
Re-run the task for at least as long as the original failure took, with the screen off if that was the trigger, and confirm the process is still alive (`pgrep`) and the output is complete.

## Rollback
Release the wake lock when finished and restore any recorded Android setting to its original value.
