# Generic agent adapter

A host agent only needs filesystem access and a way to run its own tools:

1. Parse `manifest.json`.
2. Match request text against `triggers` and descriptions.
3. Check `required_capabilities` and `platform`.
4. Read the chosen `SKILL.md`.
5. Execute only through the host’s explicit tool and confirmation policy.
6. Use the skill’s verification and rollback sections when reporting completion.

The skill pack does not assume a particular model, prompt format, tool protocol, or agent runtime.
