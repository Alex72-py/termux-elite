#!/usr/bin/env python3
"""Generate host integration files from manifest.json.

    python scripts/sync_hosts.py           write the generated files
    python scripts/sync_hosts.py --check   exit 1 if any generated file is stale
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTHOR = {"name": "Alex72-py", "url": "https://github.com/Alex72-py"}
REPOSITORY = "https://github.com/Alex72-py/termux-elite"
KEYWORDS = ["termux", "android", "agent-skills", "proot", "mobile", "devops"]


def dump(obj):
    return json.dumps(obj, indent=2) + "\n"


def agents_md(manifest):
    rows = ["| Skill | Use when the request mentions | Risk |", "| --- | --- | --- |"]
    for skill in manifest["skills"]:
        rows.append("| `%s` | %s | %s |" % (skill["name"], ", ".join(skill["triggers"][:4]), skill["risk_level"]))
    table = "\n".join(rows)
    return """# {name}

Operational skills for agents working in Termux and Android. Load the single skill whose triggers match the request; do not load them all.

## Skills

{table}

## Rules

1. Inspect before mutating. Each skill names a read-only helper in `scripts/`; run it first.
2. Native Termux, proot, and Android are not interchangeable. Establish the side with `termux-environment` when unsure.
3. Package installs, permission changes, config edits, and service changes mutate state: state the exact change and get confirmation.
4. Never print tokens, private keys, or full environment dumps.
5. After a change, re-run the original failing command. Report root cause, the change, the verification result, and any remaining limit.

## Layout

`skills/<name>/SKILL.md` is the procedure, `skills/<name>/scripts/` holds read-only helpers, and `manifest.json` is the machine-readable index.

## Working on this repository

Read `CONTRIBUTING.md`. After changing a skill or `manifest.json`, run `python scripts/sync_hosts.py` and `python -m pytest -q`.
""".format(name=manifest["name"], table=table)


def render(manifest=None):
    """Return {relative path: file text} for every generated file."""
    if manifest is None:
        manifest = json.loads((ROOT / "manifest.json").read_text())
    name, version, description = manifest["name"], manifest["version"], manifest["description"]
    common = {
        "name": name,
        "version": version,
        "description": description,
        "author": AUTHOR,
        "homepage": REPOSITORY,
        "repository": REPOSITORY,
        "license": "MIT",
        "keywords": KEYWORDS,
    }
    with_skills = dict(common, skills="./skills")
    return {
        ".claude-plugin/plugin.json": dump(common),
        ".claude-plugin/marketplace.json": dump({
            "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
            "name": name,
            "owner": AUTHOR,
            "metadata": {"description": description, "version": version},
            "plugins": [{
                "name": name,
                "description": description,
                "version": version,
                "source": "./",
                "category": "productivity",
            }],
        }),
        "plugin.json": dump(common),
        "gemini-extension.json": dump({
            "name": name,
            "version": version,
            "description": description,
            "contextFileName": "AGENTS.md",
        }),
        ".codex-plugin/plugin.json": dump(with_skills),
        ".cursor-plugin/plugin.json": dump(with_skills),
        ".agents/plugins/marketplace.json": dump({
            "name": name,
            "interface": {"displayName": "Termux Elite"},
            "plugins": [{
                "name": name,
                "version": version,
                "description": description,
                "source": {"source": "local", "path": "./"},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": "Developer Tools",
            }],
        }),
        "AGENTS.md": agents_md(manifest),
    }


def main(argv):
    generated = render()
    stale = [p for p, text in generated.items()
             if not (ROOT / p).exists() or (ROOT / p).read_text() != text]
    if "--check" in argv:
        for path in stale:
            print("stale: " + path)
        return 1 if stale else 0
    for path, text in generated.items():
        target = ROOT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
    print("wrote %d files" % len(generated))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
