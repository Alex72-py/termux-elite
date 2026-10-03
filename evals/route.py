"""Lexical routing proxy: which skill's triggers and description best match a request.

This is a cheap regression guard that catches skills whose wording makes them unreachable.
It is NOT a model of how an agent host chooses skills (hosts match semantically).
Usage: python evals/route.py "pip install fails with failed building wheel"
"""
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[1]


def tokens(text):
    return re.findall(r"[a-z0-9_]+", text.lower())


def build(manifest):
    weights = {}
    for skill in manifest["skills"]:
        counts = Counter()
        for trigger in skill["triggers"]:
            for word in tokens(trigger):
                counts[word] += 3
        for word in tokens(skill["description"]):
            counts[word] += 1
        weights[skill["name"]] = counts
    doc_freq = Counter()
    for counts in weights.values():
        for word in counts:
            doc_freq[word] += 1
    return weights, doc_freq, len(weights)


def rank(text, manifest=None):
    if manifest is None:
        manifest = json.loads((ROOT / "manifest.json").read_text())
    weights, doc_freq, total = build(manifest)
    words = set(tokens(text))
    scores = {}
    for name, counts in weights.items():
        scores[name] = sum(
            math.log(1 + total / doc_freq[w]) * math.log(1 + counts[w]) for w in words if w in counts
        )
    return sorted(scores.items(), key=lambda item: (-item[1], item[0]))


def main(argv):
    if len(argv) < 2:
        print("usage: python evals/route.py <request text>", file=sys.stderr)
        return 2
    for name, score in rank(" ".join(argv[1:]))[:3]:
        print("%-26s %.2f" % (name, score))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
