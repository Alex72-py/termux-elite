---
name: example-skill
description: One or two sentences on the operational decision this skill makes and the symptoms it covers. Use when concrete symptoms, error strings, or phrases a user would say. Do NOT use for neighbouring cases (see other-skill) or for work that needs no skill.
triggers: phrase one,phrase two,error string
risk: low
---
# Example Skill

## Purpose
The failure or decision this skill separates, in one or two sentences.

## When to use
- Concrete symptoms, error strings, requests.

## When NOT to use
- Cases that belong to another skill, or need no skill.

## Preconditions
What to capture before acting. Read-only only. Name the helper script if there is one, for example `sh scripts/check-example.sh`.

## Decision tree
1. First distinguishing check (cheapest, read-only).
2. Next branch. First match wins.
3. Mark Android-version-specific or unverified claims as such.

## Failure signatures
Optional table: signature, layer, next step.

## Safety
Which steps mutate the environment and need confirmation. What must never be printed.

## Verification
How to confirm the original problem is resolved, with a command.

## Rollback
Required for medium and high risk. How to undo exactly what this attempt changed.

## Handoffs
- `other-skill` when the condition that moves the work there.

## Report
The shortest useful summary the agent gives the user: root cause, change, verification, remaining limit.
