# termux-elite

![ci](https://github.com/Alex72-py/termux-elite/actions/workflows/ci.yml/badge.svg)

Portable operational skills for agents working inside Termux and Android environments.

This repository is a **knowledge and procedure layer**, not a replacement shell, framework, or collection of copy-paste commands. Each skill encodes when to inspect the environment, how to choose among native Termux and proot paths, what can fail, what is safe to change, and how to verify the result.

## Included skills

| Skill | Purpose | Risk |
| --- | --- | --- |
| `termux-environment` | Low-cost environment and capability detection | low |
| `python-native-build` | Python packages that need native libraries, compilers, or Rust | medium |
| `package-troubleshooting` | `pkg`/`apt` diagnosis and repository boundaries | medium |
| `storage-permissions` | Android shared-storage and permission diagnosis | low |
| `proot-boundaries` | Native Termux versus proot decision procedure | medium |
| `github-actions` | Safe investigation of failed workflow runs | low |
| `termux-api` | Termux:API app, package, and permission diagnosis | low |
| `background-processes` | Processes suspended or killed by Android | medium |
| `git-credentials` | Git HTTPS/SSH authentication without leaking secrets | medium |

The skills are intentionally focused. New skills should earn their place by encoding a repeatable operational decision, not by restating platform documentation. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Layout

```text
manifest.json
skills/<name>/SKILL.md
skills/<name>/scripts/       # small, read-only helpers where useful
skills/<name>/references/    # deeper material, when needed
adapters/<agent>/             # integration notes for a host agent
examples/
docs/                         # skill template
tests/                        # manifest, frontmatter, and script checks
.github/workflows/ci.yml
```

`manifest.json` is the discovery interface. It records name, description, triggers, required capabilities, platform, risk, and the path to the skill document.

## Minimal host integration

```python
import json, pathlib

root = pathlib.Path("termux-elite")
manifest = json.loads((root / "manifest.json").read_text())
request = "pip install cryptography failed with a build error"
hits = [s for s in manifest["skills"] if any(t in request.lower() for t in s["triggers"])]
print([s["path"] for s in hits])
```

Read the selected `SKILL.md` before proposing commands. The host agent still owns confirmation and execution.

## Use from ARIA

Set the optional skill root before starting ARIA:

```sh
export ARIA_SKILLS_PATH="$HOME/src/termux-elite"
python run_aria.py
```

ARIA can also consume any directory with the same `manifest.json` and `skills/*/SKILL.md` shape. The dependency is optional; ARIA remains usable when the repository is unavailable.

## Tool-agnostic integration

Adapters explain how a host agent can expose the same files as searchable skills. They do not contain private prompts or proprietary implementation details. The core `SKILL.md` files remain the source of truth.

## Verify the repository

```sh
python -m pip install pytest
python -m pytest -q
```

The tests check that every skill is listed in the manifest, that `SKILL.md` frontmatter matches the manifest, that required sections exist, that helper scripts are valid and read-only, and that no obvious secrets are committed.

## Design rules

1. Inspect before mutating.
2. Never assume native Termux, Android, Linux, or proot are interchangeable.
3. Treat package installation, permission changes, repository edits, and service changes as mutating actions.
4. Do not print secrets or broad environment dumps.
5. Verify the original failure after a change and record rollback information.
6. Keep helper scripts auditable and dependency-light.
