# Gemini CLI

## Install

As skills (Gemini CLI asks for confirmation; `--consent` skips the prompt):

```sh
gemini skills install https://github.com/Alex72-py/termux-elite.git --path skills
```

As an extension (bundles `skills/` and loads `AGENTS.md` as context through `gemini-extension.json`):

```sh
gemini extensions install https://github.com/Alex72-py/termux-elite
```

From a clone:

```sh
sh scripts/install.sh gemini              # ~/.gemini/skills
sh scripts/install.sh gemini --project    # ./.gemini/skills
```

## How it works

Gemini CLI injects the name and description of every enabled skill into the system prompt and calls its `activate_skill` tool when a task matches. Discovery covers workspace and user locations: `.gemini/skills/` and the interoperable `.agents/skills/` alias. Within one tier the `.agents/skills/` copy wins on a name clash.

## Notes

- `gemini skills list` and `/skills list` show what was discovered; `/skills disable` and `/skills enable` manage individual skills.
- With the extension, `AGENTS.md` is the short routing index, so keep it generated rather than hand-edited.
