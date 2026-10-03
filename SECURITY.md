# Security policy

## Reporting

Please report security problems privately through GitHub: open the **Security** tab of this repository and choose **Report a vulnerability**. Do not post exploit details in a public issue.

## In scope

- A helper script that prints a secret, token, key, or broad environment dump.
- A helper script that changes state when it should only read.
- Skill guidance that would expose a service beyond a trusted network or weaken device security without clear confirmation.
- Anything in the installer that overwrites or deletes files it did not install.

## Out of scope

Failures in Termux, Android, or a host agent themselves; report those upstream.

## Supported versions

The latest release. Fixes land on `main` and are noted in the changelog. Reports are handled on a best-effort basis.
