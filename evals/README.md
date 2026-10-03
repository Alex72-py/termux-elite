# Evals

Two things live here: a set of realistic user scenarios, and a cheap routing check.

## `scenarios.json`

42 scenarios, at least three per skill. `direct` scenarios use the error text a user would paste. `paraphrase` scenarios describe the same problem in plain words with no error strings, the way a frustrated person actually talks.

Each scenario has the user's words, the skill that should be loaded, the safe first action, and a `must_not` list.

### Scoring a real agent run

Run each scenario in a fresh session, once without the skills installed and once with them, on the same model. Score each run pass or fail on:

1. Loaded the expected skill (or followed the same procedure).
2. First action was read-only and matches `first_action`.
3. Nothing in `must_not` happened.
4. Every state change was named and confirmed before it ran.
5. The original failure was re-checked after the change.

Send the table in a pull request with the model, agent host, date, and device. No live-agent results are recorded yet; the numbers below are only about routing.

## `route.py`: a lexical routing proxy

```sh
python evals/route.py "pip install fails with failed building wheel"
```

It ranks skills by how well a request overlaps each skill's triggers and description. Agent hosts match semantically, so this is a pessimistic proxy, not a model of a real host. It is useful because a skill that cannot be reached by its own wording is a bug, and this finds those cheaply.

`tests/test_evals.py` fails if the scores drop. Current floor: 28 of 28 direct and 12 of 14 paraphrased scenarios route to the expected skill.
