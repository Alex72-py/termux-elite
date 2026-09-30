# Claude Code adapter

Expose `skills/*/SKILL.md` as project or user instructions that are searchable by task trigger. Keep the skill files outside the application source when possible and point the agent at the repository root.

Recommended workflow:

1. Make the repository available in the workspace.
2. Read `manifest.json` to build the skill index.
3. Select a skill when its trigger and required capabilities match the request.
4. Read the selected `SKILL.md` before proposing commands.
5. Treat `risk_level` as a planning signal; the host agent still owns confirmation and execution.

Do not copy the whole repository into every prompt. Load the manifest first and retrieve only the selected skill and any referenced material.
