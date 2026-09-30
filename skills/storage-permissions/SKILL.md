---
name: storage-permissions
description: Diagnose Android shared-storage access and Termux permission boundaries.
triggers: storage permission,permission denied android,shared storage
risk: low
---
# Android Storage Permissions

## Purpose
Explain whether a path is native Termux storage, a shared-storage link, a proot-visible path, or an Android permission boundary.

## When to use
Use for `Permission denied`, missing `~/storage`, inability to access `/sdcard`, or a tool that works in Termux but not inside proot.

## Preconditions
Inspect `pwd`, `$HOME`, `PREFIX`, `ls -ld ~/storage ~/storage/shared` when present, and the failing path. Do not print unrelated private filenames.

## Decision tree
1. If `~/storage/shared` is absent in native Termux, storage permission may not have been granted or the storage link may not exist.
2. A path visible to native Termux may not be writable or mounted inside proot.
3. A Unix mode bit is not proof that Android permission is granted.
4. Ask before running `termux-setup-storage`; it changes user-visible storage links and requires Android interaction.
5. Prefer project files inside `$HOME` when shared storage is not required; shared storage can have performance and permission differences.

## Verification
After permission changes, verify only the requested path with a harmless read/write test chosen by the user. Never create files in shared storage without approval.
