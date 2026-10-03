## What and why

## Checklist

- [ ] `python scripts/sync_hosts.py` run if `manifest.json` or a skill changed (generated files are not edited by hand)
- [ ] `python -m pytest -q` passes
- [ ] New or changed skill meets the quality bar in CONTRIBUTING.md: symptom-rich description with a "Do NOT use" clause, read-only check first, explicit safety, verification, handoffs, report
- [ ] Helper scripts are read-only, executable, and pass `shellcheck -S warning`
- [ ] No secrets, tokens, or private keys in code, output, or examples
- [ ] Android or Termux version-specific claims are marked as such
