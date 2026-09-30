---
name: proot-boundaries
description: Determine whether a failure belongs to native Termux or a proot distro and choose the right package boundary.
triggers: proot,proot-distro,ubuntu in termux,native termux
risk: medium
---
# Native Termux and proot Boundaries

## Purpose
Prevent packages, paths, and assumptions from leaking across the native Termux and proot environments.

## When to use
Use when a command behaves differently in Ubuntu/Debian under Termux, when Android APIs are unavailable, or when a native build/package decision is unclear.

## Detect environment
Collect `uname -a`, `$PREFIX`, `command -v pkg apt`, `/proc/1/root`, and proot-distro state. Treat a prompt label alone as unreliable.

## Decision tree
1. Native Termux uses Android/Bionic assumptions and `pkg`.
2. A proot distro has its own userspace and package manager, but still runs under Android constraints.
3. Android-facing commands such as Termux:API, storage links, and `termux-*` binaries usually belong to the native side.
4. Build dependencies for a process should be installed in the environment that launches that process.
5. Cross-boundary paths and networking must be tested rather than assumed.

## Safety
Installing or removing a proot distro is a mutating operation. Do not recommend `proot-distro reset` as a generic repair; it can destroy the distro filesystem.

## Verification
Report which side owns the process, package manager, Python interpreter, and project path before proposing a fix.
