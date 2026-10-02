# Antigravity CLI (agy)

## Install

```sh
agy plugin install https://github.com/Alex72-py/termux-elite.git
agy plugin list
```

Or from a clone:

```sh
sh scripts/install.sh agy                 # ~/.gemini/config/skills
sh scripts/install.sh agy --project       # ./.agents/skills
```

## How it works

`agy` reads the root `plugin.json` and discovers `SKILL.md` files under the installed plugin's `skills/`. For project skills it defaults to `.agents/skills/` and still honors the older `.agent/skills/`.

## Notes

- Other skill repositories report that agy scans `~/.gemini/config/skills`, `~/.gemini/skills`, and `~/.gemini/antigravity-cli/skills` globally, but not `~/.agents/skills`. That is why the `agy` host in `install.sh` targets `~/.gemini/config/skills`. This repository did not verify the behavior on a device; if your agy release differs, `scripts/install.sh agents` or a plugin install are the alternatives.
- Restart agy after installing; skills are read at startup.
- `agy plugin uninstall termux-elite` removes the plugin.
