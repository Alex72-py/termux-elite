---
name: background-processes
description: Decide whether a long-running Termux process exited, was suspended, or was killed by Android, and apply the smallest mitigation (lower parallelism, wake lock, battery settings, tmux, or the phantom process limit as a last resort). Use when a server, build, download, or script dies with the screen off, after Termux leaves the foreground, or with signal 9, exit code 137, or Process completed (signal 9). Do NOT use to tune Android settings for a process that simply exited with its own error.
triggers: process killed,signal 9,exit code 137,background process,wake lock,phantom process,dies when screen off,process completed
risk: medium
---
# Background Processes

## Purpose
Decide whether a long-running process exited, was suspended, or was killed by Android, and choose the smallest mitigation that fixes it.

## When to use
A server, build, download, or script stops while the screen is off, after Termux leaves the foreground, or with `signal 9`, exit status 137, or `Process completed (signal 9)`.

## When NOT to use
- The process ended with its own error. Read its log and exit status first.
- Starting a program at boot or restarting it after a crash: that is `termux-services`.

## Preconditions
Capture, read-only: exit status or last log lines, how long it ran, whether the screen was off, Android API level, and how many child processes the task spawns. `sh scripts/check-process-limits.sh` prints Android level, CPU count, memory, and a suggested job count.

## Decision tree
1. Confirm it was killed, not finished: exit status 137 is SIGKILL (128 plus 9); 143 is SIGTERM; check the log tail and whether Termux itself was stopped.
2. Dies soon after the screen turns off: the CPU was suspended. `termux-wake-lock` (or the wake lock action in the Termux notification) prevents it at a battery cost.
3. Dies after Termux is swiped away or in the background: check battery optimization for Termux. Vendor task killers add their own limits (Xiaomi, Huawei, Samsung and others; see dontkillmyapp.com). These are user-level settings; guide the user, do not act.
4. Dies mid-build with `Killed`: out of memory. Lower parallelism first (`make -jN`, `MAKEFLAGS`, `CMAKE_BUILD_PARALLEL_LEVEL`) using the suggested job count.
5. `signal 9` while many child processes run on Android 12 or later: suspect the phantom process limit (a cap on background child processes, 32 by default). Reduce parallelism first. Newer releases expose a developer option to disable child process restrictions; older ones need an `adb` setting change. The `adb` change is system-wide and a last resort.
6. `tmux`, `screen`, and `nohup` survive a closed terminal session, not Android killing the Termux app.

## Safety
Wake locks and battery exemptions cost battery. Any `adb` setting change is system-wide: read and record the current value first, state the exact change and how to revert it, and get explicit confirmation. Never suggest root-only workarounds by default.

## Verification
Re-run the task for at least as long as the original failure took, with the screen off if that was the trigger, then confirm the process is alive (`pgrep -f <name>`) and output is complete.

## Rollback
Release the wake lock with `termux-wake-unlock` when finished and restore any recorded Android setting to its original value.

## Handoffs
- `termux-services` for supervision, restart on crash, and start at boot.
- `termux-environment` for Android level and memory facts.
- `python-native-build` when the killed process is a Python build.
- `node-native-build` when the killed process is a Node build.
- `termux-sshd` when SSH sessions drop because Termux is suspended.

## Report
Kill versus exit versus suspend, the evidence (status code, timing), the one mitigation applied, and the verification run length.
