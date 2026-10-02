# Other agents

A host needs filesystem access and a way to read `manifest.json` or `AGENTS.md`. Skill-aware hosts can use the installer; everything else can route from the generated index.

| Host | Install |
| --- | --- |
| Codex | `codex plugin marketplace add https://github.com/Alex72-py/termux-elite`, then `codex plugin add termux-elite@termux-elite` (uses `.codex-plugin/plugin.json` and `.agents/plugins/marketplace.json`) |
| Cursor | `/add-plugin Alex72-py/termux-elite` (uses `.cursor-plugin/plugin.json`) |
| Kiro | `sh scripts/install.sh kiro` (`~/.kiro/skills`, or `--project` for `.kiro/skills`) |
| Any host that reads `.agents/skills` | `sh scripts/install.sh agents` |
| Anything that reads `AGENTS.md` | Point it at this repository; `AGENTS.md` carries the routing index and rules |

The Codex, Cursor, and marketplace manifests use the same shape as Google's published `gemini-skills` repository. They are generated and checked by tests, but this repository has not run them end to end on every host.

## Using the manifest directly

```python
import json, pathlib

root = pathlib.Path("termux-elite")
manifest = json.loads((root / "manifest.json").read_text())
request = "pip install cryptography failed with a build error"
hits = [s for s in manifest["skills"] if any(t in request.lower() for t in s["triggers"])]
print([s["path"] for s in hits])
```

Read the selected `SKILL.md` before proposing commands, run its `scripts/` helper for facts, then follow the decision tree. Map `required_capabilities` to the tools your host actually has, and refuse a skill when a capability is missing. The host owns confirmation, cancellation, and output redaction.
