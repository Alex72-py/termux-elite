#!/usr/bin/env python3
"""Rank skills for a symptom description, using manifest.json triggers and descriptions.

This is a lexical proxy for how a host might match a request to a skill. It is
deterministic and dependency-free, so it works as a regression guard for the
wording of descriptions and triggers. It does not measure agent behaviour.

Usage: python evals/route.py "pip install fails with failed building wheel"
"""
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def tokens(text):
    return re.findall(r"[a-z0-9_]+", text.lower())


def rank(text, manifest=None):
    if manifest is None:
        manifest = json.loads((ROOT / "manifest.json").read_text())
    weights = {}
    for skill in manifest["skills"]:
        counts = Counter()
        for trigger in skill["triggers"]:
            for word in tokens(trigger):
                counts[word] += 3
        for word in tokens(skill["description"]):
            counts[word] += 1
        weights[skill["name"]] = counts
    total = len(weights)
    df = Counter(word for counts in weights.values() for word in counts)
    words = set(tokens(text))
    scores = {
        name: sum(math.log(1 + total / df[w]) * math.log(1 + c[w]) for w in words if w in c)
        for name, c in weights.items()
    }
    return sorted(scores.items(), key=lambda item: (-item[1], item[0]))


def main(argv):
    if not argv:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 2
    for name, score in rank(" ".join(argv))[:3]:
        print("%-24s %.2f" % (name, score))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
