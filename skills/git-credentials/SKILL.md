---
name: git-credentials
description: Diagnose git clone and push authentication from Termux without exposing tokens or private keys.
triggers: git push failed,permission denied publickey,authentication failed,ssh key
risk: medium
---
# Git Credentials

## Purpose
Diagnose `git clone`, `fetch`, and `push` authentication failures in Termux without exposing tokens or private keys.

## When to use
Use for `Authentication failed`, HTTP 403, `Permission denied (publickey)`, repeated credential prompts, or SSH key problems.

## When NOT to use
Do not use for network outages, wrong remote names, or non-authentication push rejections such as non-fast-forward errors.

## Preconditions
Run `git remote -v` and inspect only the URL scheme and host. If the URL embeds a token (`https://user:secret@host/...`), do not print it back; treat the embedded credential as a finding to fix.

## Decision tree
1. HTTPS remote failing with authentication errors: GitHub does not accept account passwords for git operations. Use a personal access token with minimal scope or `gh auth login`; `gh auth status` does not print the token.
2. SSH remote failing with `Permission denied (publickey)`: list key file names in `~/.ssh` (never contents of private keys), confirm the matching `.pub` is registered with the account, and test with `ssh -T git@github.com`.
3. `UNPROTECTED PRIVATE KEY FILE`: `~/.ssh` should be mode 700 and private keys mode 600. Keys on shared storage cannot hold these modes; keep them under `$HOME` (see `storage-permissions`).
4. Key works only sometimes: Termux does not start an ssh-agent for you. Name the key with `IdentityFile` in `~/.ssh/config` or start an agent per session.
5. Prefer one method per remote. Do not mix an embedded token and SSH on the same repository.

## Safety
Generating keys, editing `~/.ssh/config`, storing credentials, and changing remotes are mutating actions that need confirmation. Never paste tokens or private keys into chat, logs, commits, or remote URLs. Only a `.pub` file is safe to display.

## Verification
Run the read-only `git ls-remote origin` and confirm it lists refs without prompting. Perform an actual push only when the user asks for it.
