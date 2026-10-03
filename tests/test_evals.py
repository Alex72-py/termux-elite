import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "evals"))
import route  # noqa: E402

MANIFEST = json.loads((ROOT / "manifest.json").read_text())
NAMES = [s["name"] for s in MANIFEST["skills"]]
SETS = json.loads((ROOT / "evals" / "scenarios.json").read_text())["sets"]

# Regression floors: the correct count measured when this guard was added, minus
# one so a single borderline phrasing does not break unrelated changes.
MIN_CORRECT = {'direct': 27, 'paraphrased': 10, 'heldout': 7}


def correct(name):
    return sum(route.rank(item["says"], MANIFEST)[0][0] == item["skill"] for item in SETS[name])


def test_scenarios_reference_real_skills_and_are_unique():
    seen = set()
    for name, items in SETS.items():
        for item in items:
            assert item["skill"] in NAMES, (name, item["skill"])
            assert item["says"] not in seen, item["says"]
            seen.add(item["says"])


@pytest.mark.parametrize("skill", NAMES)
def test_every_skill_has_scenarios_in_every_set(skill):
    for name, items in SETS.items():
        assert any(i["skill"] == skill for i in items), "%s has no %s scenario" % (skill, name)


@pytest.mark.parametrize("name", sorted(MIN_CORRECT))
def test_routing_does_not_regress(name):
    assert correct(name) >= MIN_CORRECT[name], "routing regressed on the %s set" % name


def test_route_cli_ranks_a_symptom():
    r = subprocess.run([sys.executable, str(ROOT / "evals" / "route.py"),
                        "gyp ERR! Undefined variable android_ndk_path"],
                       capture_output=True, text=True)
    assert r.returncode == 0
    assert r.stdout.split()[0] == "node-native-build"


def test_route_cli_needs_an_argument():
    r = subprocess.run([sys.executable, str(ROOT / "evals" / "route.py")], capture_output=True, text=True)
    assert r.returncode == 2
