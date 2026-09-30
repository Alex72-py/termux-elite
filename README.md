# termux-elite

Portable operational skills for agents working inside Termux and Android environments.

This repository is a **knowledge and procedure layer**, not a replacement shell, framework, or collection of copy-paste commands. Each skill encodes when to inspect the environment, how to choose among native Termux and proot paths, what can fail, what is safe to change, and how to verify the result.

## Included skills

- `termux-environment`: low-cost environment and capability detection
- `python-native-build`: Python packages that need native libraries, compilers, or Rust
- `package-troubleshooting`: `pkg`/`apt` diagnosis and repository boundaries
- `storage-permissions`: Android shared-storage and permission diagnosis
- `proot-boundaries`: native Termux versus proot decision procedure
- `github-actions`: safe investigation of failed workflow runs

The initial skills are intentionally focused. New skills should earn their place by encoding a repeatable operational decision, not by restating platform documentation.

## Layout

```text
manifest.json
skills/<name>/SKILL.md
skills/<name>/scripts/       # small, read-only helpers where useful
skills/<name>/references/    # deeper material, when needed
adapters/<agent>/             # integration notes for a host agent
examples/
tests/
```

`manifest.json` is the discovery interface. It records name, description, triggers, required capabilities, platform, risk, and the path to the skill document.

## Use from ARIA

Set the optional skill root before starting ARIA:

```sh
export ARIA_SKILLS_PATH="$HOME/src/termux-elite"
python run_aria.py
```

ARIA can also consume any directory with the same `manifest.json` and `skills/*/SKILL.md` shape. The dependency is optional; ARIA remains usable when the repository is unavailable.

## Tool-agnostic integration

Adapters explain how a host agent can expose the same files as searchable skills. They do not contain private prompts or proprietary implementation details. The core `SKILL.md` files remain the source of truth.

## Design rules

1. Inspect before mutating.
2. Never assume native Termux, Android, Linux, or proot are interchangeable.
3. Treat package installation, permission changes, repository edits, and service changes as mutating actions.
4. Do not print secrets or broad environment dumps.
5. Verify the original failure after a change and record rollback information.
6. Keep helper scripts auditable and dependency-light.
