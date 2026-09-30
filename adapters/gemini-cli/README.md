# Gemini CLI adapter

Use `manifest.json` as a lightweight skill catalog and load the matching `SKILL.md` as task context. A wrapper can map `required_capabilities` to the host’s available tools and refuse selection when a required capability is missing.

The skill owns diagnosis and verification guidance. Gemini CLI or another host owns tool invocation, confirmation, cancellation, and output redaction.
